import logging
import os

import torch

logger = logging.getLogger(__name__)


def get_device(strings=False, verbose=False):
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")
    env = os.environ.get("TORCH_DEVICE") or os.environ.get("DEVICE")
    if env:
        return torch.device(env) if not strings else str(env)

    if torch.cuda.is_available():
        if verbose:
            logger.debug("CUDA available: True")
            logger.debug("cuDNN available: %s", torch.backends.cudnn.is_available())
            logger.debug("cuDNN enabled (current): %s", torch.backends.cudnn.enabled)
        return torch.device("cuda") if not strings else "cuda"

    try:
        if (
            getattr(torch.backends, "mps", None) is not None
            and torch.backends.mps.is_available()
        ):
            if verbose:
                logger.debug("MPS available: True")
            return torch.device("mps") if not strings else "mps"
    except Exception:
        pass

    try:
        import intel_extension_for_pytorch as ipex
    except Exception:
        ipex = None

    try:
        xpu_candidates = [getattr(torch, "xpu", None)]
        if ipex is not None:
            xpu_candidates.append(getattr(ipex, "xpu", None))

        available_mod = None
        for mod in xpu_candidates:
            if mod is not None and hasattr(mod, "is_available") and mod.is_available():
                available_mod = mod
                break

        if available_mod is not None:
            try:
                if verbose:
                    logger.debug("XPU available: True")
                    logger.debug("XPU device count: %s", available_mod.device_count())
            except Exception:
                if verbose:
                    logger.debug("XPU available: True (device query failed)")
            return torch.device("xpu") if not strings else "xpu"
    except Exception:
        pass

    if verbose:
        logger.debug("Using CPU")
    return torch.device("cpu") if not strings else "cpu"
