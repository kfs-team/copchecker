from confluent_kafka import Consumer, KafkaException, KafkaError
from loguru import logger


class KafkaConsumer:
    def __init__(self, brokers, group_id, topic):
        self.conf = {
            'bootstrap.servers': brokers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        self.topic = topic
        self.consumer = Consumer(self.conf)
        self.running = True

    def start(self):
        self.consumer.subscribe([self.topic])
        try:
            while self.running:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())
                else:
                    logger.info(
                        f"Received message: {msg.value().decode('utf-8')} "
                        f"from topic: {msg.topic()} partition: {msg.partition()} offset: {msg.offset()}"
                    )
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    def stop(self):
        self.running = False
