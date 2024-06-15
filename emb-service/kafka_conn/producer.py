from typing import List, Dict

from loguru import logger
from confluent_kafka import Producer


class KafkaProducer:
    def __init__(self, brokers, topic):
        self.conf = {'bootstrap.servers': brokers}
        self.topic = topic
        self.producer = Producer(self.conf)

    def produce_message(self, message: str | Dict):
        self.producer.produce(self.topic, message.encode('utf-8'), callback=self.delivery_report)
        self.producer.poll(0)

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

    def flush(self):
        self.producer.flush()
