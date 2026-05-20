#!/bin/bash
# scripts/start.sh — Start backend + frontend together

echo "🚀 Starting RAG Executive Analyst..."
echo ""

# Check .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "   Edit .env with your API keys before continuing."
    echo "   GROQ_API_KEY  → https://console.groq.com"
    echo "   TAVILY_API_KEY → https://tavily.com"
    exit 1
fi

# Create data dirs if missing
mkdir -p data/uploads data/reports data/chroma_db logs

# Kill any existing processes on those ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

echo "Starting FastAPI backend on port 8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

echo "Starting Streamlit frontend on port 8501..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "✅ RAG Executive Analyst is running!"
echo "   Frontend : http://localhost:8501"
echo "   API Docs : http://localhost:8000/docs"
echo "   Health   : http://localhost:8000/api/v1/health"
echo ""
echo "Press Ctrl+C to stop both services."

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
