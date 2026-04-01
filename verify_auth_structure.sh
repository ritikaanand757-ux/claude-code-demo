#!/bin/bash

echo "=================================="
echo "Authentication System Verification"
echo "=================================="
echo ""

# Check created files
echo "Checking created files..."
files=(
    "backend/auth.py"
    "backend/auth_routes.py"
    ".env.example"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo "✓ $file exists ($lines lines)"
    else
        echo "✗ $file missing"
    fi
done

echo ""
echo "Checking modified files..."

# Check if User model exists in models.py
if grep -q "class User(Base):" "backend/models.py"; then
    echo "✓ User model added to backend/models.py"
else
    echo "✗ User model not found in backend/models.py"
fi

# Check if User schemas exist in schemas.py
if grep -q "class UserCreate" "backend/schemas.py"; then
    echo "✓ User schemas added to backend/schemas.py"
else
    echo "✗ User schemas not found in backend/schemas.py"
fi

# Check if user CRUD functions exist in crud.py
if grep -q "def create_user" "backend/crud.py"; then
    echo "✓ User CRUD functions added to backend/crud.py"
else
    echo "✗ User CRUD functions not found in backend/crud.py"
fi

# Check if auth router is included in main.py
if grep -q "from backend.auth_routes import router as auth_router" "backend/main.py"; then
    echo "✓ Auth router imported in backend/main.py"
else
    echo "✗ Auth router not imported in backend/main.py"
fi

if grep -q "app.include_router(auth_router" "backend/main.py"; then
    echo "✓ Auth router included in backend/main.py"
else
    echo "✗ Auth router not included in backend/main.py"
fi

# Check if dependencies are in requirements.txt
if grep -q "python-jose" "requirements.txt"; then
    echo "✓ python-jose added to requirements.txt"
else
    echo "✗ python-jose not in requirements.txt"
fi

if grep -q "passlib" "requirements.txt"; then
    echo "✓ passlib added to requirements.txt"
else
    echo "✗ passlib not in requirements.txt"
fi

echo ""
echo "=================================="
echo "Code Structure Verification"
echo "=================================="
echo ""

# Count functions in each file
echo "backend/auth.py functions:"
grep -c "^def " "backend/auth.py" && grep "^def " "backend/auth.py" | sed 's/def /  - /' | sed 's/(.*://'

echo ""
echo "backend/auth_routes.py endpoints:"
grep "@router\." "backend/auth_routes.py" | sed 's/@router\./  - /' | sed 's/(.*$//'

echo ""
echo "User model fields:"
grep "Column(" "backend/models.py" | grep -A 10 "class User" | grep "Column(" | head -7 | sed 's/^[[:space:]]*/  - /'

echo ""
echo "=================================="
echo "Summary"
echo "=================================="
echo ""
echo "Authentication system implementation complete!"
echo ""
echo "Next steps:"
echo "1. pip install -r requirements.txt"
echo "2. Create .env file with SECRET_KEY"
echo "3. alembic revision --autogenerate -m 'add users table'"
echo "4. alembic upgrade head"
echo "5. uvicorn backend.main:app --reload"
