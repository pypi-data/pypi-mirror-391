"""
Activation functions for PyTorch NanoCodec.
"""

import torch
import torch.nn as nn


class CodecActivation(nn.Module):
    """Simple wrapper for LeakyReLU activation used in encoder."""

    def __init__(self, negative_slope: float = 0.01):
        super().__init__()
        self.activation = nn.LeakyReLU(negative_slope=negative_slope)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.activation(x)


class SnakeActivation(nn.Module):
    """
    Snake activation function: x + (1/alpha) * sin(alpha * x)^2
    """

    def __init__(self, channels: int, alpha_init: float = 1.0):
        super().__init__()
        # Register alpha as a learnable parameter
        self.alpha = nn.Parameter(torch.ones(1, channels, 1) * alpha_init)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        sin_term = torch.sin(self.alpha * x)
        return x + (1.0 / self.alpha) * sin_term ** 2


class HalfSnakeActivation(nn.Module):
    """
    Half-Snake activation: combines Snake with LeakyReLU.
    Split channels: first half uses Snake, second half uses LeakyReLU.
    """

    def __init__(self, channels: int, alpha_init: float = 1.0, negative_slope: float = 0.01):
        super().__init__()
        self.channels = channels
        self.split_point = channels // 2
        # Register alpha as a learnable parameter for first half of channels
        self.alpha = nn.Parameter(torch.ones(1, self.split_point, 1) * alpha_init)
        self.leaky_relu = nn.LeakyReLU(negative_slope=negative_slope)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Split channels in half
        x1 = x[:, :self.split_point, :]
        x2 = x[:, self.split_point:, :]

        # First half: Snake activation
        sin_term = torch.sin(self.alpha * x1)
        x1_out = x1 + (1.0 / self.alpha) * sin_term ** 2

        # Second half: LeakyReLU
        x2_out = self.leaky_relu(x2)

        # Concatenate along channel dimension
        return torch.cat([x1_out, x2_out], dim=1)
