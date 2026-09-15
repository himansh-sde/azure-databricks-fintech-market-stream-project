import os
import json
import time
import random
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from azure.eventhub import EventHubProducerClient, EventData

# 1. Load the connection string from our hidden file
load_dotenv(".env.secret")
CONNECTION_STR = os.environ.get("eventhub_primary_connection_string")
EVENTHUB_NAME = "market-trades" # As defined in Terraform

# Tickers to simulate
SYMBOLS = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"]

def generate_trade_event():
    """Generates a single synthetic market trade execution."""
    symbol = random.choice(SYMBOLS)
    base_price = {"AAPL": 150, "MSFT": 350, "TSLA": 200, "NVDA": 500, "AMZN": 130}[symbol]
    
    # Simulate a realistic price fluctuation (+/- 2%)
    price = round(base_price * (1 + random.uniform(-0.02, 0.02)), 2)
    
    # 2. Chaos Injection: 5% chance the timestamp is artificially delayed (late-arriving data)
    timestamp = datetime.utcnow()
    if random.random() < 0.05:
        timestamp = timestamp - timedelta(minutes=random.randint(5, 60))
        
    trade = {
        "trade_id": str(uuid.uuid4()),
        "symbol": symbol,
        "price": price,
        "volume": random.randint(1, 100) * 100, # Lots of 100
        "timestamp": timestamp.isoformat() + "Z",
        "trade_type": random.choice(["buy", "sell"])
    }
    
    # 3. Chaos Injection: 2% chance to send a malformed schema
    if random.random() < 0.02:
        trade["price"] = "ERROR_NULL" # Should be a float
        del trade["volume"] # Missing required field
        
    return trade

def run_producer():
    """Connects to Event Hubs and streams data infinitely."""
    print("Initializing Event Hub Producer...")
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR, 
        eventhub_name=EVENTHUB_NAME
    )
    
    try:
        with producer:
            print("Connected! Streaming market data. Press Ctrl+C to stop.")
            while True:
                # We send data in batches for efficiency
                event_data_batch = producer.create_batch()
                
                # Generate 10-50 trades per batch
                batch_size = random.randint(10, 50)
                for _ in range(batch_size):
                    trade = generate_trade_event()
                    
                    # 4. Chaos Injection: 3% chance to duplicate an event
                    event_data_batch.add(EventData(json.dumps(trade)))
                    if random.random() < 0.03:
                        event_data_batch.add(EventData(json.dumps(trade)))
                        
                # Send the batch to Azure
                producer.send_batch(event_data_batch)
                print(f"Sent batch of {batch_size} trades to Event Hubs.")
                
                # Sleep briefly to control throughput
                time.sleep(random.uniform(0.5, 2.0))
                
    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if not CONNECTION_STR:
        print("ERROR: Connection string not found. Did you run terraform output?")
    else:
        run_producer()
