1. Create the Documentation File
Open a new terminal window (or stop the producer) and navigate to the root of your project:

Bash
touch docs/README-Phase1B-PythonProducer.md
2. The Phase 1B Runbook
Open docs/README-Phase1B-PythonProducer.md in your text editor and copy-paste the exact markdown below:

Markdown
# Phase 1B: Python Producer & Chaos Engineering

**Tool Focus:** Python 3.11, Azure Event Hubs SDK, Synthetic Data Generation.
**Objective:** Build an event-driven data producer that simulates a high-throughput market data feed (ticks/executions) and injects intentional data anomalies to test downstream pipeline resilience.

---

## 1. The Chaos Engineering Strategy

Real-world streaming data is never perfectly clean. To prove the robustness of our downstream PySpark engine, this producer intentionally injects "chaos" into the Event Hub stream:

1. **Late-Arriving Data (5%):** Timestamps are artificially delayed by 5 to 60 minutes to test Spark's watermark and state management capabilities.
2. **Schema Drift / Malformed Payloads (2%):** Required fields (like `volume`) are dropped, and correct data types (like `price` floats) are replaced with string errors (`"ERROR_NULL"`). This validates our downstream Dead Letter Queue (DLQ) logic.
3. **Duplicate Events (3%):** The exact same JSON payload is sent twice to test downstream deduplication mechanics.

---

## 2. Environment Setup

To isolate dependencies, we utilized a Python Virtual Environment.

### Step 1: Initialize the Virtual Environment
```bash
cd ingestion
python -m venv .venv
source .venv/Scripts/activate  # (Windows)
# or `source .venv/bin/activate` (macOS/Linux)
Step 2: Install Required Libraries
Bash
pip install azure-eventhub python-dotenv faker
pip freeze > requirements.txt
3. Configuration & Execution
Step 1: Securely Store the Connection String
The producer requires the Azure Event Hub connection string generated during Phase 1A by Terraform. This string is stored in a hidden .env.secret file (ignored by Git) inside the ingestion/ directory.

Crucial Formatting Note:
The python-dotenv library requires a strict KEY=VALUE pair.
Correct format inside .env.secret:
eventhub_primary_connection_string=Endpoint=sb://eh-marketstream-dev...

Step 2: Execute the Stream
Bash
python market_producer.py
(The producer batches trades into groups of 10-50 and streams them continuously until manually stopped via Ctrl + C).

4. Interview Preparation: Defending the Producer
When discussing this pipeline in an interview, focus on the deliberate injection of dirty data:

Q: Why didn't you just use a clean CSV file or a standard API for your data source?

"In a production environment, upstream systems fail, network partitions cause late data, and schemas change without notice. By engineering a custom Python producer with controlled chaos injection, I was able to guarantee that my downstream PySpark engine could handle out-of-order records, drop duplicates, and quarantine schema drift without crashing the VWAP calculation."


***

### 3. Save, Commit, and Push

Now that we have written the producer code and documented it, let's back it up to GitHub. 

*(Don't worry, your `.gitignore` will ensure your `.venv` folder and `.env.secret` file are kept safely off the internet!)*

Run these commands from the root of your project:

```bash
git add ingestion/ docs/
git commit -m "feat: add python market producer with chaos injection and runbook"
git push



-------Troubleshooting steps


1. Setting up the Python Environment
First, we need to ensure your local Python environment is isolated and has the Microsoft Event Hubs SDK installed.

Ensure you are in the root directory of your project, then navigate to the ingestion folder:

Bash
cd ingestion
1
Create a Virtual Environment
python -m venv .venv
This isolates our project dependencies from your system Python.

Bash
python -m venv .venv
2
Activate the Environment (Windows)
source .venv/Scripts/activate
Note: If you were on a Mac/Linux, you would run source .venv/bin/activate instead.

Bash
source .venv/Scripts/activate
(You should now see (.venv) at the beginning of your terminal prompt).

3
Install Required Libraries
pip install
We need the Azure SDK and a library to read our .env.secret file.

Bash
pip install azure-eventhub python-dotenv faker
4
Save the Dependencies
Freeze requirements
This ensures anyone cloning your repo knows exactly what libraries are needed.

Bash
pip freeze > requirements.txt
2. Building the Producer Script
Now we write the Python script that generates the data and pushes it to Azure.

Inside the ingestion folder, create a new file named market_producer.py:

Bash
touch market_producer.py
Open market_producer.py in your code editor and paste this code:

Python
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
The Python script is ready. Let's test it!

$ python -m venv .venv

Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Apps > Advanced app settings > App execution aliases.

