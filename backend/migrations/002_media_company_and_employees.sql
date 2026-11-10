-- AI Office Media Company Evolution (002_media_company_and_employees.sql)
-- SQLite WAL High Performance Schema for Autonomous Audiovisual Media Company

-- 1. Employees Registry & Live Office Board
CREATE TABLE IF NOT EXISTS employees (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    role TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'FREE', -- 'WORKING', 'FREE', 'WAITING_FOR_OWNER', 'STUCK', 'IN_MEETING', 'LEARNING', 'OFFLINE'
    current_task TEXT,
    current_project TEXT,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    current_blockers TEXT DEFAULT '[]', -- JSON array of strings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status);

-- 2. Employee Sessions Tracking
CREATE TABLE IF NOT EXISTS employee_sessions (
    session_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL REFERENCES employees(id),
    task_id TEXT,
    project_id TEXT,
    status TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    output_references TEXT DEFAULT '{}', -- JSON object with produced artifacts
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_emp_sessions_emp ON employee_sessions(employee_id);

-- 3. Employee XP Events & 10 Levels Progression
CREATE TABLE IF NOT EXISTS employee_xp_events (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL REFERENCES employees(id),
    task_id TEXT NOT NULL,
    xp_amount INTEGER NOT NULL,
    awarded_by TEXT NOT NULL, -- 'OWNER', 'SYSTEM_ACCEPTED'
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, task_id) -- Strict anti-duplicate XP award constraint
);

-- 4. Master Content Projects
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    topic TEXT NOT NULL,
    niche TEXT,
    target_audience TEXT,
    status TEXT NOT NULL DEFAULT 'DISCOVERY', -- 'DISCOVERY', 'STRATEGY', 'SCRIPTING', 'PRODUCTION', 'QUALITY_CONTROL', 'WAITING_FOR_OWNER', 'APPROVED', 'PUBLISHED', 'REJECTED'
    opportunity_score REAL DEFAULT 0.0,
    confidence_pct INTEGER DEFAULT 0,
    assigned_department TEXT,
    metadata TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- 5. Content Opportunities (Phase A Research)
