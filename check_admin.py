"""
Check and create/fix admin user
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from backend.auth import get_password_hash

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/taskmanager_db")

print(f"Connecting to: {DATABASE_URL}\n")

# Create engine
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Check all users
    result = session.execute(text("SELECT id, username, email, is_active, is_admin FROM users"))
    users = result.fetchall()

    print("=" * 60)
    print("EXISTING USERS:")
    print("=" * 60)
    if users:
        for user in users:
            print(f"ID: {user[0]}")
            print(f"  Username: {user[1]}")
            print(f"  Email: {user[2]}")
            print(f"  Active: {user[3]}")
            print(f"  Admin: {user[4]}")
            print("-" * 60)
    else:
        print("No users found!")
    print()

    # Check if admin user exists (.local or .com)
    result = session.execute(text("""
        SELECT id, username, email FROM users
        WHERE email IN ('admin@taskmanager.local', 'admin@taskmanager.com')
        OR username = 'admin'
    """))
    admin_user = result.fetchone()

    if admin_user:
        print("✅ Admin user exists!")
        print(f"   Email: {admin_user[2]}")
        print(f"   Username: {admin_user[1]}")

        # If email is .local, update to .com
        if admin_user[2] == 'admin@taskmanager.local':
            print("\n⚠️  Updating email from .local to .com for compatibility...")
            session.execute(text("""
                UPDATE users
                SET email = 'admin@taskmanager.com'
                WHERE id = :user_id
            """), {"user_id": admin_user[0]})
            session.commit()
            print("✅ Email updated to: admin@taskmanager.com")

        print("   Password: admin123")
    else:
        print("❌ Admin user NOT found! Creating...")

        # Create admin user
        # Password: admin123
        hashed_password = get_password_hash("admin123")

        session.execute(text("""
            INSERT INTO users (username, email, hashed_password, is_active, is_admin, created_at)
            VALUES ('admin', 'admin@taskmanager.com', :password, true, true, NOW())
        """), {"password": hashed_password})

        session.commit()

        print("✅ Admin user created successfully!")
        print("   Email: admin@taskmanager.com")
        print("   Password: admin123")

    print()
    print("=" * 60)
    print("LOGIN CREDENTIALS:")
    print("=" * 60)
    print("Email: admin@taskmanager.com")
    print("Password: admin123")
    print("=" * 60)

except Exception as e:
    session.rollback()
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
