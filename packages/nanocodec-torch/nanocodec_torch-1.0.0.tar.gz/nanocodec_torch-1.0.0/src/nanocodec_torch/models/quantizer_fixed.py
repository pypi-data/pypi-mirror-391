"""
Finite Scalar Quantizer (FSQ) implementation in PyTorch.

Based on https://arxiv.org/abs/2309.15505v1
"""

import torch
import torch.nn as nn
from typing import Optional


class RoundSTE(torch.autograd.Function):
    """
    Straight-Through Estimator for rounding operation.
    Forward: round to nearest integer
    Backward: pass gradient through unchanged (identity)
    """
    @staticmethod
    def forward(ctx, x):
        return torch.round(x)

    @staticmethod
    def backward(ctx, grad_output):
        # Straight-through: gradient passes unchanged
        return grad_output


class FiniteScalarQuantizer(nn.Module):
    """
    Finite Scalar Quantization for a single group.

    Implements FSQ algorithm with tanh-based compression and rounding
    with straight-through gradient estimation.

    Args:
        num_levels: List of quantization levels per dimension, e.g., [9, 8, 8, 7]
        eps: Small regularization constant for compression (default: 1e-3)
    """

    def __init__(self, num_levels: list[int], eps: float = 1e-3):
        super().__init__()

        self.dim = len(num_levels)
        self.eps = eps

        # Register as buffers (non-learnable, but part of state_dict)
        self.register_buffer('num_levels', torch.tensor(num_levels, dtype=torch.int32))

        # Example: [9, 8, 8, 7] -> [1, 9, 72, 576]
        base_indices = [1]
        for i in range(len(num_levels) - 1):
            base_indices.append(base_indices[-1] * num_levels[i])
        self.register_buffer('dim_base_index', torch.tensor(base_indices, dtype=torch.int32))

        self.codebook_size = int(torch.prod(self.num_levels).item())

    def compress(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Apply tanh-based compression to limit values.

        Args:
            inputs: Input tensor [B, D, T]

        Returns:
            Compressed output [B, D, T]
        """
        num_levels = self.num_levels[None, :, None].float()
        output_scale = (num_levels - 1) / 2
        output_scale = output_scale * (1 - self.eps)
        output_offset = torch.where(self.num_levels[None, :, None] % 2 == 0, 0.5, 0.0)
        input_shift = torch.tan(output_offset / output_scale)
        compressed = output_scale * torch.tanh(inputs + input_shift) - output_offset

        return compressed

    def round_ste(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Round to nearest integer with straight-through estimator.

        Args:
            inputs: Input tensor [B, D, T]

        Returns:
            Rounded tensor [B, D, T]
        """
        return RoundSTE.apply(inputs)

    def inputs_to_codes(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Convert continuous inputs to quantized codes in [-1, 1] range.

        Args:
            inputs: Input tensor [B, D, T]

        Returns:
            Quantized codes [B, D, T] with values in [-1, 1]
        """
        compressed = self.compress(inputs)
        codes_int = self.round_ste(compressed)
        scale = (self.num_levels[None, :, None] // 2).float()
        codes = codes_int / scale

        return codes

    def codes_to_nonnegative(self, codes: torch.Tensor) -> torch.Tensor:
        """
        Convert codes centered around zero to nonnegative indices.

        Args:
            codes: Code tensor [B, D, T] with values in [-1, 1]

        Returns:
            Nonnegative indices [B, D, T] with values in [0, num_levels-1]
        """
        scale = offset = (self.num_levels[None, :, None] // 2).float()
        return scale * codes + offset

    def nonnegative_to_codes(self, codes_nonnegative: torch.Tensor) -> torch.Tensor:
        """
        Convert nonnegative indices to codes centered around zero.

        Args:
            codes_nonnegative: Nonnegative indices [B, D, T] in [0, num_levels-1]

        Returns:
            Codes [B, D, T] with values in [-1, 1]
        """
        scale = offset = (self.num_levels[None, :, None] // 2).float()
        return (codes_nonnegative - offset) / scale

    def codes_to_indices(self, codes: torch.Tensor) -> torch.Tensor:
        """
        Convert code vectors to flat indices.

        Args:
            codes: Code tensor [B, D, T] with values in [-1, 1]

        Returns:
            Flat indices [B, T] with values in [0, codebook_size-1]
        """
        indices_per_dim = self.codes_to_nonnegative(codes)
        dim_base = self.dim_base_index[None, :, None].float()
        flat_indices = torch.sum(indices_per_dim * dim_base, dim=1)

        return flat_indices.to(torch.int32)

    def indices_to_codes(self, indices: torch.Tensor) -> torch.Tensor:
        """
        Convert flat indices to code vectors.

        Args:
            indices: Flat indices [B, T] with values in [0, codebook_size-1]

        Returns:
            Codes [B, D, T] with values in [-1, 1]
        """
        indices_expanded = indices[:, None, :]  # [B, 1, T]
        dim_base = self.dim_base_index[None, :, None].to(torch.int32)
        num_levels = self.num_levels[None, :, None]
        codes_nonnegative = (indices_expanded // dim_base) % num_levels
        codes = self.nonnegative_to_codes(codes_nonnegative.float())

        return codes

    def encode(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Encode continuous inputs to discrete indices.

        Args:
            inputs: Input tensor [B, D, T]

        Returns:
            Flat indices [B, T] with values in [0, codebook_size-1]
        """
        codes = self.inputs_to_codes(inputs)
        indices = self.codes_to_indices(codes)

        return indices

    def decode(self, indices: torch.Tensor) -> torch.Tensor:
        """
        Decode discrete indices to continuous codes.

        Args:
            indices: Flat indices [B, T] with values in [0, codebook_size-1]

        Returns:
            Dequantized codes [B, D, T] with values in [-1, 1]
        """
        codes = self.indices_to_codes(indices)
        return codes

    def forward(self, inputs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize and return both codes and indices.

        Args:
            inputs: Input tensor [B, D, T]

        Returns:
            codes: Quantized codes [B, D, T]
            indices: Flat indices [B, T]
        """
        codes = self.inputs_to_codes(inputs)
        indices = self.codes_to_indices(codes)
        return codes, indices


class GroupFiniteScalarQuantizer(nn.Module):
    """
    Grouped Finite Scalar Quantization.

    Splits input channels into groups and applies FSQ to each group independently.

    Args:
        num_groups: Number of groups (4 for nanocodec)
        num_levels_per_group: List of levels for each dimension within a group
                              E.g., [9, 8, 8, 7] means each group has 4 dimensions
    """

    def __init__(
        self,
        num_groups: int = 4,
        num_levels_per_group: list[int] = [9, 8, 8, 7],
    ):
        super().__init__()
        self.num_groups = num_groups
        self.num_levels_per_group = num_levels_per_group

        # Use ModuleList for proper parameter registration
        self.fsqs = nn.ModuleList([
            FiniteScalarQuantizer(num_levels=num_levels_per_group)
            for _ in range(num_groups)
        ])

        fsq_codebook_size = 1
        for levels in num_levels_per_group:
            fsq_codebook_size *= levels
        self.codebook_size = fsq_codebook_size ** num_groups

    def encode(self, x: torch.Tensor, input_len: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Encode input to quantized indices.

        Args:
            x: Input tensor [B, C, T]
            input_len: Optional length tensor [B] (not used in inference)

        Returns:
            tokens: Quantized token indices [B, num_groups, T]
        """
        batch, channels, time = x.shape
        channels_per_group = channels // self.num_groups
        all_indices = []
        for i in range(self.num_groups):
            start_idx = i * channels_per_group
            end_idx = start_idx + channels_per_group
            group_input = x[:, start_idx:end_idx, :]  # [B, channels_per_group, T]
            indices = self.fsqs[i].encode(group_input)  # [B, T]
            all_indices.append(indices)

        # Stack to [B, num_groups, T]
        tokens = torch.stack(all_indices, dim=1)

        return tokens

    def decode(self, tokens: torch.Tensor, input_len: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Decode quantized indices back to continuous values.

        Args:
            tokens: Quantized token indices [B, num_groups, T]
            input_len: Optional length tensor [B] (not used in inference)

        Returns:
            x: Dequantized tensor [B, C, T]
        """
        batch, num_groups, time = tokens.shape
        assert num_groups == self.num_groups
        channels_per_group = len(self.num_levels_per_group)
        all_groups = []
        for i in range(self.num_groups):
            group_indices = tokens[:, i, :]  # [B, T]
            group_codes = self.fsqs[i].decode(group_indices)  # [B, D, T]
            all_groups.append(group_codes)

        x = torch.cat(all_groups, dim=1)  # [B, C, T]

        return x

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize and dequantize in one pass.

        Args:
            x: Input tensor [B, C, T]

        Returns:
            tokens: Quantized token indices [B, num_groups, T]
            x_quantized: Dequantized tensor [B, C, T]
        """
        tokens = self.encode(x)
        x_quantized = self.decode(tokens)

        return tokens, x_quantized
