"""
Main AudioCodec model for PyTorch.
"""

import torch
import torch.nn as nn
from typing import Optional
import json

from .encoder import HiFiGANEncoder
from .decoder import CausalHiFiGANDecoder
from .quantizer_fixed import GroupFiniteScalarQuantizer
from ..utils import load_safetensors_weights


class AudioCodecModel(nn.Module):
    """
    NanoCodec Model in PyTorch.

    Combines encoder, quantizer, and decoder for audio compression.

    Args:
        sample_rate: Audio sample rate (22050 for nano-codec)
        encoder_config: Configuration dict for encoder
        decoder_config: Configuration dict for decoder
        quantizer_config: Configuration dict for quantizer
    """

    def __init__(
        self,
        sample_rate: int = 22050,
        encoder_config: Optional[dict] = None,
        decoder_config: Optional[dict] = None,
        quantizer_config: Optional[dict] = None,
    ):
        super().__init__()
        self.sample_rate = sample_rate

        # Default configurations matching nanocodec
        if encoder_config is None:
            encoder_config = {
                "down_sample_rates": [2, 3, 6, 7, 7],
                "encoded_dim": 16,
                "base_channels": 24,
                "activation": "lrelu",
                "pad_mode": "replicate",
            }

        if decoder_config is None:
            decoder_config = {
                "up_sample_rates": [7, 7, 6, 3, 2],
                "input_dim": 16,
                "base_channels": 864,
                "activation": "half_snake",
                "output_activation": "clamp",
                "pad_mode": "zeros",
                "n_groups_equal_to_out_channels": True,
            }

        if quantizer_config is None:
            quantizer_config = {
                "num_groups": 4,
                "num_levels_per_group": [9, 8, 8, 7],
            }

        self.audio_encoder = HiFiGANEncoder(**encoder_config)
        self.audio_decoder = CausalHiFiGANDecoder(**decoder_config)
        self.vector_quantizer = GroupFiniteScalarQuantizer(**quantizer_config)

        total_downsample = 1
        for rate in encoder_config["down_sample_rates"]:
            total_downsample *= rate
        self.samples_per_frame = total_downsample  # 1764 for nanocodec

    @torch.amp.autocast('cuda', enabled=False)  # Disable autocast for this method by default
    def encode(
        self,
        audio: torch.Tensor,
        audio_len: Optional[torch.Tensor] = None,
        use_amp: bool = False
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Encode audio to quantized tokens.

        Args:
            audio: Input audio [batch, time] or [batch, 1, time]
            audio_len: Length of each audio [batch]
            use_amp: Whether to use automatic mixed precision (default: False)

        Returns:
            tokens: Quantized token indices [batch, num_groups, time/downsample]
            tokens_len: Length of token sequence [batch]
        """
        if audio.ndim == 2:
            audio = audio.unsqueeze(1)  # [B, T] -> [B, 1, T]
        elif audio.ndim == 1:
            audio = audio.unsqueeze(0).unsqueeze(0)  # [T] -> [B, 1, T]

        if use_amp and audio.device.type == 'cuda':
            with torch.amp.autocast('cuda'):
                encoded, encoded_len = self.audio_encoder(audio, audio_len)
                tokens = self.vector_quantizer.encode(encoded, encoded_len)
        else:
            encoded, encoded_len = self.audio_encoder(audio, audio_len)
            tokens = self.vector_quantizer.encode(encoded, encoded_len)

        return tokens, encoded_len

    @torch.amp.autocast('cuda', enabled=False)  # Disable autocast for this method by default
    def decode(
        self,
        tokens: torch.Tensor,
        tokens_len: Optional[torch.Tensor] = None,
        use_amp: bool = False
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Decode quantized tokens to audio.

        Args:
            tokens: Quantized token indices [batch, num_groups, time]
            tokens_len: Length of token sequence [batch]
            use_amp: Whether to use automatic mixed precision (default: False)

        Returns:
            audio: Reconstructed audio [batch, 1, time * upsample]
            audio_len: Length of audio sequence [batch]
        """
        if use_amp and tokens.device.type == 'cuda':
            with torch.amp.autocast('cuda'):
                encoded = self.vector_quantizer.decode(tokens, tokens_len)
                audio, audio_len = self.audio_decoder(encoded, tokens_len)
        else:
            encoded = self.vector_quantizer.decode(tokens, tokens_len)
            audio, audio_len = self.audio_decoder(encoded, tokens_len)

        return audio, audio_len

    def forward(
        self,
        audio: torch.Tensor,
        audio_len: Optional[torch.Tensor] = None,
        use_amp: bool = False
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Full encode-decode pass (for validation/testing).

        Args:
            audio: Input audio [batch, time] or [batch, 1, time]
            audio_len: Length of each audio [batch]
            use_amp: Whether to use automatic mixed precision (default: False)

        Returns:
            reconstructed_audio: Reconstructed audio [batch, 1, time]
            tokens: Quantized tokens [batch, num_groups, time/downsample]
            audio_len: Length of output audio [batch]
        """
        tokens, tokens_len = self.encode(audio, audio_len, use_amp=use_amp)
        reconstructed_audio, audio_len = self.decode(tokens, tokens_len, use_amp=use_amp)

        return reconstructed_audio, tokens, audio_len

    @staticmethod
    def from_pretrained(
        weights_path: str,
        sample_rate: Optional[int] = None,
        device: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
        **kwargs
    ):
        """
        Load a pretrained model from HuggingFace Hub.

        Args:
            weights_path: Path to HuggingFace repo ID (e.g., "username/model-name")
            sample_rate: Audio sample rate (if None, will try to load from config)
            device: Device to load model on ('cpu', 'cuda', 'mps', or None for auto-detect)
            dtype: Data type for model parameters (e.g., torch.float32, torch.float16)
            **kwargs: Additional arguments passed to hf_hub_download

        Returns:
            model: Loaded AudioCodecModel instance

        Examples:
            # Load from HuggingFace Hub
            model = AudioCodecModel.from_pretrained("username/nanocodec-model")

            # Load on GPU with float16
            model = AudioCodecModel.from_pretrained("username/nanocodec-model",
                                                   device="cuda", dtype=torch.float16)
        """
        
        if '/' in weights_path:
            # This looks like a HuggingFace repo ID
            try:
                from huggingface_hub import hf_hub_download
            except ImportError:
                raise ImportError(
                    "huggingface_hub is required to download models from HuggingFace. "
                    "Install it with: pip install huggingface-hub"
                )

            print(f"Downloading model from HuggingFace Hub: {weights_path}")

            # Download config.json first to get sample_rate and model config
            config_path = None
            try:
                config_path = hf_hub_download(
                    repo_id=weights_path,
                    filename="config.json",
                    **kwargs
                )
            except Exception:
                print("Warning: config.json not found in repo, using defaults")

            # Download model.safetensors
            try:
                weights_file = hf_hub_download(
                    repo_id=weights_path,
                    filename="model.safetensors",
                    **kwargs
                )
            except Exception:
                # Fallback to .npz if safetensors not available
                print("model.safetensors not found, trying .npz format...")
                weights_file = hf_hub_download(
                    repo_id=weights_path,
                    filename="nemo_codec_weights.npz",
                    **kwargs
                )

            # Load config if available
            config = {}
            if config_path:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if sample_rate is None:
                        sample_rate = config.get('sample_rate', 22050)

            weights_path = weights_file

        # Default sample rate if not specified
        if sample_rate is None:
            sample_rate = 22050
            print(f"Using default sample_rate={sample_rate}")

        # Auto-detect device if not specified
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
            print(f"Auto-detected device: {device}")

        # Create model instance
        model = AudioCodecModel(sample_rate=sample_rate)

        # Load weights based on file extension
        if weights_path.endswith('.safetensors'):
            load_safetensors_weights(model, weights_path, device=device, verbose=True)
        else:
            raise ValueError(f"Unsupported weight format. Only .safetensors files are supported, got: {weights_path}")

        # Move model to specified device and dtype
        model = model.to(device)
        if dtype is not None:
            model = model.to(dtype)
            print(f"Converted model to dtype: {dtype}")

        return model

    def to_device(self, device: str):
        """
        Move model to specified device.

        Args:
            device: Target device ('cpu', 'cuda', 'cuda:0', 'mps', etc.)

        Returns:
            self for method chaining
        """
        return self.to(device)

    def get_device(self) -> torch.device:
        """
        Get the device the model is currently on.

        Returns:
            torch.device: The device of the model parameters
        """
        return next(self.parameters()).device

    def get_info(self) -> dict:
        """Get model information."""

        encoder_params = sum(p.numel() for p in self.audio_encoder.parameters())
        decoder_params = sum(p.numel() for p in self.audio_decoder.parameters())

        return {
            "sample_rate": self.sample_rate,
            "samples_per_frame": self.samples_per_frame,
            "encoder_params": encoder_params,
            "decoder_params": decoder_params,
            "quantizer_codebook_size": self.vector_quantizer.codebook_size,
            "device": str(self.get_device()),
        }

    def compile(
        self,
        mode: str = "default",
        fullgraph: bool = False,
        dynamic: bool = False,
        backend: str = "inductor"
    ):
        """
        Compile the model using torch.compile() for improved performance.

        This method compiles the encoder and decoder components separately for
        better optimization. Requires PyTorch 2.0+.

        Args:
            mode: Compilation mode - "default", "reduce-overhead", "max-autotune"
                  - "default": Balanced compilation for general use
                  - "reduce-overhead": Minimize Python overhead, best for small models
                  - "max-autotune": Aggressive optimization, longer compile time
            fullgraph: Whether to require full graph capture (may fail on complex graphs)
            dynamic: Whether to support dynamic shapes (can reduce optimization)
            backend: Compilation backend to use (default: "inductor")

        Returns:
            self for method chaining

        Examples:
            >>> model = AudioCodecModel.from_pretrained("username/model")
            >>> model.compile(mode="reduce-overhead")  # Compile for inference
            >>> model.eval()
            >>> tokens, tokens_len = model.encode(audio, audio_len)

        Note:
            - First inference after compilation will be slower due to compilation
            - Subsequent inferences will be significantly faster
            - Compilation is most beneficial for repeated inference on same input shapes
            - Not available on MPS backend (Apple Silicon), will fall back to eager mode
        """
        if not hasattr(torch, 'compile'):
            print("Warning: torch.compile() not available (requires PyTorch 2.0+)")
            return self

        device = self.get_device()
        if device.type == 'mps':
            print("Warning: torch.compile() not supported on MPS backend, using eager mode")
            return self

        print(f"Compiling model with mode='{mode}', backend='{backend}'...")
        print("Note: First inference will be slow due to compilation overhead")

        try:
            # Compile encoder
            self.audio_encoder = torch.compile(
                self.audio_encoder,
                mode=mode,
                fullgraph=fullgraph,
                dynamic=dynamic,
                backend=backend
            )

            # Compile decoder
            self.audio_decoder = torch.compile(
                self.audio_decoder,
                mode=mode,
                fullgraph=fullgraph,
                dynamic=dynamic,
                backend=backend
            )

            # Compile quantizer (simpler graph, safe to compile)
            self.vector_quantizer = torch.compile(
                self.vector_quantizer,
                mode=mode,
                fullgraph=fullgraph,
                dynamic=dynamic,
                backend=backend
            )

            print("✓ Model compilation successful")
        except Exception as e:
            print(f"Warning: Model compilation failed: {e}")
            print("Falling back to eager mode")

        return self
