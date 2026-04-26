#!/bin/bash
echo "Installing Docker..."
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

echo "Setting up Python virtual environment..."
mkdir -p backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-dotenv
pip install langchain langgraph langchain-google-genai
pip install qdrant-client sentence-transformers
pip install asyncpg "sqlalchemy[asyncio]" alembic
pip install yfinance httpx tenacity

echo "Starting Docker containers..."
docker pull qdrant/qdrant
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
docker run -d --name pg-dev -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=finance_db -p 5432:5432 postgres:15

echo "========================================="
echo "Setup complete!"
echo "Please restart your terminal or run 'newgrp docker' to apply docker group changes."
echo "========================================="
