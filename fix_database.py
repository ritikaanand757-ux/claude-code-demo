"""
Script to fix database issues:
1. Create default admin user
2. Assign all NULL owner_id tasks to admin user
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/taskmanager_db")

print(f"Connecting to database: {DATABASE_URL}")

# Create engine
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Step 1: Check if admin user exists
    result = session.execute(text("SELECT id, username FROM users WHERE id = 1"))
    user = result.fetchone()

    if user:
        print(f"✓ Admin user already exists: {user}")
    else:
        # Create admin user
        # Password hash for "admin123"
        hash_pw = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfqHqr3jSu"
        session.execute(text("""
            INSERT INTO users (id, username, email, hashed_password, is_active, created_at)
            VALUES (1, 'admin', 'admin@taskmanager.com', :hash_pw, true, NOW())
        """), {"hash_pw": hash_pw})
        session.commit()
        print("✓ Created admin user (username: admin, email: admin@taskmanager.com, password: admin123)")

    # Step 2: Check tasks with NULL owner_id
    result = session.execute(text("SELECT COUNT(*) FROM tasks WHERE owner_id IS NULL"))
    null_count = result.scalar()
    print(f"\nTasks with NULL owner_id: {null_count}")

    if null_count > 0:
        # Update all NULL owner_id to 1
        result = session.execute(text("""
            UPDATE tasks
            SET owner_id = 1
            WHERE owner_id IS NULL
        """))
        session.commit()
        print(f"✓ Updated {null_count} tasks to be owned by admin user")
    else:
        print("✓ All tasks already have an owner")

    # Step 3: Verify the fix
    result = session.execute(text("SELECT COUNT(*), owner_id FROM tasks GROUP BY owner_id"))
    print("\nTask ownership summary:")
    for row in result:
        print(f"  - {row[0]} tasks owned by user {row[1]}")

    # Step 4: Make owner_id NOT NULL if needed
    result = session.execute(text("""
        SELECT column_name, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'owner_id'
    """))
    col_info = result.fetchone()

    if col_info and col_info[1] == 'YES':
        session.execute(text("ALTER TABLE tasks ALTER COLUMN owner_id SET NOT NULL"))
        session.commit()
        print("\n✓ Made owner_id NOT NULL")
    else:
        print("\n✓ owner_id is already NOT NULL")

    # Step 5: Add foreign key constraint if missing
    result = session.execute(text("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = 'tasks'
        AND constraint_name = 'fk_tasks_owner_id'
    """))
    fk_exists = result.fetchone()

    if not fk_exists:
        session.execute(text("""
            ALTER TABLE tasks
            ADD CONSTRAINT fk_tasks_owner_id
            FOREIGN KEY (owner_id) REFERENCES users (id)
        """))
        session.commit()
        print("✓ Added foreign key constraint")
    else:
        print("✓ Foreign key constraint already exists")

    print("\n✅ Database fixed successfully!")
    print("\nYou can now restart uvicorn:")
    print("  python -m uvicorn backend.main:app --reload")

except Exception as e:
    session.rollback()
    print(f"\n❌ Error: {e}")
    raise
finally:
    session.close()
