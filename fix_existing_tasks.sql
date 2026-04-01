-- Fix existing tasks with NULL owner_id
-- This script creates a default admin user and assigns all orphaned tasks to them

-- Step 1: Create a default admin user if it doesn't exist
-- Password hash for "admin123" (you should change this later!)
INSERT INTO users (id, username, email, hashed_password, is_active, created_at)
VALUES (
    1,
    'admin',
    'admin@taskmanager.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfqHqr3jSu',
    true,
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Step 2: Update all tasks with NULL owner_id to be owned by user 1
UPDATE tasks
SET owner_id = 1
WHERE owner_id IS NULL;

-- Step 3: Make owner_id NOT NULL now that all tasks have an owner
ALTER TABLE tasks ALTER COLUMN owner_id SET NOT NULL;

-- Step 4: Add foreign key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_tasks_owner_id'
    ) THEN
        ALTER TABLE tasks
        ADD CONSTRAINT fk_tasks_owner_id
        FOREIGN KEY (owner_id) REFERENCES users (id);
    END IF;
END $$;

-- Display results
SELECT 'Fixed ' || COUNT(*) || ' tasks' AS result FROM tasks WHERE owner_id = 1;
