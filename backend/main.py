import asyncio
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from dhanhq import dhanhq
import pytz
from datetime import datetime
import json

IST = pytz.timezone('Asia/Kolkata')
last_data = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Your existing functions with modifications
def load_env_variables():
    load_dotenv()
    return os.getenv("DHAN_CLIENT_ID"), os.getenv("ACCESS_TOKEN")

def get_dhan_instance(client_id, access_token):
    try:
        return dhanhq(client_id, access_token)
    except Exception as e:
        print(f"Failed to create Dhan instance: {e}")
        return None

def process_holdings(dhan):
    try:
        data = dhan.get_holdings()
    except Exception as e:
        print(f"Error fetching holdings: {e}")
        return None

    results = []
    for item in data.get('data', []):
        if item["tradingSymbol"] == "NIFTYBEES":
            continue

        tradingSymbol = item["tradingSymbol"]
        availableQty = item["availableQty"]
        avgCostPrice = item["avgCostPrice"]
        lastTradedPrice = item["lastTradedPrice"]

        pl_percent = ((lastTradedPrice - avgCostPrice) / avgCostPrice) * 100
        pl = (lastTradedPrice - avgCostPrice) * availableQty

        results.append({
            "tradingSymbol": tradingSymbol,
            "availableQty": availableQty,
            "avgCostPrice": round(avgCostPrice, 2),
            "lastTradedPrice": round(lastTradedPrice, 2),
            "PL(%)": round(pl_percent, 2),
            "PL": round(pl, 2)
        })
    
    return results

def is_market_time():
    now_ist = datetime.now(IST).time()
    start_time = datetime.strptime("09:15", "%H:%M").time()
    end_time = datetime.strptime("15:30", "%H:%M").time()
    return start_time <= now_ist <= end_time

# Polling task
async def poll_dhan_data(dhan):
    global last_data
    while True:
        if not is_market_time():
            await asyncio.sleep(60)  # Check less frequently when market is closed
            continue
            
        try:
            current_data = process_holdings(dhan)
            if current_data and current_data != last_data:
                last_data = current_data
                await manager.broadcast(json.dumps(current_data))
        except Exception as e:
            print(f"Polling error: {e}")
        
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Dhan connection
    client_id, access_token = load_env_variables()
    dhan = get_dhan_instance(client_id, access_token)
    
    if dhan:
        asyncio.create_task(poll_dhan_data(dhan))
    else:
        print("Failed to initialize Dhan connection")
    
    yield

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)