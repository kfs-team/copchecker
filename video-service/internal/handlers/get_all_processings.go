package handlers

import (
	"encoding/json"
	"net/http"
	"video-service/internal"

	"github.com/sirupsen/logrus"
)

type GetAllProcessingsHandler struct {
	db     *internal.Postgres
	logger *logrus.Logger
}

func NewGetAllProcessingsHandler(db *internal.Postgres, logger *logrus.Logger) *GetAllProcessingsHandler {
	return &GetAllProcessingsHandler{db: db, logger: logger}
}

func (h *GetAllProcessingsHandler) Handle(w http.ResponseWriter, r *http.Request) {
	processings, err := h.db.GetAllProcessings()
	if err != nil || len(processings) == 0 {
		h.logger.Error(err)
		http.Error(w, "Processing not found", http.StatusInternalServerError)
		return
	}
	responseBody, _ := json.Marshal(processings)
	w.Write(responseBody)
	w.WriteHeader(http.StatusOK)
}
