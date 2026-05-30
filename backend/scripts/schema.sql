-- AI 闯关学习 · 用户系统初始表结构
-- MySQL 8.0+  utf8mb4
-- 用法：mysql -u root -p < scripts/schema.sql
-- 或在已选库 w_ai_learn 下执行表结构部分

CREATE DATABASE IF NOT EXISTS `w_ai_learn`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `w_ai_learn`;

-- ---------------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` CHAR(36) NOT NULL,
  `openid` VARCHAR(64) NOT NULL,
  `nickname` VARCHAR(64) NOT NULL,
  `avatar_url` VARCHAR(512) NULL,
  `created_at` DATETIME(3) NOT NULL,
  `updated_at` DATETIME(3) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users_openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- question_sets
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `question_sets` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `title` VARCHAR(128) NOT NULL,
  `source_text` TEXT NOT NULL,
  `knowledge_points` JSON NOT NULL,
  `questions` JSON NOT NULL,
  `question_count` INT NOT NULL,
  `created_at` DATETIME(3) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_question_sets_user_created` (`user_id`, `created_at`),
  CONSTRAINT `fk_question_sets_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- study_records
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `study_records` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `question_set_id` CHAR(36) NOT NULL,
  `session_id` VARCHAR(64) NOT NULL,
  `accuracy` DECIMAL(5,1) NOT NULL,
  `correct_count` INT NOT NULL,
  `total_questions` INT NOT NULL,
  `duration_seconds` INT NOT NULL,
  `wrong_questions` JSON NOT NULL,
  `weak_points` JSON NOT NULL,
  `summary` TEXT NOT NULL,
  `finished_at` DATETIME(3) NOT NULL,
  `created_at` DATETIME(3) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_study_records_session_id` (`session_id`),
  KEY `idx_study_records_user_finished` (`user_id`, `finished_at`),
  KEY `idx_study_records_question_set` (`question_set_id`, `finished_at`),
  CONSTRAINT `fk_study_records_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_study_records_question_set_id` FOREIGN KEY (`question_set_id`) REFERENCES `question_sets` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- study_sessions_meta（继续上次）
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `study_sessions_meta` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `question_set_id` CHAR(36) NULL,
  `status` VARCHAR(32) NOT NULL,
  `answered_count` INT NOT NULL,
  `total_questions` INT NOT NULL,
  `title` VARCHAR(128) NOT NULL,
  `updated_at` DATETIME(3) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_sessions_meta_user_status` (`user_id`, `status`, `updated_at`),
  CONSTRAINT `fk_sessions_meta_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_sessions_meta_question_set_id` FOREIGN KEY (`question_set_id`) REFERENCES `question_sets` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alembic 版本表由迁移工具自动维护；若纯 SQL 初始化可手动插入：
-- CREATE TABLE IF NOT EXISTS `alembic_version` (
--   `version_num` VARCHAR(32) NOT NULL,
--   PRIMARY KEY (`version_num`)
-- );
-- INSERT INTO `alembic_version` (`version_num`) VALUES ('001');
