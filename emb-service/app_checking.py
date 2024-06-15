import shutil
import tempfile

from kafka_conn import KafkaProducer, KafkaConsumer
from processing import *
from .utils import download_content


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

    temp_dir = tempfile.mkdtemp()

    try:
        video_id = ...
        video_path = download_content(...) # fixme
        indexing_pipeline.run(video_path, video_id)
    except Exception as e:
        raise  # report to backend
    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()
