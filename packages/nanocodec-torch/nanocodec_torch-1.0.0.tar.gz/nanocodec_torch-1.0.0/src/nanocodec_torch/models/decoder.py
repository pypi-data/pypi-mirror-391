"""
Causal HiFiGAN Decoder implementation in PyTorch.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

from ..layers import Conv1dNorm, HiFiGANResLayer
from ..layers.activations import HalfSnakeActivation


class CausalConv1d(nn.Module):
    """
    Causal Conv1D layer for streaming applications.
    Uses left-padding only for causal processing.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride: int = 1,
        dilation: int = 1,
    ):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation
        self.padding = (kernel_size - 1) * dilation

        self.conv = nn.Conv1d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=0,
            dilation=dilation,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # PyTorch Conv1d expects [B, C, T] format natively - NO TRANSPOSES
        if self.padding > 0:
            # Causal padding: left-pad only
            x = F.pad(x, (self.padding, 0), mode='constant', value=0)

        x = self.conv(x)
        return x


class CausalConvTranspose1d(nn.Module):
    """
    Causal grouped transposed convolution for upsampling.

    NanoCodec uses groups=out_channels, meaning each output channel
    is produced by a separate group with in_channels/out_channels inputs.

    Implementation: Upsample by inserting zeros, then apply grouped convolution
    with flipped kernels (equivalent to transposed convolution but causal).
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride: int = 1,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.groups = out_channels  # NanoCodec pattern: groups = out_channels
        self.trim = kernel_size - stride
        self.channels_per_group = in_channels // out_channels
        assert self.channels_per_group * out_channels == in_channels, \
            f"in_channels ({in_channels}) must be divisible by out_channels ({out_channels})"

        # Weight and bias will be loaded from pretrained model
        # Shape: [in_channels, kernel_size, 1] reshaped to [groups, channels_per_group, kernel_size, 1]
        self.register_parameter(
            'weight',
            nn.Parameter(torch.zeros(in_channels, kernel_size, 1))
        )
        self.register_parameter(
            'bias',
            nn.Parameter(torch.zeros(out_channels))
        )

    def _upsample_with_zeros(self, x: torch.Tensor, stride: int) -> torch.Tensor:
        """
        Upsample by inserting (stride-1) zeros between samples.

        Args:
            x: Input [batch, channels, time]
            stride: Upsampling factor

        Returns:
            Upsampled tensor [batch, channels, upsampled_time]
        """
        if stride == 1:
            return x

        batch, channels, time = x.shape
        # Create output tensor with zeros
        upsampled_time = time + (time - 1) * (stride - 1)
        output = torch.zeros(batch, channels, upsampled_time, device=x.device, dtype=x.dtype)

        # Place original samples at strided positions
        output[:, :, ::stride] = x

        return output

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Apply grouped transposed convolution.

        Args:
            x: Input tensor [batch, in_channels, time]

        Returns:
            Output tensor [batch, out_channels, upsampled_time]
        """
        batch, in_ch, time = x.shape
        assert in_ch == self.in_channels, f"Expected {self.in_channels} input channels, got {in_ch}"

        # Reshape for grouped processing: [B, groups, channels_per_group, T]
        x_grouped = x.view(batch, self.groups, self.channels_per_group, time)

        # Reshape weight: [groups, channels_per_group, kernel_size]
        weight_grouped = self.weight.view(self.groups, self.channels_per_group, self.kernel_size)

        # Flip kernel for transposed convolution (reverse along kernel dimension)
        weight_flipped = torch.flip(weight_grouped, dims=[2])

        # Process each group separately to minimize peak memory
        output_list = []
        for g in range(self.groups):
            x_g = x_grouped[:, g, :, :]  # [B, channels_per_group, T]

            # Upsample by inserting zeros
            x_up = self._upsample_with_zeros(x_g, self.stride)

            # Apply symmetric padding for convolution
            padding = self.kernel_size - 1
            if padding > 0:
                x_up = F.pad(x_up, (padding, padding), mode='constant', value=0)

            # Apply grouped convolution with flipped weights
            # PyTorch Conv1d expects: input [B, C_in, T], weight [C_out, C_in, K]
            # For our case: C_out = 1 (each group produces 1 output channel)
            w_g = weight_flipped[g].unsqueeze(0)  # [1, channels_per_group, kernel_size]
            y_g = F.conv1d(x_up, w_g, stride=1, padding=0)  # [B, 1, T']

            output_list.append(y_g)

        # Concatenate all groups: [B, groups, T'] -> [B, out_channels, T']
        output = torch.cat(output_list, dim=1)

        # Add bias
        output = output + self.bias.view(1, self.out_channels, 1)

        # Trim output to match expected causal length
        if self.trim > 0 and output.shape[2] > self.trim:
            output = output[:, :, :-self.trim]

        return output


