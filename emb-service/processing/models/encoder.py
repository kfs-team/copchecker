from abc import ABC, abstractmethod

import numpy as np


class Encoder(ABC):
    def __init__(
        self,
        device: str
    ):
        self.device = device

    @abstractmethod
    def get_embeddings(
        self,
        video: str,
        segment_len: int,
        overlap_len: int | None,
        segment_step: int
    ) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def emb_size(self) -> int:
        pass
