"""
Unit tests for HiFiGAN Encoder module.
"""

import pytest
import torch
from src.nanocodec_torch.models.encoder import HiFiGANEncoder


class TestHiFiGANEncoder:
    """Test suite for HiFiGAN Encoder."""

    @pytest.fixture
    def encoder(self):
        """Create a default encoder instance."""
        return HiFiGANEncoder(
            down_sample_rates=[2, 3, 6, 7, 7],
            encoded_dim=16,
            base_channels=24,
            activation="lrelu",
            pad_mode="replicate"
        )

    def test_encoder_initialization(self, encoder):
        """Test encoder initializes correctly."""
        assert isinstance(encoder, HiFiGANEncoder)
        assert encoder.encoded_dim == 16
        assert encoder.base_channels == 24
        assert len(encoder.down_sample_conv_layers) == 5
        assert len(encoder.res_layers) == 5

    def test_encoder_output_shape(self, encoder):
        """Test encoder produces correct output shape."""
        batch_size = 2
        seq_len = 22050  # 1 second at 22050 Hz
        audio = torch.randn(batch_size, 1, seq_len)

        encoded, encoded_len = encoder(audio)

        # Check shape: [B, 16, T/1764]
        expected_time_dim = seq_len // 1764
        assert encoded.shape == (batch_size, 16, expected_time_dim)
        assert encoded_len.shape == (batch_size,)

    def test_encoder_downsampling_factor(self, encoder):
        """Test encoder applies correct downsampling factor."""
        seq_len = 22050 * 4  # 4 seconds
        audio = torch.randn(1, 1, seq_len)

        encoded, encoded_len = encoder(audio)

        # Downsample factor should be 2 * 3 * 6 * 7 * 7 = 1764
        expected_samples = seq_len // 1764
        assert encoded.shape[2] == expected_samples

    def test_encoder_with_different_input_lengths(self, encoder):
        """Test encoder handles different input lengths."""
        test_lengths = [22050, 44100, 88200]  # 1s, 2s, 4s

        for seq_len in test_lengths:
            audio = torch.randn(1, 1, seq_len)
            encoded, encoded_len = encoder(audio)

            expected_len = seq_len // 1764
            assert encoded.shape[2] == expected_len
            assert encoded_len.item() == expected_len

    def test_encoder_batch_processing(self, encoder):
        """Test encoder handles batched inputs correctly."""
        batch_sizes = [1, 2, 4, 8]
        seq_len = 22050

        for batch_size in batch_sizes:
            audio = torch.randn(batch_size, 1, seq_len)
            encoded, encoded_len = encoder(audio)

            assert encoded.shape[0] == batch_size
            assert encoded_len.shape[0] == batch_size

    def test_encoder_with_audio_len(self, encoder):
        """Test encoder with explicit audio lengths."""
        batch_size = 3
        max_len = 44100

        # Different lengths for each batch item
        audio = torch.randn(batch_size, 1, max_len)
        audio_len = torch.tensor([22050, 33075, 44100])

        encoded, encoded_len = encoder(audio, audio_len)

        assert encoded.shape[0] == batch_size
        assert encoded_len.shape[0] == batch_size

        # Check that encoded lengths are approximately correct
        expected_lens = audio_len // 1764
        torch.testing.assert_close(encoded_len, expected_lens, rtol=0, atol=1)

    def test_encoder_output_range(self, encoder):
        """Test encoder output values are reasonable."""
        audio = torch.randn(1, 1, 22050)
        encoded, _ = encoder(audio)

        # Output should not be all zeros
        assert encoded.abs().sum() > 0

        # Output should not contain NaN or Inf
        assert not torch.isnan(encoded).any()
        assert not torch.isinf(encoded).any()

    def test_encoder_gradient_flow(self, encoder):
        """Test gradients flow through encoder."""
        audio = torch.randn(1, 1, 22050, requires_grad=True)
        encoded, _ = encoder(audio)

        # Compute dummy loss and backpropagate
        loss = encoded.sum()
        loss.backward()

        # Check that input has gradients
        assert audio.grad is not None
        assert not torch.isnan(audio.grad).any()

    def test_encoder_deterministic(self, encoder):
        """Test encoder produces deterministic outputs."""
        torch.manual_seed(42)
        audio = torch.randn(1, 1, 22050)

        # Run twice with same input
        encoder.eval()
        with torch.no_grad():
            encoded1, _ = encoder(audio)
            encoded2, _ = encoder(audio)

        # Outputs should be identical
        torch.testing.assert_close(encoded1, encoded2)

    def test_encoder_device_compatibility(self, encoder):
        """Test encoder works on different devices."""
        audio = torch.randn(1, 1, 22050)

        # CPU test
        encoder_cpu = encoder.to('cpu')
        audio_cpu = audio.to('cpu')
        encoded_cpu, _ = encoder_cpu(audio_cpu)
        assert encoded_cpu.device.type == 'cpu'

        # CUDA test (if available)
        if torch.cuda.is_available():
            encoder_cuda = encoder.to('cuda')
            audio_cuda = audio.to('cuda')
            encoded_cuda, _ = encoder_cuda(audio_cuda)
            assert encoded_cuda.device.type == 'cuda'

        # MPS test (if available)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            encoder_mps = encoder.to('mps')
            audio_mps = audio.to('mps')
            encoded_mps, _ = encoder_mps(audio_mps)
            assert encoded_mps.device.type == 'mps'

    def test_encoder_dtype_compatibility(self, encoder):
        """Test encoder works with different dtypes."""
        audio = torch.randn(1, 1, 22050)

        # Float32
        encoder_fp32 = encoder.to(torch.float32)
        audio_fp32 = audio.to(torch.float32)
        encoded_fp32, _ = encoder_fp32(audio_fp32)
        assert encoded_fp32.dtype == torch.float32

        # Float64
        encoder_fp64 = encoder.to(torch.float64)
        audio_fp64 = audio.to(torch.float64)
        encoded_fp64, _ = encoder_fp64(audio_fp64)
        assert encoded_fp64.dtype == torch.float64

    def test_encoder_eval_mode(self, encoder):
        """Test encoder behaves consistently in eval mode."""
        audio = torch.randn(1, 1, 22050)

        encoder.eval()
        with torch.no_grad():
            encoded1, _ = encoder(audio)
            encoded2, _ = encoder(audio)

        # Should produce identical results in eval mode
        torch.testing.assert_close(encoded1, encoded2)

    def test_encoder_parameter_count(self, encoder):
        """Test encoder has expected number of parameters."""
        total_params = sum(p.numel() for p in encoder.parameters())

        # Should have approximately 30M parameters (encoder portion)
        assert total_params > 10_000_000  # At least 10M
        assert total_params < 50_000_000  # Less than 50M

    def test_encoder_custom_config(self):
        """Test encoder with custom configuration."""
        custom_encoder = HiFiGANEncoder(
            down_sample_rates=[2, 2, 2],
            encoded_dim=8,
            base_channels=16,
            activation="lrelu",
            pad_mode="replicate"
        )

        audio = torch.randn(1, 1, 16000)
        encoded, encoded_len = custom_encoder(audio)

        # Downsampling: 2 * 2 * 2 = 8
        # Due to padding, output may be slightly larger
        assert encoded.shape[0] == 1
        assert encoded.shape[1] == 8
        assert encoded.shape[2] >= 16000 // 8
        assert encoded.shape[2] <= 16000 // 8 + 10  # Allow small padding difference

    def test_encoder_small_input(self, encoder):
        """Test encoder with very small input."""
        # Minimum viable input
        audio = torch.randn(1, 1, 1764 * 2)  # 2 frames worth
        encoded, encoded_len = encoder(audio)

        assert encoded.shape[2] >= 1  # At least 1 frame output

    def test_encoder_large_batch(self, encoder):
        """Test encoder with large batch size."""
        batch_size = 32
        audio = torch.randn(batch_size, 1, 22050)

        encoded, encoded_len = encoder(audio)

        assert encoded.shape[0] == batch_size
        assert encoded_len.shape[0] == batch_size
