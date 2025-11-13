"""
Unit tests for custom activation functions.
"""

import pytest
import torch
import torch.nn as nn
from src.nanocodec_torch.layers.activations import (
    CodecActivation,
    SnakeActivation,
    HalfSnakeActivation
)


class TestCodecActivation:
    """Test suite for CodecActivation (LeakyReLU)."""

    def test_codec_activation_initialization(self):
        """Test CodecActivation initializes correctly."""
        act = CodecActivation(negative_slope=0.01)
        assert isinstance(act, nn.Module)

    def test_codec_activation_forward_shape(self):
        """Test CodecActivation maintains shape."""
        act = CodecActivation()
        x = torch.randn(2, 32, 100)

        output = act(x)

        assert output.shape == x.shape

    def test_codec_activation_positive_values(self):
        """Test CodecActivation on positive values."""
        act = CodecActivation(negative_slope=0.01)
        x = torch.randn(10, 50).abs()  # All positive

        output = act(x)

        # Positive values should pass through unchanged
        torch.testing.assert_close(output, x)

    def test_codec_activation_negative_values(self):
        """Test CodecActivation on negative values."""
        act = CodecActivation(negative_slope=0.01)
        x = -torch.randn(10, 50).abs()  # All negative

        output = act(x)

        # Negative values should be scaled by negative_slope
        expected = x * 0.01
        torch.testing.assert_close(output, expected, rtol=1e-5, atol=1e-6)

    def test_codec_activation_mixed_values(self):
        """Test CodecActivation on mixed positive/negative values."""
        act = CodecActivation(negative_slope=0.01)
        x = torch.randn(100, 100)

        output = act(x)

        # Positive should be unchanged
        positive_mask = x > 0
        torch.testing.assert_close(output[positive_mask], x[positive_mask])

        # Negative should be scaled
        negative_mask = x < 0
        expected_negative = x[negative_mask] * 0.01
        torch.testing.assert_close(output[negative_mask], expected_negative, rtol=1e-5, atol=1e-6)

    def test_codec_activation_zero(self):
        """Test CodecActivation on zero."""
        act = CodecActivation()
        x = torch.zeros(10, 10)

        output = act(x)

        assert (output == 0).all()

    def test_codec_activation_gradient_flow(self):
        """Test gradients flow through CodecActivation."""
        act = CodecActivation()
        x = torch.randn(10, 10, requires_grad=True)

        output = act(x)
        loss = output.sum()
        loss.backward()

        assert x.grad is not None

    def test_codec_activation_device_compatibility(self):
        """Test CodecActivation works on different devices."""
        act = CodecActivation()
        x = torch.randn(10, 10)

        # CPU
        act_cpu = act.to('cpu')
        x_cpu = x.to('cpu')
        output_cpu = act_cpu(x_cpu)
        assert output_cpu.device.type == 'cpu'

        # CUDA (if available)
        if torch.cuda.is_available():
            act_cuda = act.to('cuda')
            x_cuda = x.to('cuda')
            output_cuda = act_cuda(x_cuda)
            assert output_cuda.device.type == 'cuda'


