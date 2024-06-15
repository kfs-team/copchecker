ALTER TABLE videos ADD COLUMN bucket_name VARCHAR(255) NOT NULL DEFAULT 'video-service-bucket';
ALTER TABLE videos ADD COLUMN video_name VARCHAR(255) NOT NULL;

ALTER TABLE index_videos ADD COLUMN bucket_name VARCHAR(255) NOT NULL DEFAULT 'video-service-bucket';
ALTER TABLE index_videos ADD COLUMN video_name VARCHAR(255) NOT NULL;
