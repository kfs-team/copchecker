from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

from loguru import logger
from pymilvus import MilvusClient

from ..models import Encoder


class Operator(ABC):
    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        pass


class MilvusUpload(Operator):
    def __init__(
            self,
            milvus_host,
            milvus_collection_name,
            milvus_username='',
            milvus_password='',
            upload_batch_size=128,
    ):
        self.client = MilvusClient(uri=milvus_host, user=milvus_username, password=milvus_password)
        self.collection_name = milvus_collection_name
        self.upload_batch_size = upload_batch_size

    def run(self, embedder_output: Dict[str, Any], video_id: str, **kwargs):
        logger.info(f"Uploading data to Milvus, n_items={len(embedder_output['video_embs'])}")

        data = [
            {
                'video_id': video_id,
                'video_emb': video_emb,
                'audio_emb': audio_emb,
                'start_time': start_time,
                'end_time': end_time
            }
            for video_emb, audio_emb, (start_time, end_time) in
            zip(embedder_output['video_embs'], embedder_output['audio_embs'], embedder_output['intervals'])
        ]

        for batch in self.create_batch_iterator(data, batch_size=self.upload_batch_size):
            self.client.insert(
                collection_name=self.collection_name,
                data=batch,
                timeout=5
            )
        return {self.__class__.__name__.lower() + '_output': {"video_id": video_id}}

    @staticmethod
    def create_batch_iterator(lst, batch_size):
        for i in range(0, len(lst), batch_size):
            yield lst[i:i + batch_size]


class Embedder(Operator):
    def __init__(
        self,
        audio_encoder: Encoder,
        video_encoder: Encoder
    ):
        self.audio_encoder = audio_encoder
        self.video_encoder = video_encoder

    def run(
        self,
        video_path: str,
        video_id: str,
        picinpicdetector_output: List[Tuple[int, int, List]] = [],
        **kwargs
    ) -> Dict[str, List]:
        logger.info(f"Extracting audio embeddings")
        audio_embs = self.audio_encoder.get_embeddings(video_path)

        logger.info(f"Extracting video embeddings")
        video_data = self.video_encoder.get_embeddings(
            video_path,
            picinpic_intervals=picinpicdetector_output
        )
        video_embs = video_data['embeddings']
        intervals = video_data['intervals']

        data = {
            'video_embs': video_embs,
            'audio_embs': audio_embs,
            'intervals': intervals
        }

        return {self.__class__.__name__.lower() + '_output': data}
