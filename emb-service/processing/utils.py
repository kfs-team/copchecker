from loguru import logger

import torch


def autodevice():
    if torch.cuda.is_available():
        logger.info("Using cuda accelerator for inference")
        return 'cuda'
    else:
        logger.info("Using cpu for inference")
        return 'cpu'
