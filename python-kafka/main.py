from kafka import KafkaConsumer


def main():
    consumer = KafkaConsumer(
        'index-input',
        bootstrap_servers=['localhost:29092'],
        auto_offset_reset='earliest',
    )
    for message in consumer:
        print(message)


if __name__ == '__main__':
    main()
