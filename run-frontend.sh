#!/bin/bash

echo "🚀 Starting DocIntell Frontend Demo..."
echo "======================================"

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🌟 Starting development server..."
echo "The application will be available at: http://localhost:3000"
echo ""
echo "Demo Features:"
echo "- Login with any username/password (demo mode)"
echo "- View mock dashboard with sample data"
echo "- Navigate through different pages"
echo "- UI components and responsive design"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"

# Start the development server
npm start