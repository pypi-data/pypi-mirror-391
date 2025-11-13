"""
Unit tests for Grouped Finite Scalar Quantizer module.
"""

import pytest
import torch
from src.nanocodec_torch.models.quantizer_fixed import (
    FiniteScalarQuantizer,
    GroupFiniteScalarQuantizer
)


class TestFiniteScalarQuantizer:
    """Test suite for single FSQ module."""

    @pytest.fixture
    def fsq(self):
        """Create a default FSQ instance."""
        return FiniteScalarQuantizer(
            num_levels=[9, 8, 8, 7]
        )

    def test_fsq_initialization(self, fsq):
        """Test FSQ initializes correctly."""
        assert isinstance(fsq, FiniteScalarQuantizer)
        assert fsq.dim == 4
        assert fsq.num_levels.tolist() == [9, 8, 8, 7]
        assert fsq.codebook_size == 9 * 8 * 8 * 7  # 4032

    def test_fsq_codebook_size(self):
        """Test codebook size calculation."""
        # Default config
        fsq1 = FiniteScalarQuantizer([9, 8, 8, 7])
        assert fsq1.codebook_size == 4032

        # Different config
        fsq2 = FiniteScalarQuantizer([8, 8, 8, 8])
        assert fsq2.codebook_size == 4096

        # Single level
        fsq3 = FiniteScalarQuantizer([256])
        assert fsq3.codebook_size == 256

    def test_fsq_encode_shape(self, fsq):
        """Test FSQ encoding produces correct shape."""
        batch_size = 2
        time_dim = 12
        codes = torch.randn(batch_size, 4, time_dim)

        indices = fsq.encode(codes)

        # Should output flat indices per timestep [B, T]
        assert indices.shape == (batch_size, time_dim)
        assert indices.dtype == torch.int32

    def test_fsq_decode_shape(self, fsq):
        """Test FSQ decoding produces correct shape."""
        batch_size = 2
        time_dim = 12
        # FSQ decode expects [B, T] flat indices
        indices = torch.randint(0, 4032, (batch_size, time_dim), dtype=torch.int32)

        codes = fsq.decode(indices)

        # Should output 4-dimensional codes [B, D, T]
        assert codes.shape == (batch_size, 4, time_dim)

    def test_fsq_roundtrip(self, fsq):
        """Test FSQ encode-decode roundtrip."""
        codes = torch.randn(1, 4, 10)

        # Encode then decode
        indices = fsq.encode(codes)
        reconstructed = fsq.decode(indices)

        # Shape should match
        assert reconstructed.shape == codes.shape

        # Values should be close (with quantization error)
        # FSQ quantizes to discrete levels, so exact match not expected
        # but should be within reasonable range
        assert (reconstructed - codes).abs().mean() < 1.0

    def test_fsq_encode_output_range(self, fsq):
        """Test FSQ encode produces valid indices."""
        codes = torch.randn(2, 4, 20) * 5  # Scale up input

        indices = fsq.encode(codes)

        # Indices should be within [0, codebook_size)
        assert indices.min() >= 0
        assert indices.max() < fsq.codebook_size

    def test_fsq_decode_output_range(self, fsq):
        """Test FSQ decode produces values in valid range."""
        # Valid indices
        indices = torch.randint(0, 4032, (2, 1, 20), dtype=torch.int32)

        codes = fsq.decode(indices)

        # Codes should be in reasonable range (FSQ normalizes to roughly [-1, 1])
        assert codes.abs().max() < 10.0  # Reasonable upper bound

    def test_fsq_deterministic(self, fsq):
        """Test FSQ is deterministic."""
        codes = torch.randn(1, 4, 10)

        # Encode twice
        indices1 = fsq.encode(codes)
        indices2 = fsq.encode(codes)

        # Should be identical
        torch.testing.assert_close(indices1, indices2)

        # Decode twice
        decoded1 = fsq.decode(indices1)
        decoded2 = fsq.decode(indices2)

        torch.testing.assert_close(decoded1, decoded2)

    def test_fsq_device_compatibility(self, fsq):
        """Test FSQ works on different devices."""
        codes = torch.randn(1, 4, 10)

        # CPU
        fsq_cpu = fsq.to('cpu')
        codes_cpu = codes.to('cpu')
        indices_cpu = fsq_cpu.encode(codes_cpu)
        assert indices_cpu.device.type == 'cpu'

        # CUDA (if available)
        if torch.cuda.is_available():
            fsq_cuda = fsq.to('cuda')
            codes_cuda = codes.to('cuda')
            indices_cuda = fsq_cuda.encode(codes_cuda)
            assert indices_cuda.device.type == 'cuda'

    def test_fsq_gradient_flow(self, fsq):
        """Test gradients flow through FSQ (STE)."""
        inputs = torch.randn(1, 4, 10, requires_grad=True)

        # Forward pass (uses STE for gradients)
        quantized_codes, indices = fsq(inputs)

        # Compute loss and backprop
        loss = quantized_codes.sum()
        loss.backward()

        # Gradients should flow via straight-through estimator
        assert inputs.grad is not None


