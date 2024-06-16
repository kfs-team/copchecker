from typing import Dict, Tuple, List

import cv2
import torch
import numpy as np
from PIL import Image
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


    def get_embeddings(
        self,
        video: str,
        picinpic_intervals: List[Tuple[int, int, List]] = []
    ) -> Dict[str, np.ndarray | int]:
        video = VideoFileClip(video)
        video_duration = video.duration

        embeddings = []
        embeddings_pip = []
        current_pip_idx = 0
        for segment_start in range(0, int(video_duration), self.segment_len):
            segment_end = min(segment_start + self.segment_len, video_duration)

            frames = [
                self.preprocess_image(video.get_frame(t))  # todo grayscale
                for t in range(segment_start, int(segment_end), self.segment_step)
            ]

            if picinpic_intervals:
                pip_start, pip_end, box = picinpic_intervals[current_pip_idx]

                if not (segment_start <= pip_start and segment_end >= pip_end):
                    current_pip_idx = min(current_pip_idx + 1, len(picinpic_intervals) - 1)
                    pip_start, pip_end, box = picinpic_intervals[current_pip_idx]

                crops = [
                    frame
                    for i, frame in zip(range(segment_start, int(segment_end), self.segment_step), frames)
                    if pip_start <= i < pip_end
                ]
                if crops:
                    embs = self._predict(frames).astype(np.float32)
                    embeddings_pip.append(embs)
                else:
                    embeddings_pip.append(None)
            else:
                embeddings_pip.append(None)

            embeddings.append(self._predict(frames))

        data_output = {
            'embeddings': np.array(embeddings).astype(np.float32),
            'embeddings_pip': embeddings_pip,
            'intervals': self.get_intervals(video_duration),
        }
        return data_output

    @torch.inference_mode()
    def _predict(self, images):
        inputs = self.processor(
            images=images,  # list[np.ndarray] | np.ndarray
            return_tensors="pt",
        ).to(self.device)

        with torch.autocast(device_type=self.device):
            outputs = self.model.get_image_features(**inputs).cpu().numpy()

        average_embedding = np.sum(outputs, axis=0)
        average_embedding /= np.linalg.norm(average_embedding, ord=2)

        return average_embedding

    @staticmethod
    def preprocess_image(image: np.ndarray) -> np.ndarray:
        """Удаление паддинга и заполнение чёрных пикселей"""

        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2RGB)

        image_pil = Image.fromarray(image)
        bbox = image_pil.point(lambda x: 0 if x < 10 else 255).getbbox()

        if bbox is not None:
            left, upper, right, lower = bbox
            width, height = image_pil.size

            # если нет поворота -- обрезаем паддинг
            if not (
                    abs(left - 0) < 10 and
                    abs(upper - 0) < 10 and
                    abs(right - width) < 10 and
                    abs(lower - height) < 10
            ):
                image = image[upper: lower, left: right]

        # Обнаружение чёрных пикселей
        mask = (image[:, :] <= 5)
        mean_color = image[~mask].mean(axis=0)
        image[mask] = mean_color
        return image

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
