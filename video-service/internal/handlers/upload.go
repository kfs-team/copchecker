package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/minio/minio-go/v7"
	"github.com/segmentio/kafka-go"
)

type UploadHandler struct {
	kafkaClient *kafka.Client
	minioClient *minio.Client
}

func NewUploadHandler(kafkaClient *kafka.Client, minioClient *minio.Client) *UploadHandler {
	return &UploadHandler{
		kafkaClient: kafkaClient,
		minioClient: minioClient,
	}
}

func (h *UploadHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	var err error
	if err = json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if req.Partition == 0 {
		http.Error(w, "Partition must be greater than 0", http.StatusBadRequest)
		return
	}

	if req.Offset == 0 {
		http.Error(w, "Offset must be greater than 0", http.StatusBadRequest)
		return
	}

	if req.Partition > req.Partitions {
		http.Error(w, "Partition must be less than or equal to Partitions", http.StatusBadRequest)
		return
	}

	if req.Offset > req.Partitions {
		http.Error(w, "Offset must be less than or equal to Partitions", http.StatusBadRequest)
		return
	}

}
