# Pytorch Device Detection

Small utility to select a torch device at runtime and to clear CUDA caches.

## Summary

Provides two functions:

- `get_device(strings=False, verbose=False)`: returns the best available device (`torch.device` by default, or a string when `strings=True`). Probes in this order: `TORCH_DEVICE`/`DEVICE` environment variables, CUDA, MPS, XPU (torch.xpu or intel_extension_for_pytorch.xpu), then CPU. When `verbose=True` the function emits debug-level messages through the logger.

- `clear_torch()`: calls `torch.cuda.empty_cache()`.

## Install

```console
uv add devicer
```

If you want XPU:

```console
uv add devicer[xpu]
```

## Usage

```py
from devicer import get_device

device = get_device()
print(device)
```

Environment variables:

- Set `TORCH_DEVICE` or `DEVICE` to force a device, for example `cuda`, `cuda:0`, `mps`, `cpu`, or `xpu`:

```sh
export TORCH_DEVICE=cuda
python myscript.py
```

