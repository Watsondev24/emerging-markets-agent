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
ORCHESTRATION_ID = "42379027d430475b88345e10c0b3a286_c1d67b02-6cda-4be5-894b-736fbd491e51"

async def get_iam_token(api_key):
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post("https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key})
        if r.status_code != 200:
            raise Exception(f"IAM failed: {r.text}")
        return r.json()["access_token"]

async def test_chat_api():
    print("Getting IAM token...")
    token = await get_iam_token(WXO_API_KEY)
    print(f"✓ Token obtained")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try the chat API endpoint
    base_url = "https://us-south.watson-orchestrate.cloud.ibm.com"
    
    async with httpx.AsyncClient(timeout=120.0) as c:
        # Create conversation
        conv_url = f"{base_url}/wxochat/api/chat/conversations"
        print(f"\nCreating conversation: POST {conv_url}")
        
        conv_payload = {
            "orchestrationId": ORCHESTRATION_ID,
            "agentId": WXO_AGENT_ID,
            "environmentId": WXO_ENVIRONMENT_ID
        }
        
        r = await c.post(conv_url, headers=headers, json=conv_payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500]}")
        
        if r.status_code in (200, 201):
            conv_data = r.json()
            conversation_id = conv_data.get("conversationId") or conv_data.get("id")
            print(f"✓ Conversation created: {conversation_id}")
            
            # Send message
            msg_url = f"{base_url}/wxochat/api/chat/conversations/{conversation_id}/messages"
            print(f"\nSending message: POST {msg_url}")
            
            msg_payload = {
                "message": "Should we expand into Vietnam?",
                "orchestrationId": ORCHESTRATION_ID
            }
            
            msg_resp = await c.post(msg_url, headers=headers, json=msg_payload)
            print(f"Status: {msg_resp.status_code}")
            print(f"Response: {msg_resp.text[:1000]}")
            
            if msg_resp.status_code in (200, 201):
                data = msg_resp.json()
                print("\n✓ Response received:")
                print(json.dumps(data, indent=2)[:1000])
        else:
            print(f"❌ Failed to create conversation")

if __name__ == "__main__":
    asyncio.run(test_chat_api())

# Made with Bob
