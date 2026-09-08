#!/bin/bash
# Azure App Service (Linux, Python) startup command for the frontend.
# Set this script as the app's Startup Command, with the app root
# configured to frontend/ so Oryx builds from frontend/requirements.txt
# and api_client.py's plain `from api_client import ...` resolves.
#
# BACKEND_API_URL must be set as an App Service Application Setting,
# pointing at the deployed backend Container App's URL — see
# api_client.py's get_backend_url().

python -m streamlit run app.py \
    --server.port 8000 \
    --server.address 0.0.0.0 \
    --server.headless true
