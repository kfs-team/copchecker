from typing import Dict, Any, List
from itertools import chain

import numpy as np
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


class CheckingPostprocessor(Operator):
    def __init__(self):
        pass

    def run(self, **kwargs):
        return {self.__class__.__name__.lower() + '_output': {'a': 'b', 'c': 'd'}} # todo
