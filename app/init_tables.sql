CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    original_name VARCHAR(255),
    size INTEGER,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_type VARCHAR(255)
);