CREATE TABLE IF NOT EXISTS content_opportunities (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    topic TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    evidence_sources TEXT NOT NULL DEFAULT '[]', -- JSON array of verified citations
    trend_relevance TEXT NOT NULL,
    competition_analysis TEXT,
    potential_formats TEXT NOT NULL DEFAULT '["SHORT_FORM", "LONG_FORM"]',
    risks TEXT,
    recommendation TEXT NOT NULL DEFAULT 'GO', -- 'GO', 'NO_GO'
    confidence_level REAL NOT NULL DEFAULT 0.85,
    status TEXT NOT NULL DEFAULT 'PENDING_REVIEW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Production Scripts (Phase C Scripting)
CREATE TABLE IF NOT EXISTS scripts (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    target_platform TEXT NOT NULL, -- 'YOUTUBE_SHORTS', 'TIKTOK', 'INSTAGRAM_REELS', 'FACEBOOK_REELS', 'YOUTUBE_LONG'
    target_format TEXT NOT NULL, -- 'VERTICAL_9_16', 'HORIZONTAL_16_9'
    target_duration_seconds INTEGER NOT NULL,
    hook TEXT NOT NULL,
    full_narration TEXT NOT NULL,
    thumbnail_concept TEXT,
    factual_citations TEXT DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Script Scene Sequences
CREATE TABLE IF NOT EXISTS scenes (
    id TEXT PRIMARY KEY,
    script_id TEXT NOT NULL REFERENCES scripts(id),
    scene_number INTEGER NOT NULL,
    duration_seconds REAL NOT NULL,
    visual_prompt TEXT NOT NULL,
    narration_chunk TEXT,
    audio_cues TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING'
);

CREATE INDEX IF NOT EXISTS idx_scenes_script ON scenes(script_id, scene_number);

-- 8. Production Jobs (Phase D Editing & FlowKit Integration)
CREATE TABLE IF NOT EXISTS production_jobs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    script_id TEXT REFERENCES scripts(id),
    engine TEXT NOT NULL DEFAULT 'FLOWKIT', -- 'FLOWKIT', 'GOOGLE_FLOW', 'FFMPEG_LOCAL'
    status TEXT NOT NULL DEFAULT 'WAITING_FOR_GENERATION',
    -- Granular statuses: 'WAITING_FOR_GENERATION', 'GENERATING', 'RENDERING', 'EDITING', 'QUALITY_CONTROL', 'COMPLETED', 'FAILED', 'BLOCKED_BY_QUOTA', 'WAITING_FOR_BROWSER', 'WAITING_FOR_OWNER'
    flowkit_job_id TEXT,
    progress_pct INTEGER DEFAULT 0,
    output_video_path TEXT,
    output_thumbnail_path TEXT,
    output_subtitles_path TEXT,
    qc_report TEXT DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_prod_jobs_status ON production_jobs(status);

-- 9. Master Media Assets Library
CREATE TABLE IF NOT EXISTS media_assets (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    asset_type TEXT NOT NULL, -- 'VIDEO', 'IMAGE', 'AUDIO', 'SUBTITLE', 'THUMBNAIL'
    file_path TEXT NOT NULL,
    duration_seconds REAL,
    width INTEGER,
    height INTEGER,
    aspect_ratio TEXT, -- '9:16', '16:9'
    file_size_bytes INTEGER,
    sha256 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Secure Google Pro Accounts Registry (Zero Additional Cost Invariant)
CREATE TABLE IF NOT EXISTS google_accounts (
    id TEXT PRIMARY KEY,
    account_email_masked TEXT NOT NULL,
    auth_status TEXT NOT NULL DEFAULT 'UNCONFIGURED', -- 'AUTHENTICATED', 'UNCONFIGURED', 'EXPIRED', 'ERROR'
    encrypted_credentials TEXT, -- AES-256-GCM encrypted tokens
    available_quota TEXT DEFAULT 'UNKNOWN',
    quota_observed_at TIMESTAMP,
    current_usage TEXT,
    last_successful_gen TIMESTAMP,
    is_available INTEGER NOT NULL DEFAULT 1,
    error_state TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Weekly Library Hour Proposals
CREATE TABLE IF NOT EXISTS library_proposals (
    id TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    repository_url TEXT NOT NULL,
    license TEXT NOT NULL,
    last_maintenance TEXT,
    dependencies TEXT,
    arm64_compatible INTEGER NOT NULL DEFAULT 1,
    proot_compatible INTEGER NOT NULL DEFAULT 1,
    security_risks TEXT,
    required_permissions TEXT,
    benefits TEXT,
    installation_size_mb REAL,
    integration_plan TEXT,
    recommendation TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PROPOSED', -- 'PROPOSED', 'IN_NEEDS_YOU', 'APPROVED_BY_OWNER', 'REJECTED_BY_OWNER', 'INSTALLED'
    approval_id TEXT REFERENCES approvals(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Publication Packages (Phase F Waiting for Owner)
CREATE TABLE IF NOT EXISTS publication_packages (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    target_platform TEXT NOT NULL,
    video_asset_id TEXT REFERENCES media_assets(id),
    thumbnail_asset_id TEXT REFERENCES media_assets(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    hashtags TEXT DEFAULT '[]',
    proposed_publication_time TIMESTAMP,
    quality_report TEXT DEFAULT '{}',
    approval_id TEXT REFERENCES approvals(id),
    status TEXT NOT NULL DEFAULT 'WAITING_FOR_OWNER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed Initial 3 Google Pro Accounts (Masked, unconfigured placeholders with zero charges)
INSERT OR IGNORE INTO google_accounts (id, account_email_masked, auth_status, available_quota) VALUES
('gacc-01', 'pro.account.1***@gmail.com', 'UNCONFIGURED', 'UNKNOWN'),
('gacc-02', 'pro.account.2***@gmail.com', 'UNCONFIGURED', 'UNKNOWN'),
('gacc-03', 'pro.account.3***@gmail.com', 'UNCONFIGURED', 'UNKNOWN');
