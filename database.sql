
-- CivicTrack+ Final Database Schema
-- Optimized for Consolidated Dashboard and Multi-Department Workflow

-- 1. Create the Database
CREATE DATABASE IF NOT EXISTS civitrack_db;
USE civitrack_db;

-- 2. Create Users Table
-- Stores citizens, department officials, and administrators
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    place VARCHAR(100),
    role VARCHAR(50) DEFAULT 'citizen' -- Roles: 'citizen', 'department', 'admin'
);

-- 3. Create Complaints Table
-- Stores all complaint details, evidence, and tracking information
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    department VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    incident_date DATETIME,
    incident_location VARCHAR(255),
    image VARCHAR(255),          -- Filename of evidence photo
    video VARCHAR(255),          -- Filename of evidence video
    resolved_image VARCHAR(255), -- Filename of resolution proof photo
    status VARCHAR(50) DEFAULT 'Pending', -- Statuses: 'Pending', 'In Progress', 'Assigned', 'Resolved'
    tracking_id VARCHAR(50),     -- Formatted ID (e.g., PWD-001)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Initial Setup Data
-- Clear existing administrative accounts to avoid duplicates during setup
DELETE FROM users WHERE role IN ('admin', 'department');

-- Create Default Administrator
-- Password: Admin@123 (meets requirements: 6+ chars, uppercase, special char)
INSERT INTO users (name, email, password, phone, place, role) 
VALUES ('admin', 'admin@civitrack.com', 'Admin123', '0000000000', 'Central Office', 'admin');

-- Create Department Accounts
-- These names must match the departments defined in the application logic
-- All passwords meet requirements: 6+ chars, uppercase letter, special character
INSERT INTO users (name, email, password, phone, place, role) VALUES 
('Road / PWD', 'road@civic.com', 'Road123', '0000000000', 'Road Maintenance Dept', 'department'),
('Water Authority', 'water@civic.com', 'Water123', '0000000000', 'Water Supply Dept', 'department'),
('Municipality', 'muni@civic.com', 'Muni123', '0000000000', 'Municipal Corporation', 'department'),
('Green Services', 'green@civic.com', 'Green123', '0000000000', 'Environment & Parks Dept', 'department');
