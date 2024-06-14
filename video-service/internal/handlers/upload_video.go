package handlers

import (
	"context"
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
	"video-service/internal"

	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"github.com/segmentio/kafka-go"
	"github.com/sirupsen/logrus"
)

const (
	bucketName = "video-service-bucket"
)

type Response struct {
	UUID string `json:"uuid"`
}

type UploadVideoHandler struct {
	db                 *internal.Postgres
	logger             *logrus.Logger
	minioClient        *minio.Client
	indexProducer      *kafka.Writer
	processingProducer *kafka.Writer
}

type KafkaMessage struct {
	UUID  string `json:"uuid"`
	S3URL string `json:"s3_url"`
	MD5   string `json:"md5"`
}

func NewUploadVideoHandler(db *internal.Postgres, minioClient *minio.Client, logger *logrus.Logger, indexProducer *kafka.Writer, processingProducer *kafka.Writer) *UploadVideoHandler {
	return &UploadVideoHandler{db: db, logger: logger, minioClient: minioClient, indexProducer: indexProducer, processingProducer: processingProducer}
}

func isVideoExist(db *internal.Postgres, md5Hash string) (bool, error) {
	var video internal.Video
	err := db.GetVideoByMD5(md5Hash, &video)
	if err != nil {
		return false, err
	}
	return true, nil
}

func writeKafkaMessage(producer *kafka.Writer, kafkaMessage *KafkaMessage) error {
	kafkaMessageBytes, _ := json.Marshal(kafkaMessage)

	producer.WriteMessages(context.Background(), []kafka.Message{
		kafka.Message{
			Value: kafkaMessageBytes,
		},
	}...,
	)
	return nil
}

func (h *UploadVideoHandler) Handle(w http.ResponseWriter, r *http.Request) {
	isIndex := r.FormValue("index") == "true"
	videoName := r.FormValue("name")
	if videoName == "" {
		videoName = fmt.Sprintf("%d.mp4", time.Now().Unix())
	}

	file, header, err := r.FormFile("video")
	if err != nil {
		h.logger.Error(err)
		http.Error(w, "Invalid file", http.StatusBadRequest)
		return
	}
	defer file.Close()
	// Compute MD5 hash
	hash := md5.New()
	if _, err = io.Copy(hash, file); err != nil {
		h.logger.Error(err)
		http.Error(w, "Unable to read file", http.StatusInternalServerError)
		return
	}
	md5Hash := hex.EncodeToString(hash.Sum(nil))
	isVideoExist, err := isVideoExist(h.db, md5Hash)
	if err != nil {
		h.logger.Error(err)
	}
	if isVideoExist {
		h.logger.Error("Video already exist")
		http.Error(w, "Video already exist", http.StatusBadRequest)
		return
	}

	// We need to rewind file reader
	file.Seek(0, io.SeekStart)

	_, err = h.minioClient.PutObject(context.Background(), bucketName, videoName, file, header.Size,
		minio.PutObjectOptions{ContentType: "video/mp4"})
	if err != nil {
		h.logger.Error(err)
		http.Error(w, "Unable to upload file", http.StatusInternalServerError)
		return
	}
	s3URL := fmt.Sprintf("%s/%s/%s", h.minioClient.EndpointURL(), bucketName, videoName)
	if !isIndex {
		video := &internal.Video{
			Name:        videoName,
			VideoID:     uuid.New().String(),
			Duration:    0,
			Size:        int(header.Size),
			IsProcessed: false,
			S3URL:       s3URL,
			MD5:         md5Hash,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}
		err = h.db.InsertVideo(video)
		if err != nil {
			h.logger.Error(err)
			http.Error(w, "Unable to insert video", http.StatusInternalServerError)
			return
		}

		kafkaMessage := &KafkaMessage{
			UUID:  video.VideoID,
			S3URL: s3URL,
			MD5:   md5Hash,
		}
		err = writeKafkaMessage(h.indexProducer, kafkaMessage)
		if err != nil {
			h.logger.Error(err)
			http.Error(w, "internal error", http.StatusInternalServerError)
			return
		}
		response := &Response{
			UUID: video.VideoID,
		}
		responseBody, _ := json.Marshal(response)
		w.Write(responseBody)
		w.WriteHeader(http.StatusOK)
		return
	}
	indexVideo := &internal.IndexVideo{
		UUID:      uuid.New().String(),
		S3URL:     s3URL,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err = h.db.InsertIndexVideo(indexVideo)
	if err != nil {
		h.logger.Error(err)
		http.Error(w, "Unable to insert index video", http.StatusInternalServerError)
		return
	}

	kafkaMessage := &KafkaMessage{
		UUID:  indexVideo.UUID,
		S3URL: s3URL,
		MD5:   md5Hash,
	}
	err = writeKafkaMessage(h.indexProducer, kafkaMessage)
	fmt.Fprintf(w, "File uploaded successfully")
	w.WriteHeader(http.StatusOK)
}
