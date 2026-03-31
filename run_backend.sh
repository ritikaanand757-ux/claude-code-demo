#!/bin/bash

echo "Starting Task Manager Backend..."
echo ""
echo "Make sure PostgreSQL is running and the database 'taskmanager_db' exists."
echo ""

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
