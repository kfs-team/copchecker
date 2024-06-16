package internal

import (
	"context"
	"encoding/json"
	"errors"
	"time"

	"github.com/segmentio/kafka-go"
	"github.com/sirupsen/logrus"
)

type Interval struct {
	IndexId string `json:"index_id"`
	Start   int    `json:"start_at"`
	End     int    `json:"end_at"`
}

type ProcessingResultMessage struct {
	VideoId   string     `json:"video_id" ,db:"video_id"`
	Valid     bool       `json:"valid" ,db:"valid"`
	Start     time.Time  `json:"start_time" ,db:"start"`
	End       time.Time  `json:"end_time" ,db:"end_at"`
	Intervals []Interval `json:"intervals" ,db:"intervals"`
}

type IndexResultMessage struct {
	VideoId string `json:"video_id"`
}

func KafkaProducer(brokers []string) *kafka.Writer {
	writer := kafka.Writer{
		Addr:         kafka.TCP(brokers...),
		Balancer:     &kafka.LeastBytes{},
		RequiredAcks: kafka.RequireAll,
	}
	return &writer
}

func KafkaConsumer(brokers []string, topic string) (*kafka.Reader, error) {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers: brokers,
		GroupID: "group",
		Topic:   topic,
	})
	if reader == nil {
		return nil, errors.New("kafka consumer is nil")
	}
	return reader, nil
}

type ProcessingResultReader struct {
	ctx    context.Context
	reader *kafka.Reader
	db     *Postgres
	logger *logrus.Logger
}

func NewProcessingResultReader(ctx context.Context, db *Postgres, reader *kafka.Reader, logger *logrus.Logger) *ProcessingResultReader {
	return &ProcessingResultReader{ctx: ctx, db: db, reader: reader, logger: logger}
}

func (r *ProcessingResultReader) Start() {
	for {
		select {
		case <-r.ctx.Done():
			return
		default:
			msg, err := r.reader.FetchMessage(r.ctx)
			if err != nil {
				r.logger.Error(err)
				continue
			}
			msgBytes := msg.Value
			r.logger.Info("Message bytes: ", msgBytes)
			var processingResultMessage ProcessingResultMessage
			r.logger.Info("HUITA: ", processingResultMessage.VideoId)
			_ = json.Unmarshal(msgBytes, &processingResultMessage)
			r.logger.Info("Message: ", processingResultMessage)
			err = r.db.InsertProcessing(&processingResultMessage)
			if err != nil {
				r.logger.Error(err)
				continue
			}
			err = r.db.UpdateVideoByVideoId(processingResultMessage.VideoId)
			if err != nil {
				r.logger.Error(err)
				continue
			}
			r.logger.Info("Processing result message inserted")
			r.reader.CommitMessages(r.ctx, msg)
		}
	}
}

type IndexResultReader struct {
	ctx    context.Context
	reader *kafka.Reader
	db     *Postgres
	logger *logrus.Logger
}

func NewIndexResultReader(ctx context.Context, db *Postgres, reader *kafka.Reader, logger *logrus.Logger) *IndexResultReader {
	return &IndexResultReader{ctx: ctx, db: db, reader: reader, logger: logger}
}

func (r *IndexResultReader) Start() {
	for {
		select {
		case <-r.ctx.Done():
			return
		default:
			msg, err := r.reader.FetchMessage(r.ctx)
			if err != nil {
				r.logger.Error(err)
				continue
			}
			msgBytes := msg.Value
			var indexResultMessage IndexResultMessage
			_ = json.Unmarshal(msgBytes, &indexResultMessage)
			r.logger.Info("Message: ", indexResultMessage)
			err = r.db.UpdateIndexVideoByVideoId(indexResultMessage.VideoId)
			if err != nil {
				r.logger.Error(err)
				continue
			}
			r.logger.Info("Index video added")
			r.reader.CommitMessages(r.ctx, msg)
		}
	}
}
