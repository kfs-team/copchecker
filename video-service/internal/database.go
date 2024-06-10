package internal

import (
	"time"

	"github.com/jmoiron/sqlx"
)

type Postgres struct {
	db *sqlx.DB
}

type Video struct {
	Name        string    `db:"name" json:"name"`
	VideoID     string    `db:"video_id" json:"video_id"`
	Duration    int       `db:"duration,omitempty" json:"duration"`
	Size        int       `db:"size,omitempty" json:"size"`
	IsProcessed bool      `db:"is_processed,omitempty" json:"is_processed"`
	S3URL       string    `db:"s3_url,omitempty" json:"s3_url"`
	MD5         string    `db:"md5,omitempty" json:"md5"`
	CreatedAt   time.Time `db:"created_at,omitempty" json:"created_at"`
	UpdatedAt   time.Time `db:"updated_at,omitempty" json:"updated_at"`
}

type IndexVideo struct {
	UUID      string    `db:"uuid"`
	S3URL     string    `db:"s3_url"`
	CreatedAt time.Time `db:"created_at"`
	UpdatedAt time.Time `db:"updated_at"`
}

func NewPostgres(db *sqlx.DB) *Postgres {
	return &Postgres{db: db}
}

func (p *Postgres) InsertVideo(video *Video) error {
	_, err := p.db.NamedExec("INSERT INTO videos (name, video_id, duration, size, is_processed, s3_url, md5, created_at, updated_at) VALUES (:name, :video_id, :duration, :size, :is_processed, :s3_url, :md5, :created_at, :updated_at)", video)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) GetVideoByName(name string, video *Video) error {
	err := p.db.Get(video, "SELECT name, video_id, duration, size, is_processed, s3_url, md5, created_at, updated_at FROM videos WHERE name = $1", name)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) GetVideoByMD5(md5 string, video *Video) error {
	err := p.db.Get(video, "SELECT name, video_id, duration, size, is_processed, s3_url, md5, created_at, updated_at FROM videos WHERE md5 = $1", md5)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) GetVideo(id string, video *Video) error {
	err := p.db.Get(video, "SELECT name, video_id, duration, size, is_processed, s3_url, md5, created_at, updated_at FROM videos WHERE video_id = $1", id)
	if err != nil {
		return err
	}
	return nil
}

func (p *Postgres) InsertIndexVideo(video *IndexVideo) error {
	_, err := p.db.NamedExec("INSERT INTO index_videos (uuid, s3_url, created_at, updated_at) VALUES (:uuid, :s3_url, :created_at, :updated_at)", video)
	if err != nil {
		return err
	}
	return nil
}
