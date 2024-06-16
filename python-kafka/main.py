from kafka import KafkaConsumer, KafkaProducer
import json


def main():
    inputTopic = "index-input"
    resultTopic = "index-result"
    consumer = KafkaConsumer(
        inputTopic,
        bootstrap_servers=['localhost:29092'],
        auto_offset_reset='earliest',
        group_id='group',
    )
    producer = KafkaProducer(
        bootstrap_servers=['localhost:29092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks="all",
        retries=3,
    )



    while True:
        msgs = consumer.poll(timeout_ms=1000)
        for partition, messages in msgs.items():
            for msg in messages:
                print(f"Partition: {partition}, Offset: {msg.offset}, Key: {msg.key}, Value: {msg.value}")
                consumer.commit()
                result = json.loads(msg.value)
                result['video_id'] = result['uuid']
                producer.send(resultTopic, result)
                print(f"Message: {result} sent to {resultTopic}")


if __name__ == '__main__':
    main()
