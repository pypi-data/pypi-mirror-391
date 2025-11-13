"""
HiFiGAN Encoder implementation in PyTorch.
"""

import torch
import torch.nn as nn
from typing import Optional

from ..layers import Conv1dNorm, HiFiGANResLayer, CodecActivation


class HiFiGANEncoder(nn.Module):
    """
    HiFiGAN-based audio encoder with multi-scale residual processing.

    Compresses audio through 5 downsampling stages with strided convolutions,
    achieving 1764x compression (2×3×6×7×7).

    Args:
        down_sample_rates: List of downsampling rates for each layer [2, 3, 6, 7, 7]
        encoded_dim: Output dimension (16 for nanocodec)
        base_channels: Base number of channels (24 for nanocodec)
        activation: Activation function type ('lrelu')
        pad_mode: Padding mode ('replicate' for encoder)
    """

    def __init__(
        self,
        down_sample_rates: list[int] = [2, 3, 6, 7, 7],
        encoded_dim: int = 16,
        base_channels: int = 24,
        activation: str = "lrelu",
        pad_mode: str = "replicate",
    ):
        super().__init__()
        self.down_sample_rates = down_sample_rates
        self.encoded_dim = encoded_dim
        self.base_channels = base_channels

        # Pre-convolution: 1 → base_channels (24)
        self.pre_conv = Conv1dNorm(
            in_channels=1,
            out_channels=base_channels,
            kernel_size=7,
            stride=1,
            padding_mode=pad_mode,
            padding=3,
        )

        # Activations for each downsampling stage
        self.activations = nn.ModuleList([
            CodecActivation() for _ in range(len(down_sample_rates))
        ])

        # Padding values for downsampling convolutions
        # Strides: [2, 3, 6, 7, 7] → Padding: [1, 2, 3, 4, 4]
        pytorch_padding = [1, 2, 3, 4, 4]

        # Downsampling convolution layers
        self.down_sample_conv_layers = nn.ModuleList()
        in_ch = base_channels
        for i, rate in enumerate(down_sample_rates):
            out_ch = in_ch * 2
            # Kernel size is 2× stride
            if rate == 2:
                kernel_size = 4
            elif rate == 3:
                kernel_size = 6
            elif rate == 6:
                kernel_size = 12
            elif rate == 7:
                kernel_size = 14
            else:
                kernel_size = rate * 2

            self.down_sample_conv_layers.append(
                Conv1dNorm(
                    in_channels=in_ch,
                    out_channels=out_ch,
                    kernel_size=kernel_size,
                    stride=rate,
                    padding_mode=pad_mode,
                    padding=pytorch_padding[i],
                )
            )
            in_ch = out_ch

        # Residual layers (before each downsampling)
        self.res_layers = nn.ModuleList()
        in_ch = base_channels
        for i, rate in enumerate(down_sample_rates):
            self.res_layers.append(
                HiFiGANResLayer(
                    channels=in_ch,
                    kernel_sizes=[3, 7, 11],
                    dilations=[1, 3, 5],
                    padding_mode=pad_mode,
                )
            )
            in_ch = in_ch * 2

        # Final processing
        self.final_activation = CodecActivation()
        final_channels = base_channels * (2 ** len(down_sample_rates))
        self.post_conv = Conv1dNorm(
            in_channels=final_channels,
            out_channels=encoded_dim,
            kernel_size=7,
            stride=1,
            padding_mode=pad_mode,
            padding=3,
        )

        # Pre-calculate total downsampling factor for efficiency
        self.total_downsample = 1
        for rate in down_sample_rates:
            self.total_downsample *= rate

    def forward(
        self,
        x: torch.Tensor,
        audio_len: Optional[torch.Tensor] = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Encode audio to latent representation.

        Args:
            x: Input audio [batch, channels, time] or [batch, time]
            audio_len: Length of each audio in batch [batch]

        Returns:
            encoded: Encoded representation [batch, encoded_dim, time/downsample_factor]
            encoded_len: Length of encoded sequence [batch]
        """
        # Ensure input is [B, C, T]
        if x.ndim == 2:
            x = x.unsqueeze(1)

        # Pre-convolution
        x = self.pre_conv(x)

        # Process through downsampling stages
        # Each stage: ResLayer → Activation → DownsampleConv
        for res_layer, activation, down_conv in zip(
            self.res_layers,
            self.activations,
            self.down_sample_conv_layers
        ):
            x = res_layer(x)
            x = activation(x)
            x = down_conv(x)

        # Final processing
        x = self.final_activation(x)
        x = self.post_conv(x)

        # Calculate encoded length using pre-computed total_downsample
        if audio_len is not None:
            encoded_len = audio_len // self.total_downsample
        else:
            encoded_len = torch.tensor([x.shape[2]] * x.shape[0], device=x.device, dtype=torch.int32)

        return x, encoded_len
