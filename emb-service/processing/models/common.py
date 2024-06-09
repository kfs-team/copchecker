from abc import ABC, abstractmethod

import numpy as np


class Encoder(ABC):

    @abstractmethod
    def get_embeddings(
        self,
        video: str,
        segment_len: int,
        overlap_len: int | None,
        segment_step: int
    ) -> np.ndarray:
        pass
