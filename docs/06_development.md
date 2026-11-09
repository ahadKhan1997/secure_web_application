# DB creation:
## 1. DB Creation:
    CREATE DATABASE telecom_db;

## 2. Defining Enum Types
    CREATE TYPE user_role AS ENUM ('subscriber', 'admin');
    CREATE TYPE request_status AS ENUM ('pending', 'approved', 'rejected', 'cancelled');
    CREATE TYPE swap_type AS ENUM ('physical_to_esim', 'esim_replacement', 'device_change');

## 3. Creating Users Table
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        phone_number VARCHAR(20) UNIQUE NOT NULL,
        role user_role NOT NULL DEFAULT 'subscriber',
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

## 4. Creating SIM Swap Requests Table
    CREATE TABLE sim_swap_requests (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        target_msisdn VARCHAR(20) NOT NULL,
        current_iccid VARCHAR(22) NOT NULL,
        new_iccid VARCHAR(22),
        reason TEXT NOT NULL,
        swap_type swap_type NOT NULL,
        status request_status NOT NULL DEFAULT 'pending',
        admin_notes TEXT,
        processed_by INT REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

## 5. Creating Immutable Audit Logs Table
    CREATE TABLE audit_logs (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(id) ON DELETE SET NULL,
        action VARCHAR(100) NOT NULL,
        ip_address VARCHAR(45) NOT NULL,
        user_agent TEXT,
        details JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

## 6. Creating Performance and Search Indexes
    CREATE INDEX idx_users_email ON users(email);
    CREATE INDEX idx_swap_requests_user_id ON sim_swap_requests(user_id);
    CREATE INDEX idx_swap_requests_status ON sim_swap_requests(status);
    CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);

## 7. Creating admin and first user accounts
    INSERT INTO users (email, password_hash, full_name, phone_number, role) VALUES
    ('admin@telecom.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQxMjM0NTY3OA$9v9X2P3nLzJ1F2R5K8W9E0T1Y2U3I4O5P6A7S8D9F0G', 'System Administrator', '+353870000000', 'admin'),
    ('subscriber@telecom.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQxMjM0NTY3OA$1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2', 'Ahad Khan', '+353871234567', 'subscriber');
