import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import httpx
import asyncio

WXO_API_KEY = os.getenv("WXO_API_KEY")
WXO_URL = os.getenv("WXO_URL")
WXO_AGENT_ID = "446cb76b-ed0c-49e7-90d2-11f134ab7c84"
WXO_ENVIRONMENT_ID = "553dc9d1-990a-46ad-a7aa-3a0c88c7efc9"
WXO_HOST = WXO_URL.split('/instances/')[0] if WXO_URL else ""

async def get_iam_token(api_key):
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post("https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key})
        if r.status_code != 200:
            raise Exception(f"IAM failed: {r.text}")
        return r.json()["access_token"]

async def test_watson_assistant():
    print("Getting IAM token...")
    token = await get_iam_token(WXO_API_KEY)
    print(f"✓ Token obtained")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    instance_id = WXO_URL.split('/instances/')[-1]
    
    async with httpx.AsyncClient(timeout=120.0) as c:
        # Try creating a session
        url = f"{WXO_HOST}/instances/{instance_id}/v2/assistants/{WXO_AGENT_ID}/sessions"
        print(f"\nCreating session: POST {url}")
        
        r = await c.post(url, headers=headers, json={})
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500]}")
        
        if r.status_code in (200, 201):
            session_data = r.json()
            session_id = session_data.get("session_id")
            print(f"✓ Session created: {session_id}")
            
            # Send a message
            payload = {
                "input": {
                    "message_type": "text",
                    "text": "Should we expand into Vietnam?"
                }
            }
            
            msg_url = f"{WXO_HOST}/instances/{instance_id}/v2/assistants/{WXO_AGENT_ID}/sessions/{session_id}/message"
            print(f"\nSending message: POST {msg_url}")
            
            msg_resp = await c.post(msg_url, headers=headers, json=payload)
            print(f"Status: {msg_resp.status_code}")
            print(f"Response: {msg_resp.text[:1000]}")
            
            if msg_resp.status_code in (200, 201):
                data = msg_resp.json()
                output = data.get("output", {})
                generic = output.get("generic", [])
                
                print("\n✓ Response received:")
                for item in generic:
                    if item.get("response_type") == "text":
                        print(f"  {item.get('text', '')}")
        else:
            print(f"❌ Failed to create session")

if __name__ == "__main__":
    asyncio.run(test_watson_assistant())

# Made with Bob
