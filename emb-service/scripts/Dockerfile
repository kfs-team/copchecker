FROM python:3.10-slim-bullseye

WORKDIR /app

COPY ./configs/emb_config.yaml ./emb_config.yaml
COPY ./scripts/create_db.py ./create_db.py
COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

CMD ["/bin/bash"]
