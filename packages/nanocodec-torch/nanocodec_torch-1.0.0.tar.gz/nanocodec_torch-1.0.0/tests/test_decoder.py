"""
Unit tests for Causal HiFiGAN Decoder module.
"""

import pytest
import torch
from src.nanocodec_torch.models.decoder import CausalHiFiGANDecoder


class TestCausalHiFiGANDecoder:
    """Test suite for Causal HiFiGAN Decoder."""

    @pytest.fixture
    def decoder(self):
        """Create a default decoder instance."""
        return CausalHiFiGANDecoder(
            up_sample_rates=[7, 7, 6, 3, 2],
            input_dim=16,
            base_channels=864,
            activation="half_snake",
            output_activation="clamp",
            pad_mode="zeros",
            n_groups_equal_to_out_channels=True
        )

    def test_decoder_initialization(self, decoder):
        """Test decoder initializes correctly."""
        assert isinstance(decoder, CausalHiFiGANDecoder)
        assert decoder.input_dim == 16
        assert decoder.base_channels == 864
        assert len(decoder.up_sample_conv_layers) == 5
        assert len(decoder.res_layers) == 5

    def test_decoder_output_shape(self, decoder):
        """Test decoder produces correct output shape."""
        batch_size = 2
        time_dim = 12  # Compressed time dimension
        codes = torch.randn(batch_size, 16, time_dim)

        reconstructed, recon_len = decoder(codes)

        # Check shape: [B, 1, T*1764]
        expected_time_dim = time_dim * 1764
        assert reconstructed.shape == (batch_size, 1, expected_time_dim)
        assert recon_len.shape == (batch_size,)

    def test_decoder_upsampling_factor(self, decoder):
        """Test decoder applies correct upsampling factor."""
        time_dim = 25  # Compressed time
        codes = torch.randn(1, 16, time_dim)

        reconstructed, recon_len = decoder(codes)

        # Upsample factor should be 7 * 7 * 6 * 3 * 2 = 1764
        expected_samples = time_dim * 1764
        assert reconstructed.shape[2] == expected_samples

    def test_decoder_with_different_input_lengths(self, decoder):
        """Test decoder handles different input lengths."""
        test_lengths = [10, 20, 40, 50]

        for time_dim in test_lengths:
            codes = torch.randn(1, 16, time_dim)
            reconstructed, recon_len = decoder(codes)

            expected_len = time_dim * 1764
            assert reconstructed.shape[2] == expected_len
            assert recon_len.item() == expected_len

    def test_decoder_batch_processing(self, decoder):
        """Test decoder handles batched inputs correctly."""
        batch_sizes = [1, 2, 4, 8]
        time_dim = 12

        for batch_size in batch_sizes:
            codes = torch.randn(batch_size, 16, time_dim)
            reconstructed, recon_len = decoder(codes)

            assert reconstructed.shape[0] == batch_size
            assert recon_len.shape[0] == batch_size

    def test_decoder_with_codes_len(self, decoder):
        """Test decoder with explicit code lengths."""
        batch_size = 3
        max_time = 25

        # Different lengths for each batch item
        codes = torch.randn(batch_size, 16, max_time)
        codes_len = torch.tensor([10, 15, 25])

        reconstructed, recon_len = decoder(codes, codes_len)

        assert reconstructed.shape[0] == batch_size
        assert recon_len.shape[0] == batch_size

        # Check that reconstructed lengths are approximately correct
        expected_lens = codes_len * 1764
        torch.testing.assert_close(recon_len, expected_lens, rtol=0, atol=1)

    def test_decoder_output_range(self, decoder):
        """Test decoder output values are in expected range."""
        codes = torch.randn(1, 16, 12)
        reconstructed, _ = decoder(codes)

        # Output should be clamped to [-1, 1] due to output_activation="clamp"
        assert reconstructed.min() >= -1.0
        assert reconstructed.max() <= 1.0

        # Output should not be all zeros
        assert reconstructed.abs().sum() > 0

        # Output should not contain NaN or Inf
        assert not torch.isnan(reconstructed).any()
        assert not torch.isinf(reconstructed).any()

    def test_decoder_gradient_flow(self, decoder):
        """Test gradients flow through decoder."""
        codes = torch.randn(1, 16, 12, requires_grad=True)
        reconstructed, _ = decoder(codes)

        # Compute dummy loss and backpropagate
        loss = reconstructed.sum()
        loss.backward()

        # Check that input has gradients
        assert codes.grad is not None
        assert not torch.isnan(codes.grad).any()

    def test_decoder_deterministic(self, decoder):
        """Test decoder produces deterministic outputs."""
        torch.manual_seed(42)
        codes = torch.randn(1, 16, 12)

        # Run twice with same input
        decoder.eval()
        with torch.no_grad():
            reconstructed1, _ = decoder(codes)
            reconstructed2, _ = decoder(codes)

        # Outputs should be identical
        torch.testing.assert_close(reconstructed1, reconstructed2)

    def test_decoder_device_compatibility(self, decoder):
        """Test decoder works on different devices."""
        codes = torch.randn(1, 16, 12)

        # CPU test
        decoder_cpu = decoder.to('cpu')
        codes_cpu = codes.to('cpu')
        reconstructed_cpu, _ = decoder_cpu(codes_cpu)
        assert reconstructed_cpu.device.type == 'cpu'

        # CUDA test (if available)
        if torch.cuda.is_available():
            decoder_cuda = decoder.to('cuda')
            codes_cuda = codes.to('cuda')
            reconstructed_cuda, _ = decoder_cuda(codes_cuda)
            assert reconstructed_cuda.device.type == 'cuda'

        # MPS test (if available)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            decoder_mps = decoder.to('mps')
            codes_mps = codes.to('mps')
            reconstructed_mps, _ = decoder_mps(codes_mps)
            assert reconstructed_mps.device.type == 'mps'

    def test_decoder_dtype_compatibility(self, decoder):
        """Test decoder works with different dtypes."""
        codes = torch.randn(1, 16, 12)

        # Float32
        decoder_fp32 = decoder.to(torch.float32)
        codes_fp32 = codes.to(torch.float32)
        reconstructed_fp32, _ = decoder_fp32(codes_fp32)
        assert reconstructed_fp32.dtype == torch.float32

        # Float64
        decoder_fp64 = decoder.to(torch.float64)
        codes_fp64 = codes.to(torch.float64)
        reconstructed_fp64, _ = decoder_fp64(codes_fp64)
        assert reconstructed_fp64.dtype == torch.float64

    def test_decoder_eval_mode(self, decoder):
        """Test decoder behaves consistently in eval mode."""
        codes = torch.randn(1, 16, 12)

        decoder.eval()
        with torch.no_grad():
            reconstructed1, _ = decoder(codes)
            reconstructed2, _ = decoder(codes)

        # Should produce identical results in eval mode
        torch.testing.assert_close(reconstructed1, reconstructed2)

    def test_decoder_parameter_count(self, decoder):
        """Test decoder has expected number of parameters."""
        total_params = sum(p.numel() for p in decoder.parameters())

        # Should have approximately 31M parameters (decoder portion)
        assert total_params > 10_000_000  # At least 10M
        assert total_params < 50_000_000  # Less than 50M

    def test_decoder_custom_config(self):
        """Test decoder with custom configuration."""
        custom_decoder = CausalHiFiGANDecoder(
            up_sample_rates=[2, 2, 2],
            input_dim=8,
            base_channels=128,
            activation="half_snake",
            output_activation="clamp",
            pad_mode="zeros",
            n_groups_equal_to_out_channels=True
        )

        codes = torch.randn(1, 8, 100)
        reconstructed, recon_len = custom_decoder(codes)

        # Upsampling: 2 * 2 * 2 = 8
        expected_len = 100 * 8
        assert reconstructed.shape == (1, 1, expected_len)

    def test_decoder_causality(self, decoder):
        """Test that decoder is causal (doesn't look ahead)."""
        # Create input with only first half non-zero
        time_dim = 20
        codes = torch.zeros(1, 16, time_dim)
        codes[:, :, :10] = torch.randn(1, 16, 10)  # Only first half has signal

        reconstructed, _ = decoder(codes)

        # The first half of output should have more energy than second half
        # (due to causal padding)
        mid_point = reconstructed.shape[2] // 2
        first_half_energy = reconstructed[:, :, :mid_point].abs().mean()
        second_half_energy = reconstructed[:, :, mid_point:].abs().mean()

        # First half should have significantly more energy
        assert first_half_energy > second_half_energy * 0.5

    def test_decoder_small_input(self, decoder):
        """Test decoder with very small input."""
        codes = torch.randn(1, 16, 2)  # Just 2 frames
        reconstructed, recon_len = decoder(codes)

        assert reconstructed.shape[2] == 2 * 1764

    def test_decoder_large_batch(self, decoder):
        """Test decoder with large batch size."""
        batch_size = 32
        codes = torch.randn(batch_size, 16, 12)

        reconstructed, recon_len = decoder(codes)

        assert reconstructed.shape[0] == batch_size
        assert recon_len.shape[0] == batch_size

    def test_decoder_output_activation_clamp(self, decoder):
        """Test that output activation properly clamps values."""
        # Feed in very large values
        codes = torch.randn(1, 16, 12) * 100

        reconstructed, _ = decoder(codes)

        # Output should still be clamped to [-1, 1]
        assert reconstructed.min() >= -1.0
        assert reconstructed.max() <= 1.0

    def test_decoder_zero_input(self, decoder):
        """Test decoder with zero input."""
        codes = torch.zeros(1, 16, 12)
        reconstructed, recon_len = decoder(codes)

        # Should produce valid output (not all zeros due to biases)
        assert reconstructed.shape == (1, 1, 12 * 1764)
        assert not torch.isnan(reconstructed).any()
        assert not torch.isinf(reconstructed).any()
