CREATE TABLE IF NOT EXISTS survey_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    source VARCHAR(50) DEFAULT 'web',
    browser VARCHAR(255),
    q1_response INT,
    q2_response INT,
    q3_response INT,
    q4_response INT,
    q5_response INT,
    q6_response INT,
    n1 FLOAT,
    n2 FLOAT,
    n3 FLOAT,
    plot_x FLOAT,
    plot_y FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);