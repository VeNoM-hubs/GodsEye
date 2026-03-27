-- ================================================
-- GODSEYE FINAL DATABASE SETUP
-- Run this AFTER connecting to database:
-- \c godseye
-- ================================================

-- ================================
-- USERS
-- ================================
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    role VARCHAR(50) NOT NULL,
    access_level INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- RESOURCES
-- ================================
CREATE TABLE IF NOT EXISTS resources (
    resource_id VARCHAR(50) PRIMARY KEY,
    resource_name VARCHAR(120) NOT NULL,
    resource_type VARCHAR(30) NOT NULL,
    required_access_level INT NOT NULL,
    is_sensitive BOOLEAN DEFAULT FALSE
);

-- ================================
-- PHYSICAL LOGS
-- ================================
CREATE TABLE IF NOT EXISTS physical_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(resource_id) ON DELETE RESTRICT,
    access_status VARCHAR(20) NOT NULL,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- DIGITAL LOGS
-- ================================
CREATE TABLE IF NOT EXISTS digital_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(resource_id) ON DELETE RESTRICT,
    action_type VARCHAR(50) NOT NULL,
    raw_severity VARCHAR(20) NOT NULL,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- HONEYPOT LOGS
-- ================================
CREATE TABLE IF NOT EXISTS honeypot_logs (
    id BIGSERIAL PRIMARY KEY,
    honeypot_id VARCHAR(100) NOT NULL,
    honeypot_name VARCHAR(100) NOT NULL,
    honeypot_type VARCHAR(50) NOT NULL,
    attacker_ip VARCHAR(50) NOT NULL,
    attacker_port INT NOT NULL,
    target_port INT NOT NULL,
    username_attempted VARCHAR(200),
    password_attempted VARCHAR(200),
    commands_executed TEXT[],
    auth_success BOOLEAN DEFAULT FALSE,
    session_duration_ms INT DEFAULT 0,
    threat_level VARCHAR(20) DEFAULT 'MEDIUM',
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'chk_honeypot_threat_level'
    ) THEN
        ALTER TABLE honeypot_logs
        ADD CONSTRAINT chk_honeypot_threat_level
        CHECK (threat_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'));
    END IF;
END;
$$;

-- ================================
-- SIMPLE HONEYPOT COMMAND LOGS
-- ================================
CREATE TABLE IF NOT EXISTS honeypot_command_logs (
    id BIGSERIAL PRIMARY KEY,
    attacker_ip VARCHAR(50) NOT NULL,
    target_port INT NOT NULL,
    command_text TEXT,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (target_port >= 1 AND target_port <= 65535)
);

-- ================================
-- UNIFIED MAIN LOGS
-- ================================
CREATE TABLE IF NOT EXISTS main_logs (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(20) NOT NULL,
    source_ref_id BIGINT NOT NULL,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id),
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(resource_id),
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    event_time TIMESTAMP NOT NULL,
    correlation_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- MITRE TECHNIQUES
-- ================================
CREATE TABLE IF NOT EXISTS mitre_techniques (
    technique_id VARCHAR(20) PRIMARY KEY,
    technique_name VARCHAR(200) NOT NULL,
    tactic VARCHAR(100) NOT NULL
);

INSERT INTO mitre_techniques (technique_id, technique_name, tactic)
VALUES ('T1595', 'Active Scanning', 'Reconnaissance')
ON CONFLICT (technique_id) DO NOTHING;

-- ================================
-- THREATS
-- ================================
CREATE TABLE IF NOT EXISTS threats (
    threat_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id),
    threat_pattern VARCHAR(120) NOT NULL,
    mitre_id VARCHAR(20) REFERENCES mitre_techniques(technique_id),
    risk_score INT NOT NULL,
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    event_count INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- ================================
-- INDEXES (Performance)
-- ================================
CREATE INDEX IF NOT EXISTS idx_main_time ON main_logs(event_time);
CREATE INDEX IF NOT EXISTS idx_main_severity ON main_logs(severity);
CREATE INDEX IF NOT EXISTS idx_threat_user ON threats(user_id);
CREATE INDEX IF NOT EXISTS idx_physical_user ON physical_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_digital_user ON digital_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_honeypot_event_time ON honeypot_logs(event_time);
CREATE INDEX IF NOT EXISTS idx_honeypot_attacker_ip ON honeypot_logs(attacker_ip);
CREATE INDEX IF NOT EXISTS idx_honeypot_target_port ON honeypot_logs(target_port);
CREATE INDEX IF NOT EXISTS idx_honeypot_threat_level ON honeypot_logs(threat_level);
CREATE INDEX IF NOT EXISTS idx_hcmd_event_time ON honeypot_command_logs(event_time);
CREATE INDEX IF NOT EXISTS idx_hcmd_attacker_ip ON honeypot_command_logs(attacker_ip);
CREATE INDEX IF NOT EXISTS idx_hcmd_target_port ON honeypot_command_logs(target_port);

-- ================================================
-- TRIGGER: PHYSICAL → MAIN
-- ================================================
CREATE OR REPLACE FUNCTION insert_main_log_from_physical()
RETURNS TRIGGER AS $$
DECLARE
    required_level INT;
    user_level INT;
    computed_severity TEXT;
BEGIN
    SELECT required_access_level INTO required_level
    FROM resources WHERE resource_id = NEW.resource_id;

    SELECT access_level INTO user_level
    FROM users WHERE user_id = NEW.user_id;

    IF user_level < required_level OR NEW.access_status = 'DENIED' THEN
        computed_severity := 'HIGH';
    ELSE
        computed_severity := 'LOW';
    END IF;

    INSERT INTO main_logs (
        source,
        source_ref_id,
        user_id,
        resource_id,
        event_type,
        severity,
        event_time
    )
    VALUES (
        'PHYSICAL',
        NEW.id,
        NEW.user_id,
        NEW.resource_id,
        NEW.access_status,
        computed_severity,
        NEW.event_time
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_physical_to_main ON physical_logs;

CREATE TRIGGER trg_physical_to_main
AFTER INSERT ON physical_logs
FOR EACH ROW
EXECUTE FUNCTION insert_main_log_from_physical();

-- ================================================
-- TRIGGER: DIGITAL → MAIN
-- ================================================
CREATE OR REPLACE FUNCTION insert_main_log_from_digital()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO main_logs (
        source,
        source_ref_id,
        user_id,
        resource_id,
        event_type,
        severity,
        event_time
    )
    VALUES (
        'DIGITAL',
        NEW.id,
        NEW.user_id,
        NEW.resource_id,
        NEW.action_type,
        CASE
            WHEN NEW.raw_severity = 'HIGH' THEN 'HIGH'
            WHEN NEW.raw_severity = 'MEDIUM' THEN 'MEDIUM'
            ELSE 'LOW'
        END,
        NEW.event_time
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_digital_to_main ON digital_logs;

CREATE TRIGGER trg_digital_to_main
AFTER INSERT ON digital_logs
FOR EACH ROW
EXECUTE FUNCTION insert_main_log_from_digital();

-- ================================================
-- TRIGGER: MAIN → THREAT (Escalation Logic)
-- ================================================
CREATE OR REPLACE FUNCTION detect_threat()
RETURNS TRIGGER AS $$
DECLARE
    existing_id BIGINT;
BEGIN
    IF NEW.severity = 'HIGH' THEN

        SELECT threat_id INTO existing_id
        FROM threats
        WHERE user_id = NEW.user_id
        AND status = 'ACTIVE'
        AND last_seen > NOW() - INTERVAL '10 minutes'
        LIMIT 1;

        IF existing_id IS NOT NULL THEN
            UPDATE threats
            SET event_count = event_count + 1,
                risk_score = risk_score + 10,
                last_seen = NEW.event_time
            WHERE threat_id = existing_id;
        ELSE
            INSERT INTO threats (
                user_id,
                threat_pattern,
                mitre_id,
                risk_score,
                first_seen,
                last_seen
            )
            VALUES (
                NEW.user_id,
                'Unauthorized Access Pattern',
                'T1078',
                70,
                NEW.event_time,
                NEW.event_time
            );
        END IF;

        UPDATE main_logs
        SET correlation_flag = TRUE
        WHERE id = NEW.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_main_to_threat ON main_logs;

CREATE TRIGGER trg_main_to_threat
AFTER INSERT ON main_logs
FOR EACH ROW
EXECUTE FUNCTION detect_threat();

-- ================================================
-- TRIGGER: HONEYPOT → THREAT (Auto-escalation)
-- ================================================
CREATE OR REPLACE FUNCTION escalate_honeypot_hit()
RETURNS TRIGGER AS $$
DECLARE
    threat_user_id VARCHAR(50);
    existing_id BIGINT;
    computed_risk INT;
    computed_pattern VARCHAR(120);
BEGIN
    threat_user_id := 'HPOT_' || LEFT(REGEXP_REPLACE(NEW.honeypot_id, '[^A-Za-z0-9_]', '', 'g'), 45);

    INSERT INTO users (
        user_id,
        full_name,
        role,
        access_level,
        is_active
    )
    VALUES (
        threat_user_id,
        'Honeypot Sensor ' || LEFT(NEW.honeypot_id, 30),
        'SYSTEM',
        10,
        TRUE
    )
    ON CONFLICT (user_id) DO NOTHING;

    computed_risk := CASE
        WHEN NEW.threat_level = 'CRITICAL' THEN 95
        WHEN NEW.threat_level = 'HIGH' THEN 80
        WHEN NEW.threat_level = 'MEDIUM' THEN 60
        ELSE 50
    END;

    computed_pattern := LEFT(
        'Honeypot Interaction - ' || NEW.honeypot_type || ' on port ' || NEW.target_port ||
        ' from ' || NEW.attacker_ip,
        120
    );

    SELECT threat_id INTO existing_id
    FROM threats
    WHERE user_id = threat_user_id
      AND threat_pattern = computed_pattern
      AND status = 'ACTIVE'
      AND last_seen > NOW() - INTERVAL '10 minutes'
    LIMIT 1;

    IF existing_id IS NOT NULL THEN
        UPDATE threats
        SET event_count = event_count + 1,
            risk_score = LEAST(100, GREATEST(risk_score, computed_risk) + 5),
            last_seen = NEW.event_time
        WHERE threat_id = existing_id;
    ELSE
        INSERT INTO threats (
            user_id,
            threat_pattern,
            mitre_id,
            risk_score,
            first_seen,
            last_seen,
            status
        )
        VALUES (
            threat_user_id,
            computed_pattern,
            'T1595',
            computed_risk,
            NEW.event_time,
            NEW.event_time,
            'ACTIVE'
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- TRIGGER: HONEYPOT COMMAND NORMALIZER
-- ================================================
CREATE OR REPLACE FUNCTION normalize_honeypot_command()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.command_text IS NOT NULL THEN
        NEW.command_text := BTRIM(NEW.command_text);

        IF NEW.command_text = '' OR LOWER(NEW.command_text) = '(no data)' THEN
            NEW.command_text := NULL;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_honeypot_to_threat ON honeypot_logs;

CREATE TRIGGER trg_honeypot_to_threat
AFTER INSERT ON honeypot_logs
FOR EACH ROW
EXECUTE FUNCTION escalate_honeypot_hit();

DROP TRIGGER IF EXISTS trg_hcmd_normalize ON honeypot_command_logs;

CREATE TRIGGER trg_hcmd_normalize
BEFORE INSERT OR UPDATE ON honeypot_command_logs
FOR EACH ROW
EXECUTE FUNCTION normalize_honeypot_command();

-- ================================================
-- SETUP COMPLETE
-- ================================================

SELECT 'GodsEye final setup initialized successfully.' AS status; 