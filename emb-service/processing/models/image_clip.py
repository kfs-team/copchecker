import numpy as np
import torch
from PIL import Image
from moviepy.editor import VideoFileClip
from transformers import CLIPModel, CLIPProcessor

from .encoder import Encoder


class ImageCLIPEncoder(Encoder):
    def __init__(self, device):
        super().__init__(device)

        self.model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32').eval().to(torch.float16).to(self.device)
        self.processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')

    @torch.inference_mode()
    def get_embeddings(
        self,
        video: str,
        segment_len: int,
        overlap_len: int | None,
        segment_step: int
    ) -> np.ndarray:
        """Get embeddings from the video
        :param video: path to the video
        :segment_len: len of the segment to calc embeddings (sec)
        :overpap_len: len of the segments overlap (insec)
        """
        video = VideoFileClip(video)
        video_duration = video.duration

        embeddings = []
        for segment_start in range(0, int(video_duration), segment_len):
            segment_end = min(segment_start + segment_len, video_duration)

            frames = [
                video.get_frame(t)  # todo grayscale
                for t in range(segment_start, int(segment_end), segment_step)
            ]
            inputs = self.processor(
                images=frames,  # list[np.ndarray] | np.ndarray
                return_tensors="pt",
            ).to(torch.float16).to(self.device)
            outputs = self.model.get_image_features(**inputs).cpu().numpy()

            if len(outputs):
                average_embedding = np.mean(outputs, axis=0)
                average_embedding /= np.linalg.norm(average_embedding, ord=2)
                embeddings.append(average_embedding)

        return np.array(embeddings)

    @property
    def emb_size(self) -> int:
        return 512
