package main

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/gorilla/mux"
	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
	"github.com/sirupsen/logrus"
)

const (
	bucketName = "video-service-bucket"
)

var minioClient *minio.Client
var logger *logrus.Logger

func uploadVideoHandler(w http.ResponseWriter, r *http.Request) {
	objectName := fmt.Sprintf("%d.mp4", time.Now().Unix())
	file, header, err := r.FormFile("video")
	if err != nil {
		logger.Error(err)
		http.Error(w, "Invalid file", http.StatusBadRequest)
		return
	}
	defer file.Close()
	_, err = minioClient.PutObject(context.Background(), bucketName, objectName, file, header.Size,
		minio.PutObjectOptions{ContentType: "video/mp4"})
	if err != nil {
		logger.Error(err)
		http.Error(w, "Unable to upload file", http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "File uploaded successfully")
	w.WriteHeader(http.StatusOK)
}

func main() {
	// dbConnectionString := "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable"
	logger = logrus.New()
	logger.SetLevel(logrus.DebugLevel)
	logger.Info("Starting service")
	minioHost := "localhost:9000"
	accessKey := "ROOTUSERNAME"
	secretKey := "ROOTPASSWORD"
	var err error
	minioClient, err = minio.New(minioHost, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
		Secure: false,
	})
	if err != nil {
		logger.Fatal(err)
	}
	router := mux.NewRouter()
	router.HandleFunc("/upload", uploadVideoHandler).Methods("POST")
	logger.Info("Listening on port 9999")
	http.ListenAndServe(":9999", router)
}