class TestSnakeActivation:
    """Test suite for SnakeActivation."""

    def test_snake_activation_initialization(self):
        """Test SnakeActivation initializes correctly."""
        act = SnakeActivation(channels=32)
        assert isinstance(act, nn.Module)
        assert act.alpha.shape == (1, 32, 1)

    def test_snake_activation_forward_shape(self):
        """Test SnakeActivation maintains shape."""
        act = SnakeActivation(channels=32)
        x = torch.randn(2, 32, 100)

        output = act(x)

        assert output.shape == x.shape

    def test_snake_activation_learnable_alpha(self):
        """Test that alpha is learnable parameter."""
        act = SnakeActivation(channels=16)

        # Alpha should be a parameter
        assert hasattr(act, 'alpha')
        assert isinstance(act.alpha, nn.Parameter)
        assert act.alpha.requires_grad

    def test_snake_activation_different_channels(self):
        """Test SnakeActivation with different channel sizes."""
        channel_sizes = [8, 16, 32, 64, 128]

        for channels in channel_sizes:
            act = SnakeActivation(channels=channels)
            x = torch.randn(2, channels, 50)

            output = act(x)

            assert output.shape == x.shape

    def test_snake_activation_non_zero_output(self):
        """Test SnakeActivation produces non-trivial output."""
        act = SnakeActivation(channels=16)
        x = torch.randn(1, 16, 50)

        output = act(x)

        # Output should be different from input (due to snake transformation)
        assert not torch.allclose(output, x, rtol=0.1)

    def test_snake_activation_zero_input(self):
        """Test SnakeActivation on zero input."""
        act = SnakeActivation(channels=16)
        x = torch.zeros(1, 16, 50)

        output = act(x)

        # Snake(0) should be close to 0 (x + 1/alpha * sin^2(alpha*x) = 0 + 0)
        assert output.abs().max() < 0.1

    def test_snake_activation_gradient_flow(self):
        """Test gradients flow through SnakeActivation."""
        act = SnakeActivation(channels=16)
        x = torch.randn(1, 16, 50, requires_grad=True)

        output = act(x)
        loss = output.sum()
        loss.backward()

        assert x.grad is not None
        assert act.alpha.grad is not None

    def test_snake_activation_device_compatibility(self):
        """Test SnakeActivation works on different devices."""
        act = SnakeActivation(channels=16)
        x = torch.randn(1, 16, 50)

        # CPU
        act_cpu = act.to('cpu')
        x_cpu = x.to('cpu')
        output_cpu = act_cpu(x_cpu)
        assert output_cpu.device.type == 'cpu'

        # CUDA (if available)
        if torch.cuda.is_available():
            act_cuda = act.to('cuda')
            x_cuda = x.to('cuda')
            output_cuda = act_cuda(x_cuda)
            assert output_cuda.device.type == 'cuda'

    def test_snake_activation_deterministic(self):
        """Test SnakeActivation is deterministic."""
        act = SnakeActivation(channels=16)
        x = torch.randn(1, 16, 50)

        act.eval()
        with torch.no_grad():
            output1 = act(x)
            output2 = act(x)

        torch.testing.assert_close(output1, output2)


