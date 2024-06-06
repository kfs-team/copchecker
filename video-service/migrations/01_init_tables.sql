CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    video_id VARCHAR(255) NOT NULL,
    duration INT NOT NULL,
    size INT NOT NULL,
    is_processed BOOLEAN NOT NULL,
    s3_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE index_videos (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(255) NOT NULL,
    s3_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
