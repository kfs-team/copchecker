CREATE TABLE IF NOT EXISTS processing (
    processing_id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    intervals jsonb NOT NULL,
    valid BOOLEAN NOT NULL DEFAULT TRUE,
    start_at TIMESTAMP NOT NULL,
    end_at TIMESTAMP NOT NULL
);
