import argparse
import yaml

from loguru import logger

from pymilvus import (
    MilvusClient,
    FieldSchema,
    CollectionSchema,
    DataType,
    connections,
    db
)


def create_db(config):
    settings = config['milvus_settings']
    logger.info(f"Creating milvus database with config: {settings}...")

    client = MilvusClient(
        uri=config['milvus_settings']['host'],
        username=settings['username'],
        password=settings['password'],
    )

    fid = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True)
    video_id = FieldSchema(
        name="video_id",
        dtype=DataType.VARCHAR,
        max_length=36,
        description="Video ID in Postgres"
    )
    video_emb = FieldSchema(
        name="video_emb",
        dtype=DataType.FLOAT_VECTOR,
        dim=settings['db_settings']['video_emb_dim'],
        description="Video embeddings",
    )
    audio_emb = FieldSchema(
        name="audio_emb",
        dtype=DataType.FLOAT_VECTOR,
        dim=settings['db_settings']['audio_emb_dim'],
        description="Audio embeddings"
    )
    start_time = FieldSchema(
        name="start_time",
        dtype=DataType.INT32,
        description="Segments start time (in seconds)",
    )
    end_time = FieldSchema(
        name="end_time",
        dtype=DataType.INT32,
        description="Segments end time (in seconds)",
    )

    collection_scheme = CollectionSchema(
        fields=[fid, video_id, video_emb, audio_emb, start_time, end_time],
        auto_id=True
    )

    client.create_collection(
        collection_name=settings['db_settings']['collection_name'],
        metric_type='IP',
        schema=collection_scheme
    )

    index_params = client.prepare_index_params(
        field_name="video_emb",
        index_type="HNSW",
        metric_type="IP",
        params=settings['db_settings']['HNSW']
    )

    client.create_index(
        settings['db_settings']['collection_name'],
        index_params=index_params
    )

    index_params = client.prepare_index_params(
        field_name="audio_emb",
        index_type="HNSW",
        metric_type="IP",
        params=settings['db_settings']['HNSW']
    )

    client.create_index(
        settings['db_settings']['collection_name'],
        index_params=index_params
    )

    client.load_collection(settings['db_settings']['collection_name'])

    logger.info(f"Collection `{settings['db_settings']['collection_name']}` has loaded")


def main(cmd_args):
    with open(cmd_args.config) as f:
        config = yaml.safe_load(f)
    create_db(config)


if __name__ == '__main__':
    # usage: python create_db.py --config ../configs/emb_config.yaml
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--config', type=str, required=True)
    _args = _parser.parse_args()
    main(_args)
