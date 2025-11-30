import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("✅ Connected to Supabase!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
import os
import socket
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse, urlunparse

# Load .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Parse the URL
parsed = urlparse(DATABASE_URL)

try:
    # Resolve the hostname to IPv4
    ipv4 = socket.gethostbyname(parsed.hostname)
    
    # Rebuild the DATABASE_URL with the IPv4 address
    new_netloc = f"{parsed.username}:{parsed.password}@{ipv4}:{parsed.port}"
    new_url = urlunparse((parsed.scheme, new_netloc, parsed.path, "", "", ""))
    
    # Connect using psycopg2
    conn = psycopg2.connect(new_url + "?sslmode=require")
    print("✅ Connected successfully via IPv4!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
