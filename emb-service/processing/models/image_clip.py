from typing import Dict, Tuple, List

import numpy as np
import torch
from moviepy.editor import VideoFileClip
from transformers import CLIPModel, CLIPProcessor

from .encoder import Encoder


class ImageCLIPEncoder(Encoder):
    def __init__(
        self,
        device: str,
        batch_size: int,
        segment_len: int,
        overlap_len: int | None,
        segment_step: int
    ):
        super().__init__(device, batch_size, segment_len, overlap_len, segment_step)

        self.model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32').eval().to(self.device)
        self.processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')

    @torch.inference_mode()
    def get_embeddings(
        self,
        video: str,
        picinpic_intervals: List[Tuple[int, int, List]] = []
    ) -> Dict[str, np.ndarray | int]:
        video = VideoFileClip(video)
        video_duration = video.duration

        embeddings = []
        for segment_start in range(0, int(video_duration), self.segment_len):
            segment_end = min(segment_start + self.segment_len, video_duration)

            frames = [
                video.get_frame(t)  # todo grayscale
                for t in range(segment_start, int(segment_end), self.segment_step)
            ]
            inputs = self.processor(
                images=frames,  # list[np.ndarray] | np.ndarray
                return_tensors="pt",
            ).to(self.device)

            with torch.autocast(device_type=self.device):
                outputs = self.model.get_image_features(**inputs).cpu().numpy()

            if len(outputs):
                average_embedding = np.mean(outputs, axis=0)
                average_embedding /= np.linalg.norm(average_embedding, ord=2)
                embeddings.append(average_embedding)

        return {'embeddings': np.array(embeddings).astype(np.float32), 'intervals': self.get_intervals(video_duration)}

    def get_intervals(self, video_duration: float) -> List[Tuple[int, int]]:
        video_duration = int(video_duration)
        intervals = [
            (i*self.segment_len, (i + 1)*self.segment_len)
            for i in range(0, video_duration // self.segment_len)
        ]
        if video_duration % self.segment_len != 0:
            intervals.append((video_duration - self.segment_len, video_duration))

        return intervals

    @property
    def emb_size(self) -> int:
        return 512