class TestHalfSnakeActivation:
    """Test suite for HalfSnakeActivation."""

    def test_half_snake_activation_initialization(self):
        """Test HalfSnakeActivation initializes correctly."""
        act = HalfSnakeActivation(channels=32)
        assert isinstance(act, nn.Module)
        assert act.alpha.shape == (1, 16, 1)  # Half of 32

    def test_half_snake_activation_forward_shape(self):
        """Test HalfSnakeActivation maintains shape."""
        act = HalfSnakeActivation(channels=32)
        x = torch.randn(2, 32, 100)

        output = act(x)

        assert output.shape == x.shape

    def test_half_snake_activation_even_channels(self):
        """Test HalfSnakeActivation requires even channels."""
        # Should work with even channels
        act = HalfSnakeActivation(channels=32)
        x = torch.randn(1, 32, 50)
        output = act(x)
        assert output.shape == x.shape

        # Odd channels should still work (will round down)
        act_odd = HalfSnakeActivation(channels=33)
        x_odd = torch.randn(1, 33, 50)
        output_odd = act_odd(x_odd)
        assert output_odd.shape == x_odd.shape

    def test_half_snake_activation_hybrid_behavior(self):
        """Test that HalfSnakeActivation uses Snake + LeakyReLU."""
        act = HalfSnakeActivation(channels=32)
        x = torch.randn(2, 32, 100)

        output = act(x)

        # Output should be different from pure Snake or pure LeakyReLU
        assert output.shape == x.shape
        assert not torch.allclose(output, x)

    def test_half_snake_activation_different_channels(self):
        """Test HalfSnakeActivation with different channel sizes."""
        channel_sizes = [16, 32, 64, 128, 256]

        for channels in channel_sizes:
            act = HalfSnakeActivation(channels=channels)
            x = torch.randn(2, channels, 50)

            output = act(x)

            assert output.shape == x.shape

    def test_half_snake_activation_learnable_alpha(self):
        """Test that alpha is learnable parameter."""
        act = HalfSnakeActivation(channels=32)

        # Alpha should be a parameter (for first half - Snake)
        assert hasattr(act, 'alpha')
        assert isinstance(act.alpha, nn.Parameter)
        assert act.alpha.requires_grad

    def test_half_snake_activation_gradient_flow(self):
        """Test gradients flow through HalfSnakeActivation."""
        act = HalfSnakeActivation(channels=32)
        x = torch.randn(1, 32, 50, requires_grad=True)

        output = act(x)
        loss = output.sum()
        loss.backward()

        assert x.grad is not None
        assert act.alpha.grad is not None

    def test_half_snake_activation_split_processing(self):
        """Test that channels are split and processed differently."""
        act = HalfSnakeActivation(channels=32)

        # Create input where first half is positive, second half is negative
        x = torch.randn(1, 32, 50)
        x[:, :16, :] = x[:, :16, :].abs()   # First half positive
        x[:, 16:, :] = -x[:, 16:, :].abs()  # Second half negative

        output = act(x)

        # Both halves should have valid outputs
        assert not torch.isnan(output[:, :16, :]).any()
        assert not torch.isnan(output[:, 16:, :]).any()

    def test_half_snake_activation_zero_input(self):
        """Test HalfSnakeActivation on zero input."""
        act = HalfSnakeActivation(channels=32)
        x = torch.zeros(1, 32, 50)

        output = act(x)

        # Output should be close to zero
        assert output.abs().max() < 0.1

    def test_half_snake_activation_device_compatibility(self):
        """Test HalfSnakeActivation works on different devices."""
        act = HalfSnakeActivation(channels=32)
        x = torch.randn(1, 32, 50)

        # CPU
        act_cpu = act.to('cpu')
        x_cpu = x.to('cpu')
        output_cpu = act_cpu(x_cpu)
        assert output_cpu.device.type == 'cpu'

        # CUDA (if available)
        if torch.cuda.is_available():
            act_cuda = act.to('cuda')
            x_cuda = x.to('cuda')
            output_cuda = act_cuda(x_cuda)
            assert output_cuda.device.type == 'cuda'

        # MPS (if available)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            act_mps = act.to('mps')
            x_mps = x.to('mps')
            output_mps = act_mps(x_mps)
            assert output_mps.device.type == 'mps'

    def test_half_snake_activation_deterministic(self):
        """Test HalfSnakeActivation is deterministic."""
        act = HalfSnakeActivation(channels=32)
        x = torch.randn(1, 32, 50)

        act.eval()
        with torch.no_grad():
            output1 = act(x)
            output2 = act(x)

        torch.testing.assert_close(output1, output2)

    def test_half_snake_activation_output_range(self):
        """Test HalfSnakeActivation output is reasonable."""
        act = HalfSnakeActivation(channels=32)
        x = torch.randn(1, 32, 50) * 5  # Scaled input

        output = act(x)

        # Output should not be NaN or Inf
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()

        # Output should be in reasonable range
        assert output.abs().max() < 100

    def test_half_snake_activation_batch_processing(self):
        """Test HalfSnakeActivation with batched input."""
        act = HalfSnakeActivation(channels=64)
        batch_sizes = [1, 2, 4, 8]

        for batch_size in batch_sizes:
            x = torch.randn(batch_size, 64, 100)
            output = act(x)

            assert output.shape == (batch_size, 64, 100)

    def test_half_snake_activation_small_channels(self):
        """Test HalfSnakeActivation with small channel count."""
        act = HalfSnakeActivation(channels=4)
        x = torch.randn(1, 4, 50)

        output = act(x)

        assert output.shape == x.shape
        assert not torch.isnan(output).any()
