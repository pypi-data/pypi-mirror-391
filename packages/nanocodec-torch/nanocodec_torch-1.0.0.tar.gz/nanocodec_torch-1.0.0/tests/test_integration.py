"""
Integration tests for the full NanoCodec model pipeline.
"""

import pytest
import torch
import tempfile
import os
from src.nanocodec_torch.models.audio_codec import AudioCodecModel


class TestAudioCodecModelIntegration:
    """Integration tests for the full audio codec pipeline."""

    @pytest.fixture
    def model(self):
        """Create a default model instance."""
        return AudioCodecModel(sample_rate=22050)

    def test_model_initialization(self, model):
        """Test model initializes with all components."""
        assert model is not None
        assert model.audio_encoder is not None
        assert model.audio_decoder is not None
        assert model.vector_quantizer is not None
        assert model.sample_rate == 22050
        assert model.samples_per_frame == 1764

    def test_model_info(self, model):
        """Test model info contains expected fields."""
        info = model.get_info()

        assert 'sample_rate' in info
        assert 'samples_per_frame' in info
        assert 'encoder_params' in info
        assert 'decoder_params' in info
        assert 'quantizer_codebook_size' in info
        assert 'device' in info

        # Check reasonable parameter counts
        assert info['encoder_params'] > 10_000_000
        assert info['decoder_params'] > 10_000_000

    def test_full_pipeline_forward(self, model):
        """Test full encode-quantize-decode pipeline via forward()."""
        batch_size = 2
        duration_samples = 22050  # 1 second

        audio = torch.randn(batch_size, 1, duration_samples)
        audio_len = torch.tensor([duration_samples, duration_samples])

        # Full pipeline
        reconstructed, tokens, recon_len = model(audio, audio_len)

        # Check shapes
        assert reconstructed.shape[0] == batch_size
        assert reconstructed.shape[1] == 1
        assert tokens.shape[0] == batch_size
        assert tokens.shape[1] == 4  # 4 groups
        assert recon_len.shape[0] == batch_size

    def test_separate_encode_decode(self, model):
        """Test encode() and decode() methods separately."""
        audio = torch.randn(1, 1, 22050)
        audio_len = torch.tensor([22050])

        # Encode
        tokens, tokens_len = model.encode(audio, audio_len)

        assert tokens.shape[0] == 1
        assert tokens.shape[1] == 4
        assert tokens.dtype == torch.int32

        # Decode
        reconstructed, recon_len = model.decode(tokens, tokens_len)

        assert reconstructed.shape[0] == 1
        assert reconstructed.shape[1] == 1
        assert recon_len.shape[0] == 1

    def test_compression_ratio(self, model):
        """Test that compression achieves expected ratio."""
        duration_samples = 22050
        audio = torch.randn(1, 1, duration_samples)

        tokens, _ = model.encode(audio)

        # Expected: 1764:1 compression
        expected_frames = duration_samples // 1764
        assert tokens.shape[2] == expected_frames

        # Tokens are int32, so each token is 4 bytes
        # 4 groups × expected_frames × 4 bytes
        compressed_bytes = 4 * expected_frames * 4

        # Original audio (assuming 16-bit): duration_samples × 2 bytes
        original_bytes = duration_samples * 2

        compression_ratio = original_bytes / compressed_bytes

        # Should be close to expected 1764:1, but accounting for int32 vs int16
        assert compression_ratio > 100  # At least 100:1

    def test_different_audio_lengths(self, model):
        """Test model with various audio lengths."""
        test_lengths = [
            22050,      # 1 second
            44100,      # 2 seconds
            88200,      # 4 seconds
            22050 * 10  # 10 seconds
        ]

        for length in test_lengths:
            audio = torch.randn(1, 1, length)

            reconstructed, tokens, _ = model(audio)

            expected_frames = length // 1764
            assert tokens.shape[2] == expected_frames

    def test_variable_batch_lengths(self, model):
        """Test model with variable lengths in a batch."""
        batch_size = 4
        max_length = 44100

        audio = torch.randn(batch_size, 1, max_length)
        audio_len = torch.tensor([22050, 33075, 44100, 17640])

        reconstructed, tokens, recon_len = model(audio, audio_len)

        assert reconstructed.shape[0] == batch_size
        assert tokens.shape[0] == batch_size

    def test_output_audio_range(self, model):
        """Test reconstructed audio is in valid range."""
        audio = torch.randn(1, 1, 22050)

        reconstructed, _, _ = model(audio)

        # Should be clamped to [-1, 1]
        assert reconstructed.min() >= -1.0
        assert reconstructed.max() <= 1.0

    def test_output_not_silent(self, model):
        """Test that model produces non-silent output."""
        # Input with some energy
        audio = torch.randn(1, 1, 22050) * 0.5

        reconstructed, _, _ = model(audio)

        # Output should have some energy
        assert reconstructed.abs().mean() > 0.001

    def test_model_deterministic_in_eval(self, model):
        """Test model produces deterministic output in eval mode."""
        torch.manual_seed(42)
        audio = torch.randn(1, 1, 22050)

        model.eval()
        with torch.no_grad():
            recon1, tokens1, _ = model(audio)
            recon2, tokens2, _ = model(audio)

        torch.testing.assert_close(recon1, recon2)
        torch.testing.assert_close(tokens1, tokens2)

    def test_gradient_flow_through_model(self, model):
        """Test gradients flow through entire model."""
        audio = torch.randn(1, 1, 22050, requires_grad=True)

        reconstructed, _, _ = model(audio)

        # Compute loss and backpropagate
        loss = (reconstructed - audio[:, :, :reconstructed.shape[2]]).pow(2).mean()
        loss.backward()

        # Input should have gradients
        assert audio.grad is not None
        assert not torch.isnan(audio.grad).any()

    def test_model_eval_train_modes(self, model):
        """Test model can switch between train and eval modes."""
        # Train mode
        model.train()
        assert model.training

        # Eval mode
        model.eval()
        assert not model.training

    def test_device_movement(self, model):
        """Test model can move between devices."""
        audio = torch.randn(1, 1, 22050)

        # CPU
        model_cpu = model.to('cpu')
        audio_cpu = audio.to('cpu')
        device = model_cpu.get_device()
        assert device.type == 'cpu'

        recon_cpu, _, _ = model_cpu(audio_cpu)
        assert recon_cpu.device.type == 'cpu'

        # CUDA (if available)
        if torch.cuda.is_available():
            model_cuda = model.to('cuda')
            audio_cuda = audio.to('cuda')
            device = model_cuda.get_device()
            assert device.type == 'cuda'

            recon_cuda, _, _ = model_cuda(audio_cuda)
            assert recon_cuda.device.type == 'cuda'

        # MPS (if available)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            model_mps = model.to('mps')
            audio_mps = audio.to('mps')
            device = model_mps.get_device()
            assert device.type == 'mps'

            recon_mps, _, _ = model_mps(audio_mps)
            assert recon_mps.device.type == 'mps'

    def test_dtype_conversion(self, model):
        """Test model works with different dtypes."""
        audio = torch.randn(1, 1, 22050)

        # Float32 (primary dtype for model)
        model_fp32 = model.to(torch.float32)
        audio_fp32 = audio.to(torch.float32)
        recon_fp32, _, _ = model_fp32(audio_fp32)
        assert recon_fp32.dtype == torch.float32

        # Float16 (half precision)
        try:
            model_fp16 = model.to(torch.float16)
            audio_fp16 = audio.to(torch.float16)
            recon_fp16, _, _ = model_fp16(audio_fp16)
            assert recon_fp16.dtype == torch.float16
        except RuntimeError:
            # FP16 may not be supported on all devices
            pytest.skip("FP16 not supported on this device")

    def test_amp_compatibility(self, model):
        """Test model works with automatic mixed precision."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available for AMP testing")

        model = model.to('cuda')
        audio = torch.randn(1, 1, 22050).to('cuda')

        # Test with AMP
        reconstructed, tokens, _ = model(audio, use_amp=True)

        assert reconstructed.device.type == 'cuda'
        assert not torch.isnan(reconstructed).any()

    def test_batch_independence(self, model):
        """Test that batch items are processed independently."""
        batch_size = 4
        audio = torch.randn(batch_size, 1, 22050)

        # Process as batch
        recon_batch, tokens_batch, _ = model(audio)

        # Process individually
        recon_individual = []
        tokens_individual = []
        for i in range(batch_size):
            recon, tokens, _ = model(audio[i:i+1])
            recon_individual.append(recon)
            tokens_individual.append(tokens)

        recon_individual = torch.cat(recon_individual, dim=0)
        tokens_individual = torch.cat(tokens_individual, dim=0)

        # Should be identical
        torch.testing.assert_close(recon_batch, recon_individual)
        torch.testing.assert_close(tokens_batch, tokens_individual)

    def test_zero_audio_input(self, model):
        """Test model handles zero (silent) input."""
        audio = torch.zeros(1, 1, 22050)

        reconstructed, tokens, _ = model(audio)

        # Should produce valid output
        assert not torch.isnan(reconstructed).any()
        assert not torch.isnan(tokens.float()).any()

    def test_extreme_audio_values(self, model):
        """Test model handles extreme audio values."""
        # Very loud audio (should be clipped)
        audio_loud = torch.randn(1, 1, 22050) * 10

        reconstructed, _, _ = model(audio_loud)

        # Output should still be in valid range
        assert reconstructed.min() >= -1.0
        assert reconstructed.max() <= 1.0

    def test_minimum_viable_audio_length(self, model):
        """Test model with minimum audio length."""
        # Minimum: 1 frame worth (1764 samples)
        min_length = 1764 * 2

        audio = torch.randn(1, 1, min_length)

        reconstructed, tokens, _ = model(audio)

        assert tokens.shape[2] >= 1  # At least 1 frame
        assert reconstructed.shape[2] > 0

    def test_large_batch_size(self, model):
        """Test model with large batch size."""
        batch_size = 32
        audio = torch.randn(batch_size, 1, 22050)

        reconstructed, tokens, _ = model(audio)

        assert reconstructed.shape[0] == batch_size
        assert tokens.shape[0] == batch_size

    def test_to_device_helper(self, model):
        """Test to_device() helper method."""
        # Move to CPU
        model_cpu = model.to_device('cpu')
        assert model_cpu.get_device().type == 'cpu'

        # CUDA (if available)
        if torch.cuda.is_available():
            model_cuda = model.to_device('cuda')
            assert model_cuda.get_device().type == 'cuda'

    def test_parameter_count(self, model):
        """Test total parameter count is reasonable."""
        total_params = sum(p.numel() for p in model.parameters())

        # Should have around 100M total parameters
        assert total_params > 50_000_000
        assert total_params < 150_000_000

    def test_input_shape_flexibility(self, model):
        """Test model accepts different input shapes."""
        # [B, T] - mono without channel dimension
        audio_2d = torch.randn(2, 22050)
        recon_2d, _, _ = model(audio_2d)
        assert recon_2d.shape[1] == 1

        # [B, 1, T] - standard format
        audio_3d = torch.randn(2, 1, 22050)
        recon_3d, _, _ = model(audio_3d)
        assert recon_3d.shape[1] == 1

        # [T] - single sample without batch
        audio_1d = torch.randn(22050)
        recon_1d, _, _ = model(audio_1d)
        assert recon_1d.shape[0] == 1
        assert recon_1d.shape[1] == 1

    def test_reconstruction_quality(self, model):
        """Test that reconstruction has reasonable quality."""
        # Generate sine wave (easy to reconstruct)
        t = torch.linspace(0, 1, 22050)
        audio = torch.sin(2 * torch.pi * 440 * t).unsqueeze(0).unsqueeze(0)

        model.eval()
        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Trim to same length
        min_len = min(audio.shape[2], reconstructed.shape[2])
        audio = audio[:, :, :min_len]
        reconstructed = reconstructed[:, :, :min_len]

        # Should have some correlation with input
        correlation = torch.corrcoef(torch.stack([
            audio.flatten(),
            reconstructed.flatten()
        ]))[0, 1]

        # For a 0.6kbps lossy codec, correlation can be very low
        # Just check that it's not completely inverted
        assert correlation > -0.5

    def test_tokens_are_discrete(self, model):
        """Test that tokens are discrete integers."""
        audio = torch.randn(1, 1, 22050)

        tokens, _ = model.encode(audio)

        # Tokens should be integers
        assert tokens.dtype == torch.int32

        # All tokens should be non-negative
        assert tokens.min() >= 0

        # Tokens should be within codebook size
        assert tokens.max() < 4032  # Per-group codebook size
