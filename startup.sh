#!/bin/bash
echo "=== PAAI Platform Startup ==="
echo ""

# Install dependencies
echo "[1/4] Installing dependencies..."
pip install -r requirements.txt -q

# Check if .env exists
if [ ! -f .env ]; then
  echo "[2/4] Creating .env from template..."
  cp .env.example .env
  echo "      ⚠️  Please edit .env with your DATABASE_URL and SECRET_KEY"
else
  echo "[2/4] .env found ✓"
fi

# Run migrations
echo "[3/4] Running database migrations..."
flask db upgrade 2>/dev/null || (flask db init && flask db migrate -m "Initial" && flask db upgrade)

# Seed database
echo "[4/4] Seeding sample data..."
python seed.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Login credentials:"
echo "   Admin:  admin@paai.org.in  /  Admin@PAAI2024!"
echo "   User:   meera@example.com  /  User@1234!"
echo ""
echo "🚀 Starting server on http://localhost:5000"
python main.py
