-- Legendium OS schema (PostgreSQL dialect; SQLAlchemy generates equivalents for SQLite)

CREATE TABLE departments (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  slug VARCHAR(20) UNIQUE NOT NULL,
  jira_project_key VARCHAR(10)
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(120) UNIQUE,
  password_hash VARCHAR(256) NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('admin','lead','employee')),
  department_id INT REFERENCES departments(id),
  manager_id INT REFERENCES users(id),
  title VARCHAR(100),
  skills TEXT DEFAULT '',
  capacity_hours FLOAT DEFAULT 40,
  avatar_color VARCHAR(7) DEFAULT '#06b6d4'
);

CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(50) UNIQUE,
  description TEXT DEFAULT '',
  department_id INT REFERENCES departments(id),
  status VARCHAR(20) DEFAULT 'active',
  health VARCHAR(10) DEFAULT 'green',
  target_date TIMESTAMP
);

CREATE TABLE sprints (
  id SERIAL PRIMARY KEY,
  name VARCHAR(80) NOT NULL,
  department_id INT REFERENCES departments(id),
  start_date TIMESTAMP,
  end_date TIMESTAMP,
  state VARCHAR(15) DEFAULT 'active'
);

CREATE TABLE work_items (
  id SERIAL PRIMARY KEY,
  type VARCHAR(10) NOT NULL CHECK (type IN ('epic','story','task','subtask')),
  title VARCHAR(200) NOT NULL,
  description TEXT DEFAULT '',
  status VARCHAR(20) DEFAULT 'todo'
    CHECK (status IN ('todo','in_progress','review','blocked','done')),
  priority VARCHAR(10) DEFAULT 'medium',
  discipline VARCHAR(20) DEFAULT 'development',
  estimate_hours FLOAT DEFAULT 0,
  logged_hours FLOAT DEFAULT 0,
  due_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  project_id INT NOT NULL REFERENCES projects(id),
  parent_id INT REFERENCES work_items(id),
  assignee_id INT REFERENCES users(id),
  reporter_id INT REFERENCES users(id),
  sprint_id INT REFERENCES sprints(id),
  jira_key VARCHAR(20)
);
CREATE INDEX idx_work_items_assignee ON work_items(assignee_id);
CREATE INDEX idx_work_items_jira ON work_items(jira_key);

CREATE TABLE dependencies (
  id SERIAL PRIMARY KEY,
  blocker_id INT NOT NULL REFERENCES work_items(id),
  blocked_id INT NOT NULL REFERENCES work_items(id)
);

CREATE TABLE comments (
  id SERIAL PRIMARY KEY,
  work_item_id INT NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
  author_id INT NOT NULL REFERENCES users(id),
  body TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now(),
  ai_flags VARCHAR(120) DEFAULT ''
);

CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(200) NOT NULL,
  kind VARCHAR(20) DEFAULT 'other',
  uploaded_by INT REFERENCES users(id),
  uploaded_at TIMESTAMP DEFAULT now(),
  text_content TEXT DEFAULT '',
  size_bytes INT DEFAULT 0
);

CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  message VARCHAR(300) NOT NULL,
  kind VARCHAR(20) DEFAULT 'info',
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  action VARCHAR(80) NOT NULL,
  detail TEXT DEFAULT '',
  created_at TIMESTAMP DEFAULT now()
);
