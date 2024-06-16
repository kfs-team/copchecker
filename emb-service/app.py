import json
import yaml
import shutil
import argparse
import tempfile
from pathlib import Path
from typing import Dict, Any


from loguru import logger
from minio import Minio
from kafka import KafkaConsumer, KafkaProducer

from processing import *
from utils import download_content


def main_helper(
    *,
    pipeline: Pipeline,
    global_settings: Dict[str, Any],
    service_settings: Dict[str, Any]
) -> None:
    minio_client = Minio(**global_settings['minio'])
    consumer = KafkaConsumer(
        service_settings['kafka_consumer_topic'],
        bootstrap_servers=global_settings['kafka']['bootstrap_servers'],
        auto_offset_reset='earliest'
    )

    tmp_dir = Path(tempfile.mkdtemp())
    for message in consumer:
        logger.info(f'Received a message')
        try:
            json_data = json.loads(message.value.decode('utf-8'))
            video_id = json_data['uuid']
            video_path = download_content(
                minio_client, json_data['bucket_name'], json_data['video_name'], tmp_dir
            )
            output = pipeline.run(video_path=video_path, video_id=video_id) # str or json
            output_message = {'data': output}
            # todo send message to service_settings['kafka_producer_topic']
        except Exception as e:
            logger.error("Exception occurred", exc_info=True)
            # todo report to backend
        finally:
            shutil.rmtree(tmp_dir)


def main_checker(config):
    logger.info("Starting checking service...")

    algo_settings = config['algo_settings']
    milvus_settings = config['milvus_settings']

    checking_pipeline = Pipeline(
        Embedder(
            audio_encoder=AudioASTEncoder(
                device=utils.autodevice(),
                batch_size=algo_settings['audio_encoder_batch_size'],
                segment_len=algo_settings['segment_len'],
                overlap_len=algo_settings['overlap_len'],
                segment_step=algo_settings['segment_step']
            ),
            video_encoder=ImageCLIPEncoder(
                device=utils.autodevice(),
                batch_size=algo_settings['video_encoder_batch_size'],
                segment_len=algo_settings['segment_len'],
                overlap_len=algo_settings['overlap_len'],
                segment_step=algo_settings['segment_step']
            )
        ),
        MilvusSearch(
            milvus_host=milvus_settings['host'],
            milvus_username=milvus_settings['username'],
            milvus_password=milvus_settings['password'],
            milvus_collection_name=milvus_settings['db_settings']['collection_name']
        ),
        CheckingPostprocessor(),    # fixme
        output_field='checkingpostprocessor_output'
    )

    logger.info("Checking pipeline successfully created")

    main_helper(
        pipeline=checking_pipeline,
        global_settings=config['global_settings'],
        service_settings=config['checker_settings']
    )


def main_indexer(config):
    logger.info("Starting indexer service...")

    algo_settings = config['algo_settings']
    milvus_settings = config['milvus_settings']

    indexing_pipeline = Pipeline(
        Embedder(
            audio_encoder=AudioASTEncoder(
                device=utils.autodevice(),
                batch_size=algo_settings['audio_encoder_batch_size'],
                segment_len=algo_settings['segment_len'],
                overlap_len=algo_settings['overlap_len'],
                segment_step=algo_settings['segment_step']
            ),
            video_encoder=ImageCLIPEncoder(
                device=utils.autodevice(),
                batch_size=algo_settings['video_encoder_batch_size'],
                segment_len=algo_settings['segment_len'],
                overlap_len=algo_settings['overlap_len'],
                segment_step=algo_settings['segment_step']
            )
        ),
        MilvusUpload(
            milvus_host=milvus_settings['host'],
            milvus_username=milvus_settings['username'],
            milvus_password=milvus_settings['password'],
            milvus_collection_name=milvus_settings['db_settings']['collection_name']
        ),
        output_field='milvusupload_output'
    )

    logger.info("Indexing pipeline successfully created")

    main_helper(
        pipeline=indexing_pipeline,
        global_settings=config['global_settings'],
        service_settings=config['indexer_settings']
    )


def main(cmd_args):
    with open(cmd_args.config) as f:
        config = yaml.safe_load(f)

    if cmd_args.service == 'indexer':
        main_indexer(config)
    elif cmd_args.service == 'checker':
        main_checker(config)
    else:
        raise RuntimeError(f'Unknown service mode {cmd_args.service}')


if __name__ == '__main__':
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--service', choices=['indexer', 'checker'], required=True)
    _parser.add_argument('--config', type=str, required=True)

    _args = _parser.parse_args()
    main(_args)
