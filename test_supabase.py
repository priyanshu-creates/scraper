
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"URL: {url}")
# Mask key for security
print(f"Key: {key[:10]}...{key[-5:] if key else ''}")

try:
    print("Connecting to Supabase...")
    supabase: Client = create_client(url, key)
    
    print("Listing table 'articles'...")
    response = supabase.table("articles").select("*").limit(1).execute()
    print("Success!")
    print(response)
except Exception as e:
    print(f"Error: {e}")
