from abc import ABC, abstractmethod
from typing import Dict

import numpy as np


class Encoder(ABC):
    def __init__(
        self,
        device: str,
        batch_size: int,
        segment_len: int,
        overlap_len: int | None,
        segment_step: int
    ):
        self.device = device
        self.batch_size = batch_size
        self.segment_len = segment_len
        self.overlap_len = overlap_len
        self.segment_step = segment_step

    @abstractmethod
    def get_embeddings(self, video: str) -> np.ndarray | Dict[str, np.ndarray | list]:
        pass

    @property
    @abstractmethod
    def emb_size(self) -> int:
        pass
