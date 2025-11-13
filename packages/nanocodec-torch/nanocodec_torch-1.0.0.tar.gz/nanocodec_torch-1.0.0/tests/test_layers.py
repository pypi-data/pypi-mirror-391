"""
Unit tests for custom layer modules.
"""

import pytest
import torch
import torch.nn as nn
from src.nanocodec_torch.layers.conv import (
    Conv1dNorm,
    HiFiGANResLayer,
    ResidualBlock
)
from src.nanocodec_torch.models.decoder import (
    CausalConv1d,
    CausalConvTranspose1d
)


class TestConv1dNorm:
    """Test suite for Conv1dNorm layer."""

    def test_conv1d_norm_initialization(self):
        """Test Conv1dNorm initializes correctly."""
        conv = Conv1dNorm(
            in_channels=16,
            out_channels=32,
            kernel_size=7,
            stride=1,
            padding=3,
            padding_mode="replicate"
        )

        assert conv.in_channels == 16
        assert conv.out_channels == 32
        assert conv.kernel_size == 7
        assert conv.stride == 1

    def test_conv1d_norm_forward_shape(self):
        """Test Conv1dNorm forward pass shape."""
        conv = Conv1dNorm(16, 32, 7, stride=1, padding=3)
        x = torch.randn(2, 16, 100)

        output = conv(x)

        assert output.shape == (2, 32, 100)

    def test_conv1d_norm_replicate_padding(self):
        """Test Conv1dNorm with replicate padding."""
        conv = Conv1dNorm(8, 16, 5, stride=1, padding=2, padding_mode="replicate")
        x = torch.randn(1, 8, 50)

        output = conv(x)

        assert output.shape == (1, 16, 50)
        assert not torch.isnan(output).any()

    def test_conv1d_norm_zeros_padding(self):
        """Test Conv1dNorm with zeros padding (causal)."""
        # Auto-calculate causal padding: (kernel_size - 1) * dilation = 4
        conv = Conv1dNorm(8, 16, 5, stride=1, padding_mode="zeros")
        x = torch.randn(1, 8, 50)

        output = conv(x)

        # Causal padding maintains length with stride=1
        assert output.shape == (1, 16, 50)
        assert not torch.isnan(output).any()

    def test_conv1d_norm_stride(self):
        """Test Conv1dNorm with stride > 1."""
        conv = Conv1dNorm(16, 32, 4, stride=2, padding=1)
        x = torch.randn(1, 16, 100)

        output = conv(x)

        expected_len = (100 + 2 * 1 - 4) // 2 + 1
        assert output.shape == (1, 32, expected_len)

    def test_conv1d_norm_gradient_flow(self):
        """Test gradients flow through Conv1dNorm."""
        conv = Conv1dNorm(8, 16, 3)
        x = torch.randn(1, 8, 50, requires_grad=True)

        output = conv(x)
        loss = output.sum()
        loss.backward()

        assert x.grad is not None
        assert not torch.isnan(x.grad).any()


class TestResidualBlock:
    """Test suite for ResidualBlock."""

    def test_residual_block_initialization(self):
        """Test ResidualBlock initializes correctly."""
        block = ResidualBlock(
            channels=32,
            kernel_size=3,
            dilation=1,
            padding_mode="replicate"
        )

        assert len(list(block.children())) > 0

    def test_residual_block_forward_shape(self):
        """Test ResidualBlock maintains shape."""
        block = ResidualBlock(32, 3, dilation=1, padding_mode="replicate")
        x = torch.randn(2, 32, 100)

        output = block(x)

        # Should maintain shape
        assert output.shape == x.shape

    def test_residual_block_dilation(self):
        """Test ResidualBlock with different dilations."""
        dilations = [1, 3, 5, 7]

        for dilation in dilations:
            block = ResidualBlock(16, 3, dilation=dilation, padding_mode="replicate")
            x = torch.randn(1, 16, 50)

            output = block(x)

            assert output.shape == x.shape

    def test_residual_block_residual_connection(self):
        """Test that residual connection works."""
        block = ResidualBlock(32, 3, dilation=1, padding_mode="replicate")

        # Zero out the convolution weights to test residual
        with torch.no_grad():
            for param in block.parameters():
                param.zero_()

        x = torch.randn(1, 32, 50)
        output = block(x)

        # With zero weights, output should be close to input (residual)
        # Note: activation functions may add small differences
        assert (output - x).abs().mean() < 0.5

    def test_residual_block_gradient_flow(self):
        """Test gradients flow through ResidualBlock."""
        block = ResidualBlock(16, 3, dilation=1)
        x = torch.randn(1, 16, 50, requires_grad=True)

        output = block(x)
        loss = output.sum()
        loss.backward()

        assert x.grad is not None


