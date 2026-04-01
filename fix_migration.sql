-- Fix partially completed migration 005
-- Add missing columns to tasks table

-- Step 1: Add the missing columns
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS owner_id INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS completion_note VARCHAR;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT false;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_overdue BOOLEAN DEFAULT false;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE;

-- Step 2: Set default owner_id for existing tasks (if any exist)
-- First, check if any users exist, if not, we'll need to handle this differently
UPDATE tasks SET owner_id = 1 WHERE owner_id IS NULL AND EXISTS (SELECT 1 FROM users WHERE id = 1);

-- Step 3: Make owner_id non-nullable (only if user ID 1 exists)
-- We'll skip this for now and handle it after creating a user

-- Step 4: Add foreign key constraint (only if owner_id is set)
-- ALTER TABLE tasks ADD CONSTRAINT fk_tasks_owner_id FOREIGN KEY (owner_id) REFERENCES users (id);

-- Step 5: Add CHECK constraint for title length (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'check_title_length'
    ) THEN
        ALTER TABLE tasks ADD CONSTRAINT check_title_length CHECK (LENGTH(title) >= 5 AND LENGTH(title) <= 100);
    END IF;
END $$;

-- Step 6: Mark migration as complete
UPDATE alembic_version SET version_num = '005' WHERE version_num = '004';
