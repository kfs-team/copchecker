from pathlib import Path

from minio import Minio
from loguru import logger


def download_content(
    client: Minio,
    bucket_name: str,
    video_name: str,
    tmp_dir: Path
) -> str:
    local_file = str(tmp_dir / Path(video_name).name)
    client.fget_object(bucket_name, video_name, local_file)
    logger.info(f"Successfully downloaded {video_name}")
    return local_file
