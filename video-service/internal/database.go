package internal

import (
	"time"

	"github.com/jmoiron/sqlx"
)

type Postgres struct {
	db *sqlx.DB
}

type ProcessingResult struct {
	VideoId      string     `json:"video_id"`
	ProcessingId int        `json:"processing_id"`
	Intervals    []Interval `json:"intervals"`
	Valid        bool       `json:"valid"`
	Start        time.Time  `json:"start_at"`
	End          time.Time  `json:"end_at"`
}

type Processing struct {
	Name                  string     `json:"name" db:"name"`
	ThumbnailUrl          string     `json:"thumbnail_url" db:"thumbnail_url"`
	VideoId               string     `json:"video_id" db:"video_id"`
	HasCopyrightViolences bool       `json:"has_copyright_violences" db:"has_copyright_violences"`
	ProcessingId          int        `json:"processing_id" db:"processing_id"`
	Intervals             []Interval `json:"intervals" db:"intervals"`
	Start                 time.Time  `json:"start_at" db:"start_at"`
	End                   time.Time  `json:"end_at" db:"end_at"`
}

type Video struct {
	Name        string    `db:"name" json:"name"`
	VideoID     string    `db:"video_id" json:"video_id"`
	Duration    int       `db:"duration,omitempty" json:"duration"`
	Size        int       `db:"size,omitempty" json:"size"`
	IsProcessed bool      `db:"is_processed,omitempty" json:"is_processed"`
	S3URL       string    `db:"s3_url,omitempty" json:"s3_url"`
	MD5         string    `db:"md5,omitempty" json:"md5"`
	BucketName  string    `db:"bucket_name,omitempty" json:"bucket_name"`
	VideoName   string    `db:"video_name,omitempty" json:"video_name"`
	CreatedAt   time.Time `db:"created_at,omitempty" json:"created_at"`
	UpdatedAt   time.Time `db:"updated_at,omitempty" json:"updated_at"`
}

type IndexVideo struct {
	UUID       string    `db:"uuid"`
	S3URL      string    `db:"s3_url"`
	MD5        string    `db:"md5"`
	BucketName string    `db:"bucket_name"`
	VideoName  string    `db:"video_name"`
	CreatedAt  time.Time `db:"created_at"`
	UpdatedAt  time.Time `db:"updated_at"`
}

func NewPostgres(db *sqlx.DB) *Postgres {
	return &Postgres{db: db}
}

func (p *Postgres) InsertVideo(video *Video) error {
	_, err := p.db.NamedExec("INSERT INTO videos (name, video_id, duration, size, is_processed, s3_url, md5, bucket_name, video_name, created_at, updated_at) VALUES (:name, :video_id, :duration, :size, :is_processed, :s3_url, :md5, :bucket_name, :video_name, :created_at, :updated_at)", video)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) GetVideoByName(name string, video *Video) error {
	err := p.db.Get(video, "SELECT name, video_id, duration, size, is_processed, s3_url, md5, bucket_name, video_name, created_at, updated_at FROM videos WHERE name = $1", name)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) GetVideoByMD5(md5 string, video *Video) error {
	err := p.db.Get(video, "SELECT name, video_id, duration, size, is_processed, s3_url, md5, bucket_name, video_name, created_at, updated_at FROM videos WHERE md5 = $1", md5)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) GetVideo(id string, video *Video) error {
	err := p.db.Get(video, "SELECT name, video_id, duration, size, is_processed, s3_url, md5, bucket_name, video_name, created_at, updated_at FROM videos WHERE video_id = $1", id)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) InsertIndexVideo(video *IndexVideo) error {
	_, err := p.db.NamedExec("INSERT INTO index_videos (uuid, s3_url, md5, bucket_name, video_name, created_at, updated_at) VALUES (:uuid, :s3_url, :md5, :bucket_name, :video_name, :created_at, :updated_at)", video)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) InsertProcessing(processing *ProcessingResultMessage) error {
	_, err := p.db.NamedExec("INSERT INTO processing (video_id, intervals, valid, start_at, end_at) VALUES (:video_id, :intervals, :valid, :start_at, :end_at)", processing)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) GetLastProcessingByVideoId(videoId string, processing *ProcessingResult) error {
	err := p.db.Get(processing, "SELECT video_id, processing_id, intervals, valid, start_at, end_at FROM processing WHERE video_id = $1 ORDER BY start DESC LIMIT 1", videoId)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) UpdateIndexVideoByVideoId(videoId string) error {
	_, err := p.db.Exec("UPDATE index_videos SET updated_at = NOW(), added = true WHERE uuid = $1", videoId)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) UpdateVideoByVideoId(videoId string) error {
	_, err := p.db.Exec("UPDATE videos SET updated_at = NOW(), is_processed = true WHERE video_id = $1", videoId)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) GetAllProcessings() ([]Processing, error) {
	query := `
SELECT v.name as name,
	v.s3_url as thumbnail_url,
	v.video_id as video_id,
	valid as has_copyright_violences,
	processing_id,
	start_at,
	end_at,
	intervals
	FROM processing
	left join videos v on processing.video_id = v.video_id
	`
	var processings []Processing
	err := p.db.Select(&processings, query)
	if err != nil {
		return nil, err
	}
	return processings, nil
}
