-- Create the ping_results table
CREATE TABLE IF NOT EXISTS ping_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    url VARCHAR(255) NOT NULL,
    ip INET,
    status VARCHAR(50) NOT NULL,
    response_time_ms DECIMAL(10, 2),
    count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_ping_results_timestamp ON ping_results(timestamp);
CREATE INDEX idx_ping_results_url ON ping_results(url);
CREATE INDEX idx_ping_results_status ON ping_results(status);
CREATE INDEX idx_ping_results_url_timestamp ON ping_results(url, timestamp);

-- Create a view for latest status per URL
CREATE VIEW latest_ping_status AS
SELECT DISTINCT ON (url)
    url,
    ip,
    status,
    response_time_ms,
    timestamp,
    count
FROM ping_results
ORDER BY url, timestamp DESC;

-- Sample data (optional - remove if not needed)
INSERT INTO ping_results (timestamp, url, ip, status, response_time_ms, count) VALUES
('2024-01-01 10:00:00', 'google.com', '8.8.8.8', 'Success', 15.5, 1),
('2024-01-01 10:00:30', 'google.com', '8.8.8.8', 'Success', 16.2, 2);