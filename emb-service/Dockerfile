FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu22.04

WORKDIR /app
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
        build-essential git wget python3 python3-pip \
        ffmpeg libsm6 libxext6 libxrender1 libglib2.0-0 \
        vim lsb-release curl gpg ghostscript

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install sox==1.5.0

COPY ./processing/ ./processing/
COPY ./utils.py ./utils.py
COPY ./app.py ./app.py

COPY ./configs/emb_config.yaml ./emb_config.yaml

RUN mkdir -p /app/weights
RUN wget "https://storage.yandexcloud.net/copchecker-weights/pic_in_pic_detector_yolo.pt" -P weights/

ENTRYPOINT ["/bin/bash"]