class CausalHiFiGANDecoder(nn.Module):
    """
    Causal HiFiGAN decoder for audio reconstruction.

    Args:
        up_sample_rates: List of upsampling rates [7, 7, 6, 3, 2]
        input_dim: Input dimension (16 for nanocodec)
        base_channels: Base number of channels (864 for nanocodec)
        activation: Activation function ('half_snake')
        output_activation: Output activation ('clamp')
        pad_mode: Padding mode ('zeros' for causal)
        n_groups_equal_to_out_channels: Use group norm with groups=channels
    """

    def __init__(
        self,
        up_sample_rates: list[int] = [7, 7, 6, 3, 2],
        input_dim: int = 16,
        base_channels: int = 864,
        activation: str = "half_snake",
        output_activation: str = "clamp",
        pad_mode: str = "zeros",
        n_groups_equal_to_out_channels: bool = True,
    ):
        super().__init__()
        self.up_sample_rates = up_sample_rates
        self.input_dim = input_dim
        self.base_channels = base_channels
        self.output_activation_type = output_activation

        self.pre_conv = CausalConv1d(
            in_channels=input_dim,
            out_channels=base_channels,
            kernel_size=7,
            stride=1,
        )

        # Use ModuleLists for proper parameter registration
        self.up_sample_conv_layers = nn.ModuleList()
        self.activations = nn.ModuleList()
        self.res_layers = nn.ModuleList()
        in_ch = base_channels

        for i, rate in enumerate(up_sample_rates):
            out_ch = in_ch // 2

            if activation == "half_snake":
                self.activations.append(HalfSnakeActivation(in_ch))
            else:
                from ..layers import CodecActivation
                self.activations.append(CodecActivation())

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

            self.up_sample_conv_layers.append(
                CausalConvTranspose1d(
                    in_channels=in_ch,
                    out_channels=out_ch,
                    kernel_size=kernel_size,
                    stride=rate,
                )
            )

            self.res_layers.append(
                HiFiGANResLayer(
                    channels=out_ch,
                    kernel_sizes=[3, 7, 11],
                    dilations=[1, 3, 5],
                    padding_mode=pad_mode,
                )
            )

            in_ch = out_ch

        if activation == "half_snake":
            self.post_activation = HalfSnakeActivation(in_ch)
        else:
            from ..layers import CodecActivation
            self.post_activation = CodecActivation()

        self.post_conv = CausalConv1d(
            in_channels=in_ch,
            out_channels=1,
            kernel_size=3,
            stride=1,
        )

        # Pre-calculate total upsampling factor for efficiency
        self.total_upsample = 1
        for rate in up_sample_rates:
            self.total_upsample *= rate

    def forward(
        self,
        x: torch.Tensor,
        tokens_len: Optional[torch.Tensor] = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Decode latent representation to audio.

        Args:
            x: Encoded representation [batch, input_dim, time]
            tokens_len: Length of encoded sequence [batch]

        Returns:
            audio: Reconstructed audio [batch, 1, time * upsample_factor]
            audio_len: Length of audio sequence [batch]
        """
        x = self.pre_conv(x)

        for activation, up_layer, res_layer in zip(
            self.activations, self.up_sample_conv_layers, self.res_layers
        ):
            x = activation(x)
            x = up_layer(x)
            x = res_layer(x)

        x = self.post_activation(x)
        x = self.post_conv(x)

        # Apply output activation
        if self.output_activation_type == "clamp":
            x = torch.clamp(x, -1.0, 1.0)
        elif self.output_activation_type == "tanh":
            x = torch.tanh(x)

        # Calculate output audio length using pre-computed total_upsample
        if tokens_len is not None:
            audio_len = tokens_len * self.total_upsample
        else:
            audio_len = torch.tensor([x.shape[2]] * x.shape[0], device=x.device, dtype=torch.int32)

        return x, audio_len
