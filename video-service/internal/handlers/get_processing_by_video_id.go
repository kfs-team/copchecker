package handlers

import (
	"encoding/json"
	"net/http"
	"video-service/internal"

	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
)

type GetProcessingByVideoIdHandler struct {
	db     *internal.Postgres
	logger *logrus.Logger
}

func NewGetProcessingByVideoIdHandler(db *internal.Postgres, logger *logrus.Logger) *GetProcessingByVideoIdHandler {
	return &GetProcessingByVideoIdHandler{db: db, logger: logger}
}

func (h *GetProcessingByVideoIdHandler) Handle(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	h.logger.Info(vars)
	videoId := vars["id"]
	h.logger.Info("Get processing by video id, id:", videoId)
	processing := &internal.ProcessingResult{}
	err := h.db.GetLastProcessingByVideoId(videoId, processing)
	if err != nil {
		h.logger.Error(err)
		http.Error(w, "Processing not found", http.StatusInternalServerError)
		return
	}
	responseBody, _ := json.Marshal(processing)
	w.Write(responseBody)
	w.WriteHeader(http.StatusOK)
}
