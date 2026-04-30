import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import asyncio
import httpx

WXO_API_KEY = os.getenv("WXO_API_KEY")
WXO_URL = os.getenv("WXO_URL")
WXO_AGENT_ID = "446cb76b-ed0c-49e7-90d2-11f134ab7c84"

async def get_iam_token(api_key):
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post("https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key})
        if r.status_code != 200:
            raise Exception(f"IAM failed: {r.text}")
        return r.json()["access_token"]

async def test_sdk():
    from ibm_watsonx_orchestrate.client.chat.run_client import RunClient
    from ibm_watsonx_orchestrate.client.threads.threads_client import ThreadsClient
    
    print("Getting IAM token...")
    token = await get_iam_token(WXO_API_KEY)
    print("✓ Token obtained")
    
    # Initialize SDK clients (api_key parameter takes the IAM token)
    run_client = RunClient(base_url=WXO_URL, api_key=token)
    threads_client = ThreadsClient(base_url=WXO_URL, api_key=token)
    
    print(f"\nSending message to agent {WXO_AGENT_ID}...")
    
    # Create run
    run_response = run_client.create_run(
        message="Should we expand into Vietnam?",
        agent_id=WXO_AGENT_ID
    )
    
    run_id = run_response.get("run_id")
    thread_id = run_response.get("thread_id")
    print(f"✓ Run created: run_id={run_id}, thread_id={thread_id}")
    
    # Wait for completion
    print("Waiting for response...")
    final_status = run_client.wait_for_run_completion(run_id, poll_interval=2, max_retries=60)
    
    status = final_status.get("status", "").lower()
    print(f"✓ Run status: {status}")
    
    # Get messages
    if thread_id:
        messages_data = threads_client.get_thread_messages(thread_id)
        # messages_data might be a list directly or a dict with "messages" key
        messages = messages_data if isinstance(messages_data, list) else messages_data.get("messages", [])
        
        assistant_messages = [
            msg for msg in messages
            if isinstance(msg, dict) and msg.get("role") in ("assistant", "agent")
        ]
        
        if assistant_messages:
            last_message = assistant_messages[-1]
            content = last_message.get("content", "")
            
            if isinstance(content, list):
                response_text = " ".join(
                    item.get("text", "") 
                    for item in content 
                    if isinstance(item, dict) and item.get("text")
                )
            else:
                response_text = str(content)
            
            print(f"\n✓ Agent Response:\n{response_text[:500]}...")

if __name__ == "__main__":
    asyncio.run(test_sdk())

# Made with Bob
