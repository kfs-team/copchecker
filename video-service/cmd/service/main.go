package main

import (
	"context"
	"net/http"

	"video-service/internal"
	"video-service/internal/handlers"

	"github.com/gorilla/mux"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq" // Импорт драйвера PostgreSQL
	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
	"github.com/segmentio/kafka-go"
	"github.com/sirupsen/logrus"
)

const (
	bucketName         = "video-service-bucket"
	indexTopic         = "index-input"
	processingTopic    = "processing-input"
	minioHost          = "minio:9000"
	accessKey          = "ROOTUSERNAME"
	secretKey          = "ROOTPASSWORD"
	dbConnectionString = "postgres://postgres:postgres@postgres:5432/postgres?sslmode=disable"
	kafkaHost          = "kafka:9092"
	indexResultTopic   = "index-result"
	processingResult   = "processing-result"
)

func main() {
	logger := logrus.New()
	logger.SetLevel(logrus.DebugLevel)
	logger.Info("Starting service")

	// graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	defer func() {
		logger.Info("Stopping service")
		cancel()
	}()

	kafkaIndexConsumer := internal.KafkaConsumer([]string{kafkaHost}, indexResultTopic)
	kafkaProcessingConsumer := internal.KafkaConsumer([]string{kafkaHost}, processingResult)
	kafkaProducer := internal.KafkaProducer([]string{kafkaHost})

	// creating topics
	conn, err := kafka.DialLeader(ctx, "tcp", kafkaHost, indexTopic, 0)
	if err != nil {
		logger.Fatal(err)
	}
	conn.Close()

	conn, err = kafka.DialLeader(ctx, "tcp", kafkaHost, processingTopic, 0)
	if err != nil {
		logger.Fatal(err)
	}
	conn.Close()

	minioClient, err := minio.New(minioHost, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
		Secure: false,
	})
	if err != nil {
		logger.Fatal(err)
	}
	dbClient, err := sqlx.Connect("postgres", dbConnectionString)
	if err != nil {
		logger.Fatal(err)
	}
	defer dbClient.Close()
	db := internal.NewPostgres(dbClient)

	processingResultReader := internal.NewProcessingResultReader(ctx, db, kafkaProcessingConsumer, logger)
	indexResultReader := internal.NewIndexResultReader(ctx, db, kafkaIndexConsumer, logger)

	go processingResultReader.Start()
	go indexResultReader.Start()

	uploadVideoHandler := handlers.NewUploadVideoHandler(db, minioClient, logger, kafkaProducer)
	getVideoHandler := handlers.NewGetVideoHandler(db, minioClient, logger)
	getProcessingByVideoIdHandler := handlers.NewGetProcessingByVideoIdHandler(db, logger)
	getAllProcessingsHandler := handlers.NewGetAllProcessingsHandler(db, logger)
	router := mux.NewRouter()
	router.HandleFunc("/video", uploadVideoHandler.Handle).Methods("POST")
	router.HandleFunc("/video/{id}", getVideoHandler.Handle).Methods("GET")
	router.HandleFunc("/processing/{id}", getProcessingByVideoIdHandler.Handle).Methods("GET")
	router.HandleFunc("/processing", getAllProcessingsHandler.Handle).Methods("GET")
	logger.Info("Listening on port 1111")
	http.ListenAndServe(":1111", router)
}
