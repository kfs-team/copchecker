from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone

import numpy as np
import torch
from ultralytics import YOLO
from moviepy.editor import VideoFileClip
from pymilvus import connections, Collection, AnnSearchRequest, RRFRanker

from .operators import Operator


class MilvusSearch(Operator):
    def __init__(
        self,
        milvus_host,
        milvus_collection_name,
        milvus_username='',
        milvus_password='',
        download_batch_size=128
    ):
        connections.connect(uri=milvus_host, user=milvus_username, password=milvus_password)
        self.collection = Collection(name=milvus_collection_name)
        self.download_batch_size = download_batch_size

    def run(self, embedder_output: Dict[str, Any], **kwargs):
        vit = self.create_batch_iterator(embedder_output['video_embs'], self.download_batch_size)
        ait = self.create_batch_iterator(embedder_output['audio_embs'], self.download_batch_size)

        proposals = []
        for video_embs, audio_embs in zip(vit, ait):
            video_request = AnnSearchRequest(
                data=video_embs,
                anns_field="video_emb",
                param={
                    "metric_type": "IP",
                    "params": {"ef": 200}       # fixme
                },
                limit=5                         # fixme
            )
            audio_request = AnnSearchRequest(
                data=audio_embs,
                anns_field="audio_emb",
                param={
                    "metric_type": "IP",
                    "params": {"ef": 200}       # fixme
                },
                limit=5                         # fixme
            )
            reqs = [video_request, audio_request]

            rerank = RRFRanker(k=60)             # fixme
            batch_proposals = self.collection.hybrid_search(
                reqs=reqs,
                rerank=rerank,
                limit=20,                       # fixme
                output_fields=["video_id", "start_time", "end_time"],
            )
            proposals.extend(batch_proposals)

        return {self.__class__.__name__.lower() + '_output': proposals}

    @staticmethod
    def create_batch_iterator(lst, batch_size):
        for i in range(0, len(lst), batch_size):
            yield lst[i:i + batch_size]


class PicInPicDetector(Operator):
    def __init__(
        self,
        device: str,
        detector_path: str,
        min_length: int,
        pip_area_threshold: float,
        confidence_threshold: float,
        black_share_threshold: float,
        frame_every_k_sec: int
    ):
        assert 0 <= pip_area_threshold <= 1, pip_area_threshold
        assert 0 <= confidence_threshold <= 1, confidence_threshold
        assert 0 <= black_share_threshold <= 1, black_share_threshold

        self.detector = YOLO(detector_path).to(device)

        self.min_length = min_length
        self.pip_area_threshold = pip_area_threshold
        self.confidence_threshold = confidence_threshold
        self.frame_every_k_sec = frame_every_k_sec
        self.black_share_threshold = black_share_threshold

    @torch.inference_mode()
    def run(
        self,
        video_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        video = VideoFileClip(video_path)

        # Step 1: Detect picture-in-picture frames in the video
        pip_timestamps = []
        last_good_frame = 0

        for i in range(0, int(video.duration), self.frame_every_k_sec):
            img = video.get_frame(i)
            out = self.detector(img, verbose=False)
            confidence = float('inf')
            if out[0].boxes:
                box = out[0].boxes.xyxy.cpu().int().tolist()[0]
                confidence = round(out[0].boxes.conf[0].cpu().item(), 2)
                if confidence >= self.confidence_threshold:
                    pip_timestamps.append((i, confidence, box))
                    last_good_frame = i

            if not out[0].boxes or confidence < self.confidence_threshold:
                black_pixel = np.array([4, 4, 4])
                black_pixels_count = np.sum(np.all(img <= black_pixel, axis=-1))
                if ((
                        (black_pixels_count * 3) / img.size > self.black_share_threshold) and
                        (i - last_good_frame <= self.min_length) and
                        pip_timestamps
                ):
                    pip_timestamps.append((i, self.confidence_threshold, pip_timestamps[-1][-1]))
                    last_good_frame = i

        # if potential pip is not found in the video
        if not pip_timestamps:
            final_results = []
        else:
            # Step 2: Split the detected frames into intervals based on a minimum length
            intervals = []
            current_interval = []

            for i in range(len(pip_timestamps)):
                if not current_interval:
                    current_interval.append(pip_timestamps[i])
                else:
                    if pip_timestamps[i][0] - current_interval[-1][0] < self.min_length:
                        current_interval.append(pip_timestamps[i])
                    else:
                        if current_interval[-1][0] - current_interval[0][0] >= self.min_length:
                            intervals.append((current_interval[0][0], current_interval[-1][0]))
                        current_interval = [pip_timestamps[i]]

            if current_interval and (current_interval[-1][0] - current_interval[0][0] >= self.min_length):
                intervals.append((current_interval[0][0], current_interval[-1][0]))

            # Step 3: Select the highest confidence bounding boxes for each interval
            # Need to filter with relative PiP area
            potential_pip = []

            for interval in intervals:
                start, end = interval
                filtered_results = [res for res in pip_timestamps if start <= res[0] <= end]

                if filtered_results:
                    highest_confidence_result = max(filtered_results, key=lambda x: x[1])
                    potential_pip.append((start, end, highest_confidence_result[2]))

            # Step 4. Filter relative by relative area. Crop is PiP when area <= thr * video area
            video_shape = video.get_frame(0).shape
            video_area = video_shape[0] * video_shape[1]
            final_results = []

            for interval in potential_pip:
                x_min, y_min, x_max, y_max = interval[-1]
                box_area = (x_max - x_min) * (y_max - y_min)
                relative_area = box_area / video_area
                if relative_area <= self.pip_area_threshold:
                    final_results.append(interval)

        return {self.__class__.__name__.lower() + '_output': final_results}


class ProposalsPostprocessor(Operator):
    def run(
        self,
        embedder_output: Dict[str, Any],
        picinpicdetector_output: List[Tuple[int, int, List]] = [],
        **kwargs
    ) -> Dict[str, Any]:



        return {self.__class__.__name__.lower() + '_output': kwargs['proposals']}


class CheckerDatabasePostprocessor(Operator):
    def run(
        self,
        video_id: str,
        start_time: str,
        proposalspostprocessor_output=None,
        **kwargs
    ):
        # fixme генерация интервалов
        import uuid
        import random
        end_time = self.get_current_utc_time_iso()
        intervals_data = [
            {
                "index_id": str(uuid.uuid4()),
                "start": random.randint(1, 1000),
                "end": random.randint(1, 1000),
                "start_time": start_time,
                "end_time": end_time
            } for _ in range(random.randint(0, 150))
        ]

        data = {
            "video_id": video_id,
            "valid": not intervals_data,
            "intervals": intervals_data,
        }

        return {self.__class__.__name__.lower() + '_output': data}  # todo

    @staticmethod
    def get_current_utc_time_iso():
        now_utc = datetime.now(timezone.utc)
        iso_time_str = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        return iso_time_str
