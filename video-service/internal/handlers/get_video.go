package handlers

import (
	"encoding/json"
	"net/http"
	"video-service/internal"

	"github.com/gorilla/mux"
	"github.com/minio/minio-go/v7"
	"github.com/sirupsen/logrus"
)

type GetVideoHandler struct {
	db          *internal.Postgres
	logger      *logrus.Logger
	minioClient *minio.Client
}

func NewGetVideoHandler(db *internal.Postgres, minioClient *minio.Client, logger *logrus.Logger) *GetVideoHandler {
	return &GetVideoHandler{db: db, logger: logger, minioClient: minioClient}
}

func (h *GetVideoHandler) Handle(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	h.logger.Info(vars)
	videoId := vars["id"]
	h.logger.Info("Get video", "videoId", videoId)
	video := &internal.Video{}
	err := h.db.GetVideo(videoId, video)
	if err != nil {
		h.logger.Error(err)
		http.Error(w, "Video not found", http.StatusInternalServerError)
		return
	}
	responseBody, _ := json.Marshal(video)
	w.Write(responseBody)
	w.WriteHeader(http.StatusOK)
}
