#!/usr/bin/env bash

# 1. Start the official Strands Decider 2B server in the background on port 8000
echo "Starting Strands Decider 2B local server..."
strands-decider serve StrandsAgents/strands-decider-2B-hobson-v19 --port 8000 &

# 2. Wait for the model weights to load and download onto HF disk
echo "Waiting for model weights to load..."
sleep 15

# 3. Start your FastAPI gateway on HF's required port 7860
echo "Starting Sentry-Gate FastAPI Gateway on port 7860..."
uvicorn sentry_gate:app --host 0.0.0.0 --port 7860