This is a classic Windows quirk! Windows has a built-in "shortcut" that intercepts the python command and tries to force you to download it from the Microsoft Store if it isn't explicitly found in your system's PATH.

Since you already have the Windows Package Manager (winget) working from our Terraform setup, we can use it to install Python professionally and bypass the Microsoft Store entirely.

Here is how to get Python installed and your virtual environment running.

1
Install Python
winget
Run this command in your current Git Bash terminal to install Python (Version 3.11 is highly stable for Data Engineering libraries):

Bash
winget install Python.Python.3.11
(If prompted to agree to terms, type Y and press Enter).

2
Restart Git Bash
Critical Step
Just like before, Windows needs to update your system's PATH variables so Git Bash knows exactly where Python was installed.
Close your Git Bash window completely.

Open a fresh Git Bash window and navigate back to your ingestion folder:

Bash
cd /d/Streaming_project_DE/azure-databricks-fintech-market-stream-project/ingestion
3
Verify the Installation
python --version
Verify that Windows is no longer intercepting the command:

Bash
python --version
(If it prints Python 3.11.x, you are good to go! If it still opens the Windows store, run py --version instead).

4
Create and Activate the Virtual Environment
python -m venv
Now you can safely create your isolated environment and activate it:

Bash
python -m venv .venv
source .venv/Scripts/activate
(You should see (.venv) appear at the beginning of your terminal prompt).

Once you see that (.venv) prefix, you can resume the setup by installing the Azure libraries we need:

Bash
pip install azure-eventhub python-dotenv faker
pip freeze > requirements.txt
Python is installed and the script is ready!

Yes
I successfully installed Python, activated the virtual environment, installed the libraries, and saved the market_producer.py script. I am ready to run it!

This is where the architecture comes to life! You have built the highway (Terraform/Azure), and now we are going to drive the cars (Python/Chaos Data) on it.

Ensure your terminal still shows the (.venv) prefix and you are inside the ingestion folder.

1. Execute the Producer
Run this command in your terminal:

Bash
python market_producer.py
2. What to Expect
If everything is wired up correctly, your terminal will immediately start printing out something like this:

Plaintext
Initializing Event Hub Producer...
Connected! Streaming market data. Press Ctrl+C to stop.
Sent batch of 34 trades to Event Hubs.
Sent batch of 12 trades to Event Hubs.
Sent batch of 47 trades to Event Hubs.
...
Let it run for about 30 to 60 seconds.
We want to pump a few thousand records into the Event Hub so that our Spark Streaming engine has a good backlog of data (and chaos!) to process when we build it in the next phase.

3. Stop the Stream
Once you have let it run for a bit, click inside your terminal window and press Ctrl + C on your keyboard to gracefully shut down the producer.

Why this matters for your interview
When you describe this project, you can now confidently state:

"I didn't just build a pipeline for perfect data. I engineered a custom Python producer that dynamically injects late-arriving records, schema drift, and duplicates. This allowed me to prove that my downstream Databricks engine can successfully quarantine bad data and calculate an accurate VWAP regardless of upstream system failures."

That sentence alone separates Senior/Staff candidates from junior developers.

The data is sent! Let's document and move on.

Yes
$ python market_producer.py

ERROR: Connection string not found. Did you run terraform output?

This is actually my fault! As your Tech Lead, I gave you a command earlier that missed a crucial detail about how Python reads environment variables.

When we ran terraform output -raw > .env.secret, Terraform dumped the raw connection string directly into the file (e.g., Endpoint=sb://...). However, the Python python-dotenv library explicitly requires a KEY=VALUE format to read it properly. Right now, your file only has the VALUE.

Let's fix that file manually so Python can read it.

1
Open the secret file
Open your code editor (like VS Code or Notepad), navigate to the ingestion/ folder, and open the hidden .env.secret file.
(If you can't see it, make sure your editor is set to show hidden files).

2
Format as KEY=VALUE
You will see a long string starting with Endpoint=sb://....
Add the variable name eventhub_primary_connection_string= to the very beginning of that line, so it looks exactly like this:

Plaintext
eventhub_primary_connection_string=Endpoint=sb://eh-marketstream-dev...
(Do not add spaces around the equals sign, and make sure it is all on one single line).

3
Save and Re-run
Save the file, go back to your terminal (making sure you are in the ingestion folder with the (.venv) activated), and run the script again:

Bash
python market_producer.py
Let it run for about 30 to 60 seconds to pump a few thousand records into your Event Hub, then press Ctrl + C to stop it. Let me know when you've successfully pushed the data!

