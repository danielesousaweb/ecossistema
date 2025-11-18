-- CAS Tecnologia Ecosystem - MySQL 8.0 Schema
-- Migration from MongoDB to MySQL

-- Drop existing tables if they exist
DROP TABLE IF EXISTS webhook_events;
DROP TABLE IF EXISTS sync_logs;
DROP TABLE IF EXISTS status_checks;
DROP TABLE IF EXISTS acf_schema;
DROP TABLE IF EXISTS hemera_products;

-- Main products table
CREATE TABLE hemera_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unopim_id INT NOT NULL UNIQUE,
    sku VARCHAR(100) NOT NULL UNIQUE,
    status ENUM('active', 'inactive', 'discontinued', 'archived') DEFAULT 'active',
    product_type VARCHAR(50) DEFAULT 'simple',
    title VARCHAR(255) NOT NULL,
    
    -- JSON columns for dynamic data
    attributes JSON,
    relationships JSON,
    categories JSON,
    
    -- Graph data
    graph_node JSON,
    graph_edges JSON,
    
    -- Metadata
    checksum VARCHAR(32) NOT NULL,
    completeness_score INT,
    
    -- Timestamps
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    synced_at DATETIME NOT NULL,
    
    -- Indexes
    INDEX idx_sku (sku),
    INDEX idx_status (status),
    INDEX idx_unopim_id (unopim_id),
    INDEX idx_checksum (checksum),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ACF Schema definitions
CREATE TABLE acf_schema (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(100) NOT NULL UNIQUE,
    label VARCHAR(255),
    type VARCHAR(50) NOT NULL,
    is_relationship BOOLEAN DEFAULT FALSE,
    is_required BOOLEAN DEFAULT FALSE,
    is_filterable BOOLEAN DEFAULT TRUE,
    position INT DEFAULT 0,
    options JSON,
    detected_at DATETIME,
    
    INDEX idx_code (code),
    INDEX idx_type (type),
    INDEX idx_is_relationship (is_relationship)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Webhook events
CREATE TABLE webhook_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    data JSON,
    checksum VARCHAR(32),
    timestamp DATETIME NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    
    INDEX idx_event_type (event_type),
    INDEX idx_entity_id (entity_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_processed (processed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sync logs
CREATE TABLE sync_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    action VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    message TEXT,
    duration_ms INT,
    timestamp DATETIME NOT NULL,
    
    FOREIGN KEY (product_id) REFERENCES hemera_products(id) ON DELETE SET NULL,
    INDEX idx_product_id (product_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Status checks
CREATE TABLE status_checks (
    id VARCHAR(36) PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
