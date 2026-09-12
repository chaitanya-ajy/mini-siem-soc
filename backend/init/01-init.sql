-- Mini SIEM & SOC Database Initialization
-- This file is executed automatically by MySQL on first startup

CREATE DATABASE IF NOT EXISTS siemdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE siemdb;

-- Create tables (also managed by SQLAlchemy, but this ensures init works)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    source_ip VARCHAR(45),
    dest_ip VARCHAR(45),
    source_port INT,
    dest_port INT,
    protocol VARCHAR(20),
    action VARCHAR(100),
    severity VARCHAR(20) DEFAULT 'info',
    raw_log TEXT,
    parsed_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'open',
    source_log_id INT,
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (source_log_id) REFERENCES logs(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'new',
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS alert_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    condition_field VARCHAR(50) NOT NULL,
    operator VARCHAR(20) NOT NULL,
    value VARCHAR(255) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed default admin user (password: admin123)
INSERT INTO users (username, email, password_hash, role)
VALUES (
    'admin',
    'admin@minisiem.local',
    'admin123',
    'admin'
)
ON DUPLICATE KEY UPDATE username = username;

-- Seed default alert rules
INSERT INTO alert_rules (name, condition_field, operator, value, severity)
VALUES
    ('SSH Brute Force - Failed Password', 'action', 'contains', 'failed password', 'high'),
    ('SQL Injection Pattern', 'raw_log', 'regex', 'OR 1=1|DROP TABLE|UNION SELECT', 'critical'),
    ('External Denied Traffic', 'severity', 'equals', 'high', 'medium')
ON DUPLICATE KEY UPDATE name = name;
