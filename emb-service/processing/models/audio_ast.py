from typing import Tuple, Dict

import numpy as np
import torch
import torchaudio

from transformers import ASTForAudioClassification, ASTFeatureExtractor

from .encoder import Encoder


class AudioASTEncoder(Encoder):
    def __init__(
        self,
        device: str,
        batch_size: int,
        segment_len: int,
        overlap_len: int | None,
        segment_step: int
    ):
        super().__init__(device, batch_size, segment_len, overlap_len, segment_step)

        self.model = ASTForAudioClassification.from_pretrained(
            "MIT/ast-finetuned-audioset-10-10-0.4593",
            output_hidden_states=True
        ).to(self.device)
        self.feature_extractor = ASTFeatureExtractor.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")

    @torch.inference_mode()
    def get_embeddings(self, video: str) -> np.ndarray:
        waveform, sample_rate = self.load_audio(video)

        interval_size = (waveform.shape[1] // (self.segment_len * sample_rate))
        wf_tensor = torch.vstack(
            [
                waveform[..., :interval_size * self.segment_len * sample_rate].reshape(interval_size, self.segment_len * sample_rate),
                waveform[..., -self.segment_len * sample_rate:]
            ]
        )

        embs = []
        for batch in torch.split(wf_tensor, self.batch_size):
            inputs = torch.cat([
                self.feature_extractor(
                    elem,
                    sampling_rate=sample_rate,
                    return_tensors="pt"
                )['input_values']
                for elem in batch
            ]).to(self.device)
            with torch.autocast(device_type=self.device):
                outputs = self.model(input_values=inputs)
            cls_embeddings = outputs.hidden_states[-1][:, 0, :]
            embs.append(cls_embeddings.cpu().numpy())
        embs = np.concatenate(embs)
        embs /= np.linalg.norm(embs, axis=0)
        return embs.astype(np.float32)

    @staticmethod
    def load_audio(file_path, target_sample_rate=16000) -> Tuple[torch.Tensor, int]:
        waveform, sample_rate = torchaudio.load(file_path)
        if sample_rate != target_sample_rate:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
            waveform = resampler(waveform)
            sample_rate = target_sample_rate

        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        return waveform, sample_rate

    @property
    def emb_size(self) -> int:
        return 768
