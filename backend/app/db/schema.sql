-- USERS & SESSIONS
CREATE TABLE IF NOT EXISTS users (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  email         VARCHAR(255) NOT NULL UNIQUE,
  full_name     VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('doctor','assistant') NOT NULL DEFAULT 'assistant',
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sessions (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  session_id    CHAR(36) NOT NULL UNIQUE,            -- UUIDv4
  user_id       BIGINT NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at    DATETIME NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- CSV UPLOADS
CREATE TABLE IF NOT EXISTS csv_uploads (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id       BIGINT,
  filename      VARCHAR(255) NOT NULL,
  rows_parsed   INT NOT NULL DEFAULT 0,
  rows_loaded   INT NOT NULL DEFAULT 0,
  status        ENUM('queued','processing','completed','failed') NOT NULL DEFAULT 'queued',
  error_msg     TEXT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- PATIENTS & OBSERVATIONS
CREATE TABLE IF NOT EXISTS patients (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  patient_uid   VARCHAR(64) NOT NULL UNIQUE,
  first_name    VARCHAR(64) NOT NULL,
  last_name     VARCHAR(64) NOT NULL,
  age           INT NOT NULL,
  sex           ENUM('M','F','O') NOT NULL DEFAULT 'O',
  contact_phone VARCHAR(32) NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS patient_observations (
  id               BIGINT PRIMARY KEY AUTO_INCREMENT,
  patient_id       BIGINT NOT NULL,
  obs_type         VARCHAR(64) NOT NULL,
  value_num        DOUBLE NULL,
  value_text       VARCHAR(255) NULL,
  unit             VARCHAR(32) NULL,
  observed_at      DATETIME NOT NULL,
  source_upload_id BIGINT NULL,
  FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  FOREIGN KEY (source_upload_id) REFERENCES csv_uploads(id) ON DELETE SET NULL,
  INDEX idx_patient_obs (patient_id, obs_type, observed_at)
) ENGINE=InnoDB;
