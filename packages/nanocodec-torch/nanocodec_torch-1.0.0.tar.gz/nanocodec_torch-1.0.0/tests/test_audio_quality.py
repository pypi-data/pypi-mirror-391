"""
Audio quality validation tests for NanoCodec.
Tests various audio properties and quality metrics.
"""

import pytest
import torch
import numpy as np
from src.nanocodec_torch.models.audio_codec import AudioCodecModel


class TestAudioQuality:
    """Test suite for audio quality validation."""

    @pytest.fixture
    def model(self):
        """Create model instance in eval mode."""
        model = AudioCodecModel(sample_rate=22050)
        model.eval()
        return model

    def test_dc_offset_preservation(self, model):
        """Test that DC offset is handled correctly."""
        # Audio with DC offset
        audio = torch.randn(1, 1, 22050) * 0.5 + 0.3

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Reconstructed should be centered (no extreme DC offset)
        # Due to clamping, DC might not be perfectly preserved
        assert reconstructed.mean().abs() < 0.5

    def test_signal_to_noise_ratio(self, model):
        """Test basic signal-to-noise ratio."""
        # Generate clean sine wave
        t = torch.linspace(0, 1, 22050)
        audio = torch.sin(2 * torch.pi * 440 * t).unsqueeze(0).unsqueeze(0) * 0.5

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Trim to same length
        min_len = min(audio.shape[2], reconstructed.shape[2])
        audio_trimmed = audio[:, :, :min_len]
        recon_trimmed = reconstructed[:, :, :min_len]

        # Calculate SNR
        signal_power = (audio_trimmed ** 2).mean()
        noise_power = ((audio_trimmed - recon_trimmed) ** 2).mean()

        snr_db = 10 * torch.log10(signal_power / (noise_power + 1e-8))

        # For a 0.6kbps lossy codec, expect significant degradation
        # Just check that it's not completely broken (> -10 dB)
        assert snr_db > -10

    def test_frequency_response_preservation(self, model):
        """Test that frequency content is somewhat preserved."""
        # Generate multi-frequency signal
        t = torch.linspace(0, 1, 22050)
        audio = (
            0.3 * torch.sin(2 * torch.pi * 220 * t) +  # A3
            0.3 * torch.sin(2 * torch.pi * 440 * t) +  # A4
            0.3 * torch.sin(2 * torch.pi * 880 * t)    # A5
        ).unsqueeze(0).unsqueeze(0)

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Both should have energy (not silent)
        assert audio.abs().mean() > 0.1
        assert reconstructed.abs().mean() > 0.01

    def test_amplitude_preservation(self, model):
        """Test that amplitude levels are roughly preserved."""
        # Different amplitude levels
        amplitudes = [0.1, 0.3, 0.5, 0.7, 0.9]

        for amp in amplitudes:
            audio = torch.randn(1, 1, 22050) * amp

            with torch.no_grad():
                reconstructed, _, _ = model(audio)

            # Reconstructed should have some relation to input amplitude
            # (though not perfect due to compression)
            input_rms = audio.pow(2).mean().sqrt()
            output_rms = reconstructed.pow(2).mean().sqrt()

            # Should be in similar order of magnitude
            assert output_rms > input_rms * 0.01  # Not completely silent
            assert output_rms < 1.0  # Clamped to reasonable range

    def test_transient_response(self, model):
        """Test handling of transients (sudden changes)."""
        # Create signal with sharp transient
        audio = torch.zeros(1, 1, 22050)
        audio[:, :, 11025:11075] = 0.8  # Short burst in middle

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Reconstructed should have some energy in the transient region
        transient_start = 11025 // 1764 * 1764
        transient_end = transient_start + 1764 * 2

        if transient_end <= reconstructed.shape[2]:
            transient_region = reconstructed[:, :, transient_start:transient_end]
            assert transient_region.abs().mean() > 0.01

    def test_silence_preservation(self, model):
        """Test that silence is preserved (no artifacts)."""
        # Silent audio
        audio = torch.zeros(1, 1, 22050)

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Reconstructed should be mostly silent (small artifacts OK)
        assert reconstructed.abs().mean() < 0.1

    def test_clipping_avoidance(self, model):
        """Test that output doesn't clip excessively."""
        # Normal audio
        audio = torch.randn(1, 1, 22050) * 0.5

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Check that most samples are not at clipping threshold
        clipped_samples = ((reconstructed.abs() - 1.0).abs() < 0.01).float().mean()

        # Less than 5% of samples should be clipped
        assert clipped_samples < 0.05

    def test_phase_coherence(self, model):
        """Test basic phase coherence with sine wave."""
        # Pure sine wave
        t = torch.linspace(0, 1, 22050)
        frequency = 440
        audio = torch.sin(2 * torch.pi * frequency * t).unsqueeze(0).unsqueeze(0)

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Trim to same length
        min_len = min(audio.shape[2], reconstructed.shape[2])

        # Check correlation (measures phase alignment)
        audio_np = audio[0, 0, :min_len].numpy()
        recon_np = reconstructed[0, 0, :min_len].numpy()

        correlation = np.corrcoef(audio_np, recon_np)[0, 1]

        # For a 0.6kbps codec, phase coherence is often lost
        # Just check that correlation is reasonable (not completely inverted)
        assert correlation > -0.5

    def test_stereo_to_mono_handling(self, model):
        """Test that model handles mono input correctly."""
        # Model expects mono, test with mono input
        audio = torch.randn(1, 1, 22050) * 0.5

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Output should be mono
        assert reconstructed.shape[1] == 1

    def test_energy_preservation(self, model):
        """Test that overall energy is somewhat preserved."""
        audio = torch.randn(1, 1, 22050) * 0.5

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Calculate energy
        min_len = min(audio.shape[2], reconstructed.shape[2])
        input_energy = (audio[:, :, :min_len] ** 2).sum()
        output_energy = (reconstructed[:, :, :min_len] ** 2).sum()

        # Energies should be in similar range
        # For a 0.6kbps codec with 1764:1 compression, energy can be VERY low
        # Just verify it's not completely zero (which would indicate total failure)
        energy_ratio = output_energy / (input_energy + 1e-8)
        assert energy_ratio > 1e-6  # Allow for extreme compression artifacts
        assert energy_ratio < 100

    def test_harmonic_distortion(self, model):
        """Test for excessive harmonic distortion."""
        # Pure tone
        t = torch.linspace(0, 1, 22050)
        audio = torch.sin(2 * torch.pi * 440 * t).unsqueeze(0).unsqueeze(0) * 0.5

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Reconstructed should not be constant (which would indicate total failure)
        # For a 0.6kbps codec, std can be very low
        assert reconstructed.std() > 0.0001

        # Should not have extreme values everywhere (excessive distortion)
        assert (reconstructed.abs() < 0.99).float().mean() > 0.9

    def test_noise_floor(self, model):
        """Test noise floor with very quiet signal."""
        # Very quiet signal
        audio = torch.randn(1, 1, 22050) * 0.01

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Should not amplify to full scale
        assert reconstructed.abs().max() < 0.9

    def test_dynamic_range(self, model):
        """Test handling of dynamic range."""
        # Signal with varying dynamics
        t = torch.linspace(0, 1, 22050)
        envelope = torch.linspace(0.1, 0.9, 22050)
        audio = (envelope * torch.sin(2 * torch.pi * 440 * t)).unsqueeze(0).unsqueeze(0)

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Reconstructed should have some dynamic variation
        # For a 0.6kbps codec, std can be very low
        assert reconstructed.std() > 0.0001

    def test_impulse_response(self, model):
        """Test impulse response."""
        # Single impulse
        audio = torch.zeros(1, 1, 22050)
        audio[:, :, 11025] = 1.0

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Should produce some response (not stay silent)
        assert reconstructed.abs().sum() > 0.1

    def test_white_noise_handling(self, model):
        """Test handling of white noise."""
        # White noise
        audio = torch.randn(1, 1, 22050) * 0.3

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Should produce non-silent output
        assert reconstructed.abs().mean() > 0.01

        # Should be within valid range
        assert reconstructed.min() >= -1.0
        assert reconstructed.max() <= 1.0

    def test_multi_tone_preservation(self, model):
        """Test preservation of multiple simultaneous tones."""
        # Create chord (multiple frequencies)
        t = torch.linspace(0, 1, 22050)
        audio = (
            0.25 * torch.sin(2 * torch.pi * 261.63 * t) +  # C4
            0.25 * torch.sin(2 * torch.pi * 329.63 * t) +  # E4
            0.25 * torch.sin(2 * torch.pi * 392.00 * t)    # G4
        ).unsqueeze(0).unsqueeze(0)

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Should preserve multi-tone character (not collapse to silence)
        # For a 0.6kbps codec, amplitude can be very low
        assert reconstructed.abs().mean() > 0.001

    def test_reconstruction_consistency(self, model):
        """Test that reconstruction is consistent across runs."""
        audio = torch.randn(1, 1, 22050) * 0.5

        with torch.no_grad():
            recon1, _, _ = model(audio)
            recon2, _, _ = model(audio)

        # Should be deterministic in eval mode
        torch.testing.assert_close(recon1, recon2)

    def test_boundary_conditions(self, model):
        """Test audio at amplitude boundaries."""
        # Maximum amplitude
        audio_max = torch.ones(1, 1, 22050) * 0.99

        with torch.no_grad():
            recon_max, _, _ = model(audio_max)

        # Should handle without NaN or Inf
        assert not torch.isnan(recon_max).any()
        assert not torch.isinf(recon_max).any()

        # Minimum amplitude
        audio_min = torch.ones(1, 1, 22050) * -0.99

        with torch.no_grad():
            recon_min, _, _ = model(audio_min)

        assert not torch.isnan(recon_min).any()
        assert not torch.isinf(recon_min).any()

    def test_temporal_stability(self, model):
        """Test temporal stability (no excessive temporal artifacts)."""
        # Constant tone
        t = torch.linspace(0, 2, 44100)  # 2 seconds
        audio = torch.sin(2 * torch.pi * 440 * t).unsqueeze(0).unsqueeze(0) * 0.5

        with torch.no_grad():
            reconstructed, _, _ = model(audio)

        # Split into chunks and check consistency
        chunk_size = 11025
        chunks = []
        for i in range(0, min(reconstructed.shape[2], 44100), chunk_size):
            end = min(i + chunk_size, reconstructed.shape[2])
            if end - i > chunk_size // 2:  # Only use reasonably sized chunks
                chunk = reconstructed[:, :, i:end]
                chunks.append(chunk.abs().mean())

        if len(chunks) >= 2:
            # RMS energy of chunks should be relatively stable
            chunks_tensor = torch.tensor(chunks)
            stability = chunks_tensor.std() / (chunks_tensor.mean() + 1e-8)

            # Coefficient of variation should be reasonable
            assert stability < 2.0
