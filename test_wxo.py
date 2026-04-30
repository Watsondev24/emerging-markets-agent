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
# Extract host from WXO_URL
WXO_HOST = WXO_URL.split('/instances/')[0] if WXO_URL else "https://dev-wa.watson-orchestrate.ibm.com"

async def get_iam_token(api_key):
    print(f"Getting IAM token...")
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post("https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key})
        print(f"IAM Status: {r.status_code}")
        if r.status_code != 200:
            print(f"IAM Error: {r.text}")
            raise Exception(f"IAM failed: {r.text}")
        return r.json()["access_token"]

async def test_wxo():
    print(f"\n=== Testing wxO Agent ===")
    print(f"WXO_API_KEY: {WXO_API_KEY[:10]}..." if WXO_API_KEY else "WXO_API_KEY: NOT SET")
    print(f"WXO_URL: {WXO_URL}")
    print(f"WXO_AGENT_ID: {WXO_AGENT_ID}")
    print(f"WXO_ENVIRONMENT_ID: {WXO_ENVIRONMENT_ID}")
    print(f"WXO_HOST: {WXO_HOST}")
    
    if not WXO_API_KEY:
        print("\n❌ WXO_API_KEY not set!")
        return
    
    if not WXO_URL:
        print("\n❌ WXO_URL not set!")
        return
    
    try:
        token = await get_iam_token(WXO_API_KEY)
        print(f"✓ IAM token obtained: {token[:20]}...")
    except Exception as e:
        print(f"\n❌ IAM token error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    instance_id = WXO_URL.split('/instances/')[-1]
    print(f"\nInstance ID: {instance_id}")
    
    query = "Should we expand into Vietnam?"
    payload = {
        "message": {"role": "user", "content": query},
        "agent_id": WXO_AGENT_ID,
        "environment_id": WXO_ENVIRONMENT_ID
    }
    
    print(f"\nPayload: {payload}")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as c:
            url = f"{WXO_HOST}/instances/{instance_id}/v1/orchestrate/runs"
            print(f"\nPOST {url}")
            r = await c.post(url, headers=headers, json=payload)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:500]}")
            
            if r.status_code not in (200, 201):
                print(f"\n❌ Error: {r.status_code} - {r.text}")
                return
            
            data = r.json()
            run_id = data.get("run_id") or data.get("id")
            thread_id = data.get("thread_id")
            print(f"\n✓ Run created: run_id={run_id}, thread_id={thread_id}")
            
            if not run_id:
                print(f"❌ No run_id in response: {data}")
                return
            
            # Poll for completion
            print(f"\nPolling for completion...")
            status_data = {}
            for i in range(30):
                await asyncio.sleep(2)
                sr = await c.get(f"{WXO_HOST}/instances/{instance_id}/v1/orchestrate/runs/{run_id}", headers=headers)
                status_data = sr.json()
                s = status_data.get("status", "")
                print(f"  Poll {i+1}: {s}")
                
                if s in ("completed", "success", "done"):
                    print(f"\n✓ Run completed!")
                    break
                elif s in ("failed", "error", "cancelled"):
                    print(f"\n❌ Run failed: {s}")
                    print(f"Status data: {status_data}")
                    return
            
            # Get messages
            if thread_id:
                print(f"\nFetching messages from thread {thread_id}...")
                mr = await c.get(f"{WXO_HOST}/instances/{instance_id}/v1/orchestrate/threads/{thread_id}/messages", headers=headers)
                md = mr.json()
                print(f"Messages response: {str(md)[:500]}")
                
                msgs = md.get("messages", md) if isinstance(md, dict) else md
                asst = [m for m in msgs if isinstance(m, dict) and m.get("role") in ("assistant", "agent")]
                
                if asst:
                    content = asst[-1].get("content", "")
                    if isinstance(content, list):
                        content = " ".join(x.get("text","") for x in content if isinstance(x, dict))
                    print(f"\n✓ Agent response: {content[:200]}...")
                    return
            
            out = status_data.get("output") or status_data.get("response") or ""
            print(f"\n✓ Output: {str(out)[:200]}...")
            
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_wxo())

# Made with Bob
