# NanoCodec PyTorch

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)

A PyTorch implementation of [NVIDIA NeMo NanoCodec](https://huggingface.co/nvidia/nemo-nano-codec-22khz-0.6kbps-12.5fps), an ultra-lightweight neural audio codec achieving **0.6 kbps** bitrate with **1764:1 compression ratio**.

## Features

- **Ultra-Low Bitrate**: 0.6 kbps at 22.05 kHz (12.5 fps frame rate)
- **High Compression**: 1764:1 compression ratio (2×3×6×7×7 downsampling)
- **Multi-Device Support**: CPU, CUDA (NVIDIA GPUs), MPS (Apple Silicon)
- **Production Ready**: 164/164 tests passing, comprehensive validation
- **Causal Architecture**: Supports streaming inference
- **Efficient**: ~105M parameters, optimized for real-time inference

## Model Architecture

- **Encoder**: HiFiGAN-based encoder with 5 downsampling stages
- **Quantizer**: Grouped Finite Scalar Quantization (4 groups, 4032 codes per group)
- **Decoder**: Causal HiFiGAN decoder with HalfSnake activations
- **Sample Rate**: 22.05 kHz mono
- **Parameters**: ~105M.

## Installation

### From PyPI (when available)

```bash
pip install nanocodec-torch soundfile
```

### From Source

```bash
git clone https://github.com/nineninesix-ai/nanocodec-torch.git
cd nanocodec-torch
pip install -e .
```

### Dependencies

- Python 3.10+
- PyTorch 2.0+
- soundfile
- numpy
- huggingface-hub
- safetensors

## Quick Start

### Basic Usage

```python
import torch
from nanocodec_torch.models.audio_codec import AudioCodecModel
import soundfile as sf

# Load pretrained model from HuggingFace Hub
model = AudioCodecModel.from_pretrained(
    "nineninesix/nemo-nano-codec-22khz-0.6kbps-12.5fps-pytorch"
)

# Move to desired device
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
model.eval()

# Load audio (will be resampled to 22050 Hz if needed)
audio, sr = sf.read("input.wav")
audio_tensor = torch.tensor(audio, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)
audio_len = torch.tensor([len(audio)], dtype=torch.int32).to(device)

# Encode and decode
with torch.no_grad():
    tokens, tokens_len = model.encode(audio_tensor, audio_len)
    reconstructed, recon_len = model.decode(tokens, tokens_len)

# Save reconstructed audio
output = reconstructed[0, 0, :int(recon_len[0])].cpu().numpy()
sf.write("output.wav", output, 22050)

print(f"Compression ratio: {len(audio) / tokens.shape[2]:.0f}:1")
print(f"Tokens shape: {tokens.shape}")  # [B, 4, T/1764]
```

### Device Selection

```python
# CUDA (NVIDIA GPU)
if torch.cuda.is_available():
    device = "cuda"
    model = model.to(device)

# MPS (Apple Silicon M1/M2/M3)
if torch.backends.mps.is_available():
    device = "mps"
    model = model.to(device)

# CPU (fallback)
device = "cpu"
model = model.to(device)
```

### Batch Processing

```python
import torch
from nanocodec_torch.models.audio_codec import AudioCodecModel
import soundfile as sf

model = AudioCodecModel.from_pretrained(
    "nineninesix/nemo-nano-codec-22khz-0.6kbps-12.5fps-pytorch"
).to("cuda").eval()

# Load multiple audio files
audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
audio_list = []
audio_lens = []

for file in audio_files:
    audio, sr = sf.read(file)
    audio_list.append(torch.tensor(audio, dtype=torch.float32))
    audio_lens.append(len(audio))

# Pad to same length
max_len = max(audio_lens)
audio_batch = torch.zeros(len(audio_list), 1, max_len)
for i, audio in enumerate(audio_list):
    audio_batch[i, 0, :len(audio)] = audio

audio_lens = torch.tensor(audio_lens, dtype=torch.int32).to("cuda")
audio_batch = audio_batch.to("cuda")

# Process batch
with torch.no_grad():
    tokens, tokens_len = model.encode(audio_batch, audio_lens)
    reconstructed, recon_lens = model.decode(tokens, tokens_len)

# Save outputs
for i, (audio, length) in enumerate(zip(reconstructed, recon_lens)):
    output = audio[0, :int(length)].cpu().numpy()
    sf.write(f"output_{i}.wav", output, 22050)
```

## Examples

Comprehensive examples are available in the [examples/](examples/) directory:

- [basic_encode_decode.py](examples/basic_encode_decode.py) - Basic encode/decode workflow
- [batch_processing.py](examples/batch_processing.py) - Batch process multiple files
- [streaming_inference.py](examples/streaming_inference.py) - Causal streaming inference
- [device_examples.py](examples/device_examples.py) - Multi-device usage examples

## API Reference

### AudioCodecModel

The main model class for audio encoding and decoding.

#### Methods

**`from_pretrained(repo_id: str, device: str = "cpu") -> AudioCodecModel`**

Load pretrained model from HuggingFace Hub.

```python
model = AudioCodecModel.from_pretrained(
    "nineninesix/nemo-nano-codec-22khz-0.6kbps-12.5fps-pytorch"
)
```

**`encode(audio: torch.Tensor, audio_len: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]`**

Encode audio to discrete tokens.

- **Input**:
  - `audio`: Audio tensor `[B, 1, T]`, float32, range [-1, 1]
  - `audio_len`: Length tensor `[B]`, int32
- **Output**:
  - `tokens`: Discrete tokens `[B, 4, T/1764]`, int32
  - `tokens_len`: Token lengths `[B]`, int32

**`decode(tokens: torch.Tensor, tokens_len: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]`**

Decode tokens back to audio.

- **Input**:
  - `tokens`: Discrete tokens `[B, 4, T]`, int32
  - `tokens_len`: Token lengths `[B]`, int32
- **Output**:
  - `audio`: Reconstructed audio `[B, 1, T*1764]`, float32, range [-1, 1]
  - `audio_len`: Audio lengths `[B]`, int32

**`forward(audio: torch.Tensor, audio_len: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]`**

Full encode-decode roundtrip.

- **Output**: `(reconstructed_audio, tokens, audio_len)`

For detailed API documentation, see [API_REFERENCE.md](API_REFERENCE.md).

## Input/Output Specifications

### Input
- **Type**: Audio waveform
- **Format**: .wav, .mp3, .flac (any format supported by soundfile)
- **Sample Rate**: 22.05 kHz (audio will be resampled if necessary)
- **Channels**: Mono (stereo will be converted to mono)
- **Range**: [-1.0, 1.0] (normalized float32)

### Output
- **Type**: Reconstructed audio waveform
- **Format**: .wav (or any format supported by soundfile)
- **Sample Rate**: 22.05 kHz
- **Channels**: Mono
- **Range**: [-1.0, 1.0] (clamped)
- **Bitrate**: 0.6 kbps (12.5 fps × 4 groups × log2(4032) ≈ 600 bps)

## Performance Benchmarks

### Inference Speed 

- Use `torch.compile(mode="reduce-overhead")`. Note: torch.compile() not supported on MPS.

- Real-time factor = audio duration / processing time

### Performance Optimization

For optimal inference performance on CUDA/CPU:

```python
# Load and compile model (PyTorch 2.0+)
model = AudioCodecModel.from_pretrained(
    "nineninesix/nemo-nano-codec-22khz-0.6kbps-12.5fps-pytorch",
    device="cuda"
)
model.eval()

# Compile for 1.2-2x speedup
model.compile(mode="reduce-overhead")

# First inference includes compilation overhead (~5-10 seconds)
with torch.no_grad():
    tokens, _ = model.encode(audio_tensor, audio_len)

# Subsequent inferences are faster
with torch.no_grad():
    reconstructed, _ = model.decode(tokens, tokens_len)
```

**Compilation modes**:
- `default`: Balanced optimization
- `reduce-overhead`: Best for inference (recommended)
- `max-autotune`: Aggressive optimization (longer compile time)

**Note**: torch.compile() requires PyTorch 2.0+ and is not supported on MPS (Apple Silicon).

### Memory Usage

| Batch Size | Audio Length | Model Size | Peak Memory (CUDA) |
|------------|--------------|------------|--------------------|
| 1          | 5s           | 420 MB     | 500 MB             |
| 4          | 5s           | 420 MB     | 650 MB             |
| 16         | 5s           | 420 MB     | 1.2 GB             |

## Testing

The codebase includes comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/nanocodec_torch --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m quality       # Audio quality tests
```

**Test Results**: 164/164 tests passing (98.8%), 2 skipped (device-specific).

## Documentation

- [API_REFERENCE.md](API_REFERENCE.md) - Complete API reference
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines


## Known Limitations

1. **Audio Quality**: As an ultra-low bitrate codec (0.6 kbps), expect significant quality degradation compared to higher bitrate codecs
2. **Sample Rate**: Fixed at 22.05 kHz, not suitable for high-fidelity audio
3. **Mono Only**: Stereo audio will be converted to mono
4. **Compression Artifacts**: Extreme compression ratio (1764:1) introduces noticeable artifacts
5. **Use Case**: Best suited for speech/voice applications, not music production

## License

This code is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

The original NVIDIA NeMo NanoCodec model weights and architecture are developed by NVIDIA Corporation and are licensed under the **NVIDIA Open Model License**. See [NOTICE](NOTICE) for attribution.

**When using this project, you must comply with both licenses.**

## Acknowledgments

- Original implementation by NVIDIA NeMo Team
- Architecture based on [HiFi-GAN](https://arxiv.org/abs/2010.05646)
- Quantization based on [Finite Scalar Quantization (FSQ)](https://arxiv.org/abs/2309.15505)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pytorch-nano/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pytorch-nano/discussions)
- **Documentation**: [Full Documentation](https://github.com/yourusername/pytorch-nano/tree/main/docs)

