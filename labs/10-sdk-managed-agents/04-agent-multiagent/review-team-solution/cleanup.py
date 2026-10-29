import json
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = Anthropic()
stores_file = Path(__file__).parent / "stores.json"
stores = json.loads(stores_file.read_text())

for label, store_id in stores.items():
    client.beta.memory_stores.delete(store_id)
    print(f"deleted      {label} {store_id}")
stores_file.unlink()
print(f"removed      {stores_file.name}")
