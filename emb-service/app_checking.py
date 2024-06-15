from kafka_conn import KafkaProducer, KafkaConsumer

from processing import *


def main():
    indexing_pipeline = Pipeline(
        Embedder(
            audio_encoder=AudioASTEncoder(
                device=autodevice(),
                batch_size=16,      # fixme config
                segment_len=10,     # fixme config
                overlap_len=0,      # fixme config
                segment_step=2      # fixme config
            ),
            video_encoder=ImageCLIPEncoder(
                device=autodevice(),
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

    video_path = ...
    video_id = ...

    indexing_pipeline.run(video_path, video_id)


if __name__ == '__main__':
    main()