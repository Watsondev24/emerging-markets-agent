import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import httpx
import asyncio
import json

WXO_API_KEY = os.getenv("WXO_API_KEY")
WXO_URL = os.getenv("WXO_URL")
WXO_AGENT_ID = "446cb76b-ed0c-49e7-90d2-11f134ab7c84"
WXO_ENVIRONMENT_ID = "553dc9d1-990a-46ad-a7aa-3a0c88c7efc9"

async def get_iam_token(api_key):
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post("https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key})
        if r.status_code != 200:
            raise Exception(f"IAM failed: {r.text}")
        return r.json()["access_token"]

async def test_rest_api():
    print("Getting IAM token...")
    token = await get_iam_token(WXO_API_KEY)
    print(f"✓ Token obtained")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    instance_id = WXO_URL.split('/instances/')[-1]
    base_url = WXO_URL.split('/instances/')[0]
    
    async with httpx.AsyncClient(timeout=120.0) as c:
        # Try listing agents to verify access
        list_url = f"{base_url}/instances/{instance_id}/v1/agents"
        print(f"\nListing agents: GET {list_url}")
        
        r = await c.get(list_url, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:1000]}")
        
        if r.status_code == 200:
            agents = r.json()
            print(f"\n✓ Agents found: {json.dumps(agents, indent=2)[:500]}")
        
        # Try getting specific agent
        agent_url = f"{base_url}/instances/{instance_id}/v1/agents/{WXO_AGENT_ID}"
        print(f"\nGetting agent: GET {agent_url}")
        
        r = await c.get(agent_url, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:1000]}")
        
        # Try message endpoint with different structure
        msg_url = f"{base_url}/instances/{instance_id}/v1/agents/{WXO_AGENT_ID}/message"
        print(f"\nSending message: POST {msg_url}")
        
        msg_payload = {
            "input": {
                "text": "Should we expand into Vietnam?"
            },
            "environment_id": WXO_ENVIRONMENT_ID
        }
        
        r = await c.post(msg_url, headers=headers, json=msg_payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:1000]}")

if __name__ == "__main__":
    asyncio.run(test_rest_api())

# Made with Bob
