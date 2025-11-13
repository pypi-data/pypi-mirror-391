"""
Convolutional layers for PyTorch NanoCodec.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Literal

from .activations import CodecActivation, HalfSnakeActivation


class Conv1dNorm(nn.Module):
    """
    Conv1D layer with custom padding support.

    Supports two padding strategies:
    - replicate: Symmetric padding (for encoder)
    - zeros: Causal padding (left-only, for decoder)

    PyTorch Conv1d natively uses [B, C, T] format, so no transpose needed.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride: int = 1,
        dilation: int = 1,
        padding_mode: Literal["replicate", "zeros"] = "replicate",
        padding: int = None,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation
        self.padding_mode = padding_mode

        if padding is not None:
            self.padding_left = padding
            self.padding_right = padding
        elif padding_mode == "zeros":
            # Causal: left-padding only
            total_padding = (kernel_size - 1) * dilation
            self.padding_left = total_padding
            self.padding_right = 0
        else:
            # Symmetric padding for replicate mode
            total_padding = (kernel_size - 1) * dilation
            self.padding_left = total_padding // 2
            self.padding_right = total_padding - self.padding_left

        self.conv = nn.Conv1d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=0,
            dilation=dilation,
        )

    def _apply_padding(self, x: torch.Tensor) -> torch.Tensor:
        """Apply custom padding based on padding_mode."""
        if self.padding_left == 0 and self.padding_right == 0:
            return x

        # PyTorch F.pad format for 3D tensor [B, C, T]: (left, right)
        if self.padding_mode == "replicate":
            return F.pad(x, (self.padding_left, self.padding_right), mode='replicate')
        else:  # zeros
            return F.pad(x, (self.padding_left, self.padding_right), mode='constant', value=0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # PyTorch Conv1d expects [B, C, T] format natively
        x = self._apply_padding(x)
        x = self.conv(x)
        return x


class ResidualBlock(nn.Module):
    """
    Residual block with dilated convolutions used in HiFiGAN encoder/decoder.

    For decoder (padding_mode="zeros"), uses HalfSnakeActivation.
    For encoder (padding_mode="replicate"), uses CodecActivation (LeakyReLU).

    Architecture: x → Activation → Conv(dilation) → Activation → Conv(dilation=1) → Add(x)
    """

    def __init__(
        self,
        channels: int,
        kernel_size: int,
        dilation: int = 1,
        padding_mode: Literal["replicate", "zeros"] = "replicate",
        dropout: float = 0.0,
    ):
        super().__init__()
        self.channels = channels
        self.dropout_p = dropout

        if padding_mode == "zeros":
            self.input_activation = HalfSnakeActivation(channels)
            self.skip_activation = HalfSnakeActivation(channels)
        else:
            self.input_activation = CodecActivation()
            self.skip_activation = CodecActivation()

        self.input_conv = Conv1dNorm(
            channels,
            channels,
            kernel_size,
            dilation=dilation,
            padding_mode=padding_mode,
        )

        self.skip_conv = Conv1dNorm(
            channels,
            channels,
            kernel_size,
            dilation=1,
            padding_mode=padding_mode,
        )

        if dropout > 0:
            self.dropout = nn.Dropout(p=dropout)
        else:
            self.dropout = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        original_size = x.shape[2]
        out = self.input_activation(x)
        out = self.input_conv(out)
        out = self.skip_activation(out)
        out = self.skip_conv(out)

        # Handle size mismatch (shouldn't happen with proper padding, but safety check)
        if out.shape[2] != original_size:
            if out.shape[2] > original_size:
                out = out[:, :, :original_size]
            else:
                pad_amount = original_size - out.shape[2]
                out = F.pad(out, (0, pad_amount))

        if self.dropout is not None:
            out = self.dropout(out)

        return x + out


class HiFiGANResBlock(nn.Module):
    """
    HiFiGAN residual block containing multiple residual blocks with different dilations.

    Sequential application of residual blocks with dilations [1, 3, 5].
    """

    def __init__(
        self,
        channels: int,
        kernel_size: int,
        dilations: list[int],
        padding_mode: Literal["replicate", "zeros"] = "replicate",
    ):
        super().__init__()
        # Use ModuleList for proper parameter registration
        self.res_blocks = nn.ModuleList([
            ResidualBlock(channels, kernel_size, dilation, padding_mode)
            for dilation in dilations
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for block in self.res_blocks:
            x = block(x)
        return x


class HiFiGANResLayer(nn.Module):
    """
    Layer containing multiple HiFiGAN residual blocks with different kernel sizes.

    Parallel processing with kernel sizes [3, 7, 11], then averages the outputs.
    This provides multi-scale receptive field processing.
    """

    def __init__(
        self,
        channels: int,
        kernel_sizes: list[int] = [3, 7, 11],
        dilations: list[int] = [1, 3, 5],
        padding_mode: Literal["replicate", "zeros"] = "replicate",
    ):
        super().__init__()
        # Use ModuleList for proper parameter registration
        self.res_blocks = nn.ModuleList([
            HiFiGANResBlock(channels, kernel_size, dilations, padding_mode)
            for kernel_size in kernel_sizes
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Process through parallel paths with different kernel sizes
        residuals = []
        for block in self.res_blocks:
            res = block(x)
            residuals.append(res)

        # Average all parallel paths
        out = torch.stack(residuals, dim=0).mean(dim=0)
        return out
