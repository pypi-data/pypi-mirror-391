"""Unit tests for CUDA functionality."""

import logging

import torch.cuda

logger = logging.getLogger(__name__)


def test_cuda_availability() -> None:
    """Test if CUDA is available."""
    logger.info("Testing CUDA...")
    # GIVEN / WHEN
    cuda_available = torch.cuda.is_available()

    # THEN
    assert cuda_available is True

    logger.info("CUDA available!")
    logger.info("✓ CUDA version: %s", torch.version.cuda)
    logger.info("✓ Number of GPUs: %d", torch.cuda.device_count())
    for i in range(torch.cuda.device_count()):
        logger.info("  - GPU %d: %s", i, torch.cuda.get_device_name(i))