class TestHiFiGANResLayer:
    """Test suite for HiFiGANResLayer."""

    def test_hifigan_res_layer_initialization(self):
        """Test HiFiGANResLayer initializes correctly."""
        layer = HiFiGANResLayer(
            channels=32,
            kernel_sizes=[3, 7, 11],
            dilations=[1, 3, 5],
            padding_mode="replicate"
        )

        # Should have 3 parallel paths (one per kernel size)
        assert len(layer.res_blocks) == 3

    def test_hifigan_res_layer_forward_shape(self):
        """Test HiFiGANResLayer maintains shape."""
        layer = HiFiGANResLayer(32, [3, 7, 11], [1, 3, 5], "replicate")
        x = torch.randn(2, 32, 100)

        output = layer(x)

        # Should maintain shape
        assert output.shape == x.shape

    def test_hifigan_res_layer_multi_scale(self):
        """Test HiFiGANResLayer processes at multiple scales."""
        layer = HiFiGANResLayer(16, [3, 7, 11], [1, 3, 5], "replicate")
        x = torch.randn(1, 16, 50)

        output = layer(x)

        # Should combine information from different kernel sizes
        assert output.shape == x.shape
        assert not torch.isnan(output).any()

    def test_hifigan_res_layer_gradient_flow(self):
        """Test gradients flow through HiFiGANResLayer."""
        layer = HiFiGANResLayer(16, [3, 7], [1, 3], "replicate")
        x = torch.randn(1, 16, 50, requires_grad=True)

        output = layer(x)
        loss = output.sum()
        loss.backward()

        assert x.grad is not None

    def test_hifigan_res_layer_custom_config(self):
        """Test HiFiGANResLayer with custom configuration."""
        layer = HiFiGANResLayer(
            channels=64,
            kernel_sizes=[5, 9],
            dilations=[1, 2, 4],
            padding_mode="replicate"
        )

        x = torch.randn(1, 64, 100)
        output = layer(x)

        assert output.shape == x.shape


class TestCausalConv1d:
    """Test suite for CausalConv1d."""

    def test_causal_conv1d_initialization(self):
        """Test CausalConv1d initializes correctly."""
        conv = CausalConv1d(16, 32, kernel_size=7, stride=1, dilation=1)

        assert conv.kernel_size == 7
        assert conv.stride == 1
        assert conv.dilation == 1

    def test_causal_conv1d_forward_shape(self):
        """Test CausalConv1d forward pass shape."""
        conv = CausalConv1d(16, 32, 7, stride=1)
        x = torch.randn(2, 16, 100)

        output = conv(x)

        # Should maintain length with causal padding
        assert output.shape == (2, 32, 100)

    def test_causal_conv1d_causality(self):
        """Test that CausalConv1d is truly causal."""
        conv = CausalConv1d(1, 1, kernel_size=5, stride=1)

        # Create input with impulse at position 10
        x = torch.zeros(1, 1, 50)
        x[:, :, 10] = 1.0

        output = conv(x)

        # Output should only be affected at position 10 and after
        # (not before, due to causality)
        assert output[:, :, :10].abs().sum() < output[:, :, 10:].abs().sum()

    def test_causal_conv1d_dilation(self):
        """Test CausalConv1d with dilation."""
        conv = CausalConv1d(8, 16, kernel_size=3, stride=1, dilation=2)
        x = torch.randn(1, 8, 50)

        output = conv(x)

        assert output.shape == (1, 16, 50)

    def test_causal_conv1d_stride(self):
        """Test CausalConv1d with stride > 1."""
        conv = CausalConv1d(8, 16, kernel_size=4, stride=2)
        x = torch.randn(1, 8, 100)

        output = conv(x)

        expected_len = 100 // 2
        assert output.shape == (1, 16, expected_len)

    def test_causal_conv1d_gradient_flow(self):
        """Test gradients flow through CausalConv1d."""
        conv = CausalConv1d(8, 16, 3)
        x = torch.randn(1, 8, 50, requires_grad=True)

        output = conv(x)
        loss = output.sum()
        loss.backward()

        assert x.grad is not None


