-- Migration 003: Complete Connected Platform Accounts
-- Expands social_accounts table for Google (1, 2, 3), YouTube, TikTok, Instagram, and Facebook

ALTER TABLE social_accounts ADD COLUMN operational_status TEXT NOT NULL DEFAULT 'DISCONNECTED';
ALTER TABLE social_accounts ADD COLUMN capabilities TEXT DEFAULT '[]';
ALTER TABLE social_accounts ADD COLUMN scopes TEXT DEFAULT '[]';
ALTER TABLE social_accounts ADD COLUMN last_test_result TEXT DEFAULT '{}';
ALTER TABLE social_accounts ADD COLUMN app_intent_uri TEXT;

-- Seed all 7 required platforms
INSERT OR IGNORE INTO social_accounts (platform, operational_status, capabilities, scopes, app_intent_uri) VALUES
('google-1', 'DISCONNECTED', '["Account Identification", "Google Services Profile", "Zero-Cost Quota"]', '["openid", "email", "profile"]', 'https://accounts.google.com'),
('google-2', 'DISCONNECTED', '["Account Identification", "Google Services Profile", "Zero-Cost Quota"]', '["openid", "email", "profile"]', 'https://accounts.google.com'),
('google-3', 'DISCONNECTED', '["Account Identification", "Google Services Profile", "Zero-Cost Quota"]', '["openid", "email", "profile"]', 'https://accounts.google.com'),
('youtube', 'DISCONNECTED', '["Channel Identity", "Upload Preparation", "Publication Status", "Channel Analytics"]', '["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.upload"]', 'vnd.youtube://'),
('tiktok', 'DISCONNECTED', '["Account Authorization", "Video Preparation", "Content Posting API", "Publication Status"]', '["user.info.basic", "video.upload", "video.publish"]', 'snssdk1233://'),
('instagram', 'DISCONNECTED', '["Professional Account", "Media Preparation", "Publishing Where Approved", "Insights"]', '["instagram_basic", "instagram_content_publish", "instagram_manage_insights"]', 'instagram://'),
('facebook', 'DISCONNECTED', '["Page Authorization", "Media Preparation", "Publishing Where Approved", "Page Insights"]', '["pages_show_list", "pages_read_engagement", "pages_manage_posts"]', 'fb://');
