import shutil
import tempfile
from pathlib import Path

from minio import Minio

from kafka_conn import KafkaProducer, KafkaConsumer
from processing import *
from utils import download_content


def main():
    indexing_pipeline = Pipeline(
        Embedder(
            audio_encoder=AudioASTEncoder(
                device=utils.autodevice(),
                batch_size=16,      # fixme config
                segment_len=10,     # fixme config
                overlap_len=0,      # fixme config
                segment_step=2      # fixme config
            ),
            video_encoder=ImageCLIPEncoder(
                device=utils.autodevice(),
                batch_size=16,      # fixme config
                segment_len=10,     # fixme config
                overlap_len=0,      # fixme config
                segment_step=2      # fixme config
            )
        ),
        MilvusUpload(
            "http://192.168.0.110:19530",       # fixme config
            'copyright',                # fixme config
        )
    )

    minio_client = Minio(
        'minio:9000',                # fixme
        'ROOTUSERNAME',            # fixme
        'ROOTPASSWORD'             # fixme
    )

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        json_data = ...
        video_id = json_data['uuid']
        video_path = download_content(
            minio_client, json_data['bucket_name'], json_data['video_name'], tmp_dir
        )
        indexing_pipeline.run(video_path, video_id)
    except Exception as e:
        raise  # report to backend
    finally:
        shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    main()
