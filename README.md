# Real-Time Tracking Dashboard with DhanHQ

Real-time stock holdings monitoring system using:
- Frontend: Angular 19
- Backend: FastAPI (Python)
- Data: DhanHQ API

## Features
- Real-time WebSocket updates
- Profit/Loss calculations
- Market hours detection
- Automatic reconnection

## Setup

### Backend (FastAPI)
```bash
cd backend/
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (Angular)
```bash
cd frontend/
npm install
ng serve
```

## Environment Variables
Create `.env` file:
```ini
DHAN_CLIENT_ID=your_client_id
ACCESS_TOKEN=your_access_token
```