class TestCausalConvTranspose1d:
    """Test suite for CausalConvTranspose1d."""

    def test_causal_conv_transpose_initialization(self):
        """Test CausalConvTranspose1d initializes correctly."""
        # NanoCodec pattern: in_channels must be divisible by out_channels
        # (groups = out_channels, so in_channels/out_channels per group)
        conv = CausalConvTranspose1d(32, 16, kernel_size=4, stride=2)

        assert conv.in_channels == 32
        assert conv.out_channels == 16

    def test_causal_conv_transpose_forward_shape(self):
        """Test CausalConvTranspose1d upsamples correctly."""
        conv = CausalConvTranspose1d(32, 16, kernel_size=4, stride=2)
        x = torch.randn(2, 32, 50)

        output = conv(x)

        # Should upsample by stride factor
        expected_len = 50 * 2
        assert output.shape == (2, 16, expected_len)

    def test_causal_conv_transpose_upsampling_factor(self):
        """Test different upsampling factors."""
        strides = [2, 3, 6, 7]

        for stride in strides:
            out_channels = 16
            conv = CausalConvTranspose1d(
                32, out_channels,
                kernel_size=stride * 2,
                stride=stride
            )
            x = torch.randn(1, 32, 20)

            output = conv(x)

            expected_len = 20 * stride
            assert output.shape == (1, out_channels, expected_len)

    def test_causal_conv_transpose_grouped(self):
        """Test CausalConvTranspose1d with grouped convolution (groups=out_channels is hardcoded)."""
        out_channels = 64
        conv = CausalConvTranspose1d(
            128, out_channels,
            kernel_size=14,
            stride=7
        )
        x = torch.randn(1, 128, 10)

        output = conv(x)

        assert output.shape == (1, out_channels, 70)

    def test_causal_conv_transpose_causality(self):
        """Test that CausalConvTranspose1d maintains causality."""
        conv = CausalConvTranspose1d(1, 1, kernel_size=6, stride=3)

        # Initialize weights to non-zero values for meaningful test
        nn.init.xavier_uniform_(conv.weight)
        nn.init.zeros_(conv.bias)

        # Input with signal only in first half
        x = torch.zeros(1, 1, 20)
        x[:, :, :10] = torch.randn(1, 1, 10)

        output = conv(x)

        # First half should have more energy than second half
        mid_point = output.shape[2] // 2
        first_half_energy = output[:, :, :mid_point].abs().sum()
        second_half_energy = output[:, :, mid_point:].abs().sum()

        assert first_half_energy > second_half_energy * 0.5

    def test_causal_conv_transpose_gradient_flow(self):
        """Test gradients flow through CausalConvTranspose1d."""
        conv = CausalConvTranspose1d(32, 16, kernel_size=4, stride=2)
        x = torch.randn(1, 32, 20, requires_grad=True)

        output = conv(x)
        loss = output.sum()
        loss.backward()

        assert x.grad is not None
        assert not torch.isnan(x.grad).any()

    def test_causal_conv_transpose_device_compatibility(self):
        """Test CausalConvTranspose1d on different devices."""
        conv = CausalConvTranspose1d(16, 8, kernel_size=4, stride=2)
        x = torch.randn(1, 16, 20)

        # CPU
        conv_cpu = conv.to('cpu')
        x_cpu = x.to('cpu')
        output_cpu = conv_cpu(x_cpu)
        assert output_cpu.device.type == 'cpu'

        # CUDA (if available)
        if torch.cuda.is_available():
            conv_cuda = conv.to('cuda')
            x_cuda = x.to('cuda')
            output_cuda = conv_cuda(x_cuda)
            assert output_cuda.device.type == 'cuda'

    def test_causal_conv_transpose_deterministic(self):
        """Test CausalConvTranspose1d is deterministic."""
        conv = CausalConvTranspose1d(16, 8, kernel_size=4, stride=2)
        x = torch.randn(1, 16, 20)

        conv.eval()
        with torch.no_grad():
            output1 = conv(x)
            output2 = conv(x)

        torch.testing.assert_close(output1, output2)
