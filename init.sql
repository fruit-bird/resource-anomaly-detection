CREATE TABLE IF NOT EXISTS metrics (
    time TIMESTAMPTZ NOT NULL,
    cpu_percent FLOAT,
    memory_percent FLOAT,
    disk_usage FLOAT,
    bytes_sent BIGINT,
    bytes_recv BIGINT,
    PRIMARY KEY (time)
);
SELECT create_hypertable('metrics', 'time');