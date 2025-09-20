from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("7948578566:AAGZzyXFx4vgmAZTsRELno1heKLK--B1OhY")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
