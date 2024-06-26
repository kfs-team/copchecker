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
	bucketName      = "video-service-bucket"
	indexTopic      = "index-input"
	processingTopic = "processing-input"
	retiries        = 3
)

type Response struct {
	UUID string `json:"uuid"`
}

type UploadVideoHandler struct {
	db            *internal.Postgres
	logger        *logrus.Logger
	minioClient   *minio.Client
	kafkaProducer *kafka.Writer
}

type KafkaMessage struct {
	topic      string
	UUID       string `json:"uuid"`
	S3URL      string `json:"s3_url"`
	MD5        string `json:"md5"`
	BucketName string `json:"bucket_name"`
	VideoName  string `json:"video_name"`
}

func NewUploadVideoHandler(
	db *internal.Postgres,
	minioClient *minio.Client,
	logger *logrus.Logger,
	producer *kafka.Writer,
) *UploadVideoHandler {
	return &UploadVideoHandler{
		db:            db,
		logger:        logger,
		minioClient:   minioClient,
		kafkaProducer: producer,
	}
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
	var err error
	for i := 0; i < retiries; i++ {
		err = producer.WriteMessages(context.Background(), []kafka.Message{
			{
				Value: kafkaMessageBytes,
				Topic: kafkaMessage.topic,
			},
		}...)
		if err != nil {
			time.Sleep(time.Second)
			continue
		}
		return nil
	}
	return err
}

func (h *UploadVideoHandler) Handle(w http.ResponseWriter, r *http.Request) {
	isIndexStr := r.FormValue("index")
	h.logger.Info("isIndex: ", isIndexStr)
	isIndex := isIndexStr == "true"
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
	h.logger.Info("s3URL: ", s3URL)
	if !isIndex {
		video := &internal.Video{
			Name:        videoName,
			VideoID:     uuid.New().String(),
			Duration:    0,
			Size:        int(header.Size),
			IsProcessed: false,
			S3URL:       s3URL,
			MD5:         md5Hash,
			BucketName:  bucketName,
			VideoName:   videoName,
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
			topic:      processingTopic,
			UUID:       video.VideoID,
			S3URL:      s3URL,
			MD5:        md5Hash,
			BucketName: bucketName,
			VideoName:  videoName,
		}
		h.logger.Info("kafkaProcessingMessage: ", kafkaMessage)
		err = writeKafkaMessage(h.kafkaProducer, kafkaMessage)
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
		UUID:       uuid.New().String(),
		S3URL:      s3URL,
		MD5:        md5Hash,
		BucketName: bucketName,
		VideoName:  videoName,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}
	h.logger.Info("Inserting index video")
	err = h.db.InsertIndexVideo(indexVideo)
	if err != nil {
		h.logger.Error(err)
		http.Error(w, "Unable to insert index video", http.StatusInternalServerError)
		return
	}

	kafkaMessage := &KafkaMessage{
		topic:      indexTopic,
		UUID:       indexVideo.UUID,
		S3URL:      s3URL,
		MD5:        md5Hash,
		BucketName: bucketName,
		VideoName:  videoName,
	}
	h.logger.Info("kafkaIndexMessage: ", kafkaMessage)
	err = writeKafkaMessage(h.kafkaProducer, kafkaMessage)
	if err != nil {
		h.logger.Error(err)
		http.Error(w, "Unable to insert index video", http.StatusInternalServerError)
		return
	}
	fmt.Fprintf(w, "File uploaded successfully")
	w.WriteHeader(http.StatusOK)
}
