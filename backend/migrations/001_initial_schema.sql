-- AI Office Initial Schema (001_initial_schema.sql)
-- SQLite WAL High Performance Schema

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    director_name TEXT NOT NULL,
    mission TEXT NOT NULL,
    kpi_metrics TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department_id TEXT NOT NULL REFERENCES departments(id),
    role TEXT NOT NULL,
    hierarchy_level TEXT NOT NULL, -- 'MANAGER', 'DIRECTOR', 'SPECIALIST'
    status TEXT NOT NULL DEFAULT 'IDLE', -- 'IDLE', 'WORKING', 'PAUSED', 'FAILED', 'COMPLETED'
    current_task_id TEXT,
    current_provider TEXT,
    current_model TEXT,
    tokens_input INTEGER NOT NULL DEFAULT 0,
    tokens_output INTEGER NOT NULL DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    department_id TEXT NOT NULL REFERENCES departments(id),
    assigned_agent_id TEXT REFERENCES agents(id),
    status TEXT NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'BLOCKED'
    priority TEXT NOT NULL DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    progress_pct INTEGER NOT NULL DEFAULT 0,
    payload TEXT,
    result TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agents(id),
    department_id TEXT NOT NULL REFERENCES departments(id),
    action_type TEXT NOT NULL,
    destination TEXT NOT NULL,
    payload TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    risk_level TEXT NOT NULL DEFAULT 'MEDIUM',
    cost REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'APPROVED', 'REJECTED', 'EXECUTED', 'EXPIRED'
    decision_comment TEXT,
    decided_by TEXT,
    decided_at TIMESTAMP,
    execution_status TEXT, -- 'PENDING', 'SUCCESS', 'FAILED'
    execution_result TEXT,
    executed_at TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);
CREATE INDEX IF NOT EXISTS idx_approvals_hash ON approvals(payload_hash);

CREATE TABLE IF NOT EXISTS audit_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actor TEXT NOT NULL,
    department_id TEXT,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_hash TEXT,
    details TEXT
);

CREATE TABLE IF NOT EXISTS social_accounts (
    platform TEXT PRIMARY KEY,
    account_id TEXT,
    username TEXT,
    connected INTEGER NOT NULL DEFAULT 0,
    permissions TEXT,
    encrypted_token TEXT,
    token_expires_at TIMESTAMP,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    report_type TEXT NOT NULL,
    department_id TEXT,
    reporting_period TEXT,
    content TEXT NOT NULL,
    kpis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    provenance TEXT NOT NULL,
    source_ref TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS executive_meetings (
    id TEXT PRIMARY KEY,
    meeting_type TEXT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    status TEXT NOT NULL DEFAULT 'SCHEDULED',
    minutes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed Initial 8 Departments
INSERT OR IGNORE INTO departments (id, name, director_name, mission, kpi_metrics) VALUES
('research', 'Research & Intelligence', 'Dr. Aris Vance', 'Market scanning, competitive intelligence, academic research, and factual grounding.', '{"accuracy": 0.98, "sources_verified": 100}'),
('technology', 'Technology & Engineering', 'Marcus Sterling', 'Architecture design, code implementation, automated testing, and infrastructure health.', '{"uptime": 0.999, "test_pass_rate": 1.0}'),
('marketing', 'Marketing & Communications', 'Elena Rostova', 'Campaign ideation, audience research, copy drafting, and social growth.', '{"engagement_rate": 0.05, "campaign_roi": 0.0}'),
('finance', 'Finance & Economic Guardrails', 'Cassian Drake', 'Zero-cost enforcement, quota audit, budget simulation, and unit economics.', '{"cost_compliance": 1.0, "quota_efficiency": 0.95}'),
('operations', 'Operations & Workflow Logistics', 'Tariq Benali', 'Inter-departmental pipeline execution, task routing, and scheduler resilience.', '{"throughput": 150, "sla_compliance": 0.99}'),
('creative', 'Creative & Visual Studio', 'Lyra Silvers', 'Visual asset prompts, storyboard composition, video scripting, and aesthetic polish.', '{"aesthetic_score": 9.5, "brand_consistency": 1.0}'),
('strategy', 'Strategy & Growth Governance', 'Kaelen Thorne', 'Long-term roadmapping, organizational alignment, risk matrix modeling, and CEO escalation.', '{"alignment_index": 0.97, "risk_mitigation": 1.0}'),
('hr', 'Human Resources & Workforce Optimization', 'Sora Tanaka', 'Dynamic specialist agent lifecycle, prompt calibration, and cognitive load balancing.', '{"workforce_utilization": 0.85, "agent_health": 1.0}');

-- Seed Central AI Manager
INSERT OR IGNORE INTO agents (id, name, department_id, role, hierarchy_level, status, current_provider, current_model) VALUES
('mgr-001', 'Nova Prime (AI Manager)', 'operations', 'Chief AI Orchestrator', 'MANAGER', 'IDLE', 'openrouter', 'meta-llama/llama-3.2-3b-instruct:free');
