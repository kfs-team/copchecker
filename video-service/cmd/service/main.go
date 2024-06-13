package main

import (
	"net/http"
	"video-service/internal"
	"video-service/internal/handlers"

	"github.com/gorilla/mux"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq" // Импорт драйвера PostgreSQL
	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
	"github.com/sirupsen/logrus"
)

const (
	bucketName = "video-service-bucket"
)

func main() {
	logger := logrus.New()
	logger.SetLevel(logrus.DebugLevel)
	logger.Info("Starting service")
	minioHost := "minio:9000"
	accessKey := "ROOTUSERNAME"
	secretKey := "ROOTPASSWORD"
	dbConnectionString := "postgres://postgres:postgres@postgres:5432/postgres?sslmode=disable"
	kafkaHost := "kafka:9092"
	indexTopic := "index-input"
	processingTopic = "processing-input"
	indexResultTopic = "index-result"
	processingResult = "processing-result"
	topics := []string{"index-add", "processing-video", "processing-video-result"}
	kafkaProducer := internal.KafkaProducer([]string{kafkaHost}, indexTopic)

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
	uploadVideoHandler := handlers.NewUploadVideoHandler(db, minioClient, logger)
	getVideoHandler := handlers.NewGetVideoHandler(db, minioClient, logger)
	router := mux.NewRouter()
	router.HandleFunc("/video", uploadVideoHandler.Handle).Methods("POST")
	router.HandleFunc("/video/{id}", getVideoHandler.Handle).Methods("GET")
	logger.Info("Listening on port 9999")
	http.ListenAndServe(":9999", router)
}
