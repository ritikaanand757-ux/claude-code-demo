#!/bin/bash

echo "Starting Task Manager Frontend..."
echo ""
echo "The frontend will be available at http://localhost:3000"
echo ""

cd frontend
python -m http.server 3000
