import numpy as np
import torch
from PIL import Image
from moviepy.editor import VideoFileClip
from transformers import AutoModel

from .common import Encoder


class ImageJCLIPEncoder(Encoder):
    def __init__(self):
        self.image_embedder = AutoModel.from_pretrained(
            'jinaai/jina-clip-v1',
            trust_remote_code=True
        ).to('cuda')

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
                Image.fromarray(video.get_frame(t)).convert('L')
                for t in range(segment_start, int(segment_end), segment_step)
            ]
            segment_embeddings = self.image_embedder.encode_image(frames)
            if len(segment_embeddings):
                average_embedding = np.mean(segment_embeddings, axis=0)
                embeddings.append(average_embedding)

        return np.array(embeddings)