class TestGroupFiniteScalarQuantizer:
    """Test suite for Grouped FSQ module."""

    @pytest.fixture
    def quantizer(self):
        """Create a default GFSQ instance."""
        return GroupFiniteScalarQuantizer(
            num_groups=4,
            num_levels_per_group=[9, 8, 8, 7]
        )

    def test_quantizer_initialization(self, quantizer):
        """Test GFSQ initializes correctly."""
        assert isinstance(quantizer, GroupFiniteScalarQuantizer)
        assert quantizer.num_groups == 4
        assert len(quantizer.fsqs) == 4
        # Each FSQ has 4 dimensions (length of num_levels_per_group)
        assert quantizer.fsqs[0].dim == 4

    def test_quantizer_codebook_size(self, quantizer):
        """Test total codebook size calculation."""
        # Each group: 4032 codes
        # Total: 4032^4 ≈ 2.64 × 10^14
        expected = 4032 ** 4
        assert quantizer.codebook_size == expected

    def test_quantizer_encode_shape(self, quantizer):
        """Test GFSQ encoding produces correct shape."""
        batch_size = 2
        time_dim = 12
        codes = torch.randn(batch_size, 16, time_dim)  # 4 groups × 4 dims

        indices = quantizer.encode(codes)

        # Should output one index per group
        assert indices.shape == (batch_size, 4, time_dim)
        assert indices.dtype == torch.int32

    def test_quantizer_decode_shape(self, quantizer):
        """Test GFSQ decoding produces correct shape."""
        batch_size = 2
        time_dim = 12
        indices = torch.randint(0, 4032, (batch_size, 4, time_dim), dtype=torch.int32)

        codes = quantizer.decode(indices)

        # Should output 16-dimensional codes (4 groups × 4 dims)
        assert codes.shape == (batch_size, 16, time_dim)

    def test_quantizer_roundtrip(self, quantizer):
        """Test GFSQ encode-decode roundtrip."""
        codes = torch.randn(2, 16, 20)

        # Encode then decode
        indices = quantizer.encode(codes)
        reconstructed = quantizer.decode(indices)

        # Shape should match
        assert reconstructed.shape == codes.shape

        # Values should be close (with quantization error)
        assert (reconstructed - codes).abs().mean() < 1.0

    def test_quantizer_encode_output_range(self, quantizer):
        """Test GFSQ encode produces valid indices."""
        codes = torch.randn(2, 16, 20) * 5

        indices = quantizer.encode(codes)

        # Each group's indices should be within [0, 4032)
        assert indices.min() >= 0
        assert indices.max() < 4032

    def test_quantizer_deterministic(self, quantizer):
        """Test GFSQ is deterministic."""
        codes = torch.randn(1, 16, 10)

        # Encode twice
        indices1 = quantizer.encode(codes)
        indices2 = quantizer.encode(codes)

        torch.testing.assert_close(indices1, indices2)

        # Decode twice
        decoded1 = quantizer.decode(indices1)
        decoded2 = quantizer.decode(indices2)

        torch.testing.assert_close(decoded1, decoded2)

    def test_quantizer_device_compatibility(self, quantizer):
        """Test GFSQ works on different devices."""
        codes = torch.randn(1, 16, 10)

        # CPU
        quantizer_cpu = quantizer.to('cpu')
        codes_cpu = codes.to('cpu')
        indices_cpu = quantizer_cpu.encode(codes_cpu)
        assert indices_cpu.device.type == 'cpu'

        # CUDA (if available)
        if torch.cuda.is_available():
            quantizer_cuda = quantizer.to('cuda')
            codes_cuda = codes.to('cuda')
            indices_cuda = quantizer_cuda.encode(codes_cuda)
            assert indices_cuda.device.type == 'cuda'

        # MPS (if available)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            quantizer_mps = quantizer.to('mps')
            codes_mps = codes.to('mps')
            indices_mps = quantizer_mps.encode(codes_mps)
            assert indices_mps.device.type == 'mps'

    def test_quantizer_with_codes_len(self, quantizer):
        """Test GFSQ with explicit code lengths."""
        batch_size = 3
        max_time = 25

        codes = torch.randn(batch_size, 16, max_time)
        codes_len = torch.tensor([10, 15, 25])

        # Encode
        indices = quantizer.encode(codes, codes_len)

        assert indices.shape == (batch_size, 4, max_time)

        # Decode
        reconstructed = quantizer.decode(indices, codes_len)

        assert reconstructed.shape == codes.shape

    def test_quantizer_gradient_flow(self, quantizer):
        """Test gradients flow through GFSQ via individual FSQ forward passes."""
        inputs = torch.randn(1, 16, 10, requires_grad=True)

        # GFSQ's forward() uses encode/decode which breaks gradient chain (int32 tokens)
        # In actual training, gradients flow through: encoder → FSQ codes (STE) → decoder
        # Test that individual FSQ groups maintain gradients:
        batch, channels, time = inputs.shape
        channels_per_group = channels // quantizer.num_groups

        # Test first group's gradient flow
        group_input = inputs[:, :channels_per_group, :]
        codes, indices = quantizer.fsqs[0](group_input)

        loss = codes.sum()
        loss.backward()

        # Gradients should flow via straight-through estimator
        assert inputs.grad is not None
        assert not torch.isnan(inputs.grad).any()

    def test_quantizer_different_input_sizes(self, quantizer):
        """Test GFSQ with various input sizes."""
        test_sizes = [
            (1, 16, 5),
            (2, 16, 10),
            (4, 16, 20),
            (8, 16, 50)
        ]

        for batch, channels, time in test_sizes:
            codes = torch.randn(batch, channels, time)
            indices = quantizer.encode(codes)
            reconstructed = quantizer.decode(indices)

            assert indices.shape == (batch, 4, time)
            assert reconstructed.shape == codes.shape

    def test_quantizer_eval_mode(self, quantizer):
        """Test GFSQ behaves consistently in eval mode."""
        codes = torch.randn(1, 16, 10)

        quantizer.eval()
        with torch.no_grad():
            indices1 = quantizer.encode(codes)
            indices2 = quantizer.encode(codes)

        torch.testing.assert_close(indices1, indices2)

    def test_quantizer_custom_config(self):
        """Test GFSQ with custom configuration."""
        custom_quantizer = GroupFiniteScalarQuantizer(
            num_groups=2,
            num_levels_per_group=[8, 8]
        )

        codes = torch.randn(1, 4, 10)  # 2 groups × 2 dims
        indices = custom_quantizer.encode(codes)
        reconstructed = custom_quantizer.decode(indices)

        assert indices.shape == (1, 2, 10)
        assert reconstructed.shape == codes.shape
        assert custom_quantizer.codebook_size == (8 * 8) ** 2

    def test_quantizer_zero_input(self, quantizer):
        """Test GFSQ with zero input."""
        codes = torch.zeros(1, 16, 10)

        indices = quantizer.encode(codes)
        reconstructed = quantizer.decode(indices)

        # Should handle zeros gracefully
        assert not torch.isnan(indices).any()
        assert not torch.isnan(reconstructed).any()

    def test_quantizer_extreme_values(self, quantizer):
        """Test GFSQ with extreme input values."""
        # Very large values
        codes_large = torch.randn(1, 16, 10) * 100

        indices_large = quantizer.encode(codes_large)
        reconstructed_large = quantizer.decode(indices_large)

        # Should still produce valid outputs
        assert indices_large.min() >= 0
        assert indices_large.max() < 4032
        assert not torch.isnan(reconstructed_large).any()

    def test_quantizer_batch_independence(self, quantizer):
        """Test that batch items are processed independently."""
        batch_size = 4
        codes = torch.randn(batch_size, 16, 10)

        # Encode full batch
        indices_batch = quantizer.encode(codes)

        # Encode individually
        indices_individual = []
        for i in range(batch_size):
            idx = quantizer.encode(codes[i:i+1])
            indices_individual.append(idx)

        indices_individual = torch.cat(indices_individual, dim=0)

        # Should be identical
        torch.testing.assert_close(indices_batch, indices_individual)
