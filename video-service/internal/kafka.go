package internal

import "github.com/segmentio/kafka-go"

func KafkaProducer(brokers []string, topic string) *kafka.Writer {
	writer := kafka.NewWriter(kafka.WriterConfig{
		Brokers:  brokers,
		Topic:    topic, // Название топика
		Balancer: &kafka.LeastBytes{},
	},
	)
	return writer
}

func KafkaConsumer(brokers []string, topic string) *kafka.Reader {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers: brokers,
		GroupID: "group",
		Topic:   topic,
	})
	return reader
}
