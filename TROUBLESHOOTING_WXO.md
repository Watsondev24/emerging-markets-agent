# Watson Orchestrate Agent Troubleshooting

## Issue Summary
The wxO agent cannot be invoked via REST API. All attempted endpoints return 404 errors.

## What We Tried

### 1. Original Orchestrate Runs Endpoint
```
POST https://dev-wa.watson-orchestrate.ibm.com/instances/{instance_id}/v1/orchestrate/runs
Status: 404
```

### 2. Corrected API Host
```
POST https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/{instance_id}/v1/orchestrate/runs
Status: 500 - Database error
```

### 3. Watson Assistant v2 API
```
POST https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/{instance_id}/v2/assistants/{agent_id}/sessions
Status: 404
```

### 4. Chat API
```
POST https://us-south.watson-orchestrate.cloud.ibm.com/wxochat/api/chat/conversations
Status: 404
```

### 5. Agents REST API
```
GET https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/{instance_id}/v1/agents
Status: 404 - Resource does not exist
```

## Root Cause
The Watson Orchestrate instance appears to only support the **embed chat widget** interface, not direct REST API calls.

## Solutions

### Option 1: Use IBM watsonx Orchestrate Python SDK (Recommended)
Install the official SDK:
```bash
pip install ibm-watsonx-orchestrate
```

Then use it in your code:
```python
from ibm_watsonx_orchestrate import WatsonxOrchestrate

# Initialize client
wxo = WatsonxOrchestrate(
    api_key=WXO_API_KEY,
    instance_id=instance_id,
    region="us-south"
)

# Send message to agent
response = wxo.agents.message(
    agent_id=WXO_AGENT_ID,
    environment_id=WXO_ENVIRONMENT_ID,
    message="Should we expand into Vietnam?"
)
```

### Option 2: Use the Embed Chat Widget (Current Working Solution)
The embed chat widget in `meridian-ui.html` already works. Keep using it for the UI.

### Option 3: Contact IBM Support
Request API access or documentation for programmatic agent invocation for your instance.

### Option 4: Use WebSocket Connection (Advanced)
The embed widget likely uses WebSockets. You could:
1. Inspect the network traffic from the working embed widget
2. Replicate the WebSocket connection in your backend
3. This is complex and not recommended

## Recommended Next Steps

1. **Check IBM Cloud Console**
   - Go to your Watson Orchestrate instance
   - Look for "API Keys" or "Credentials" section
   - Check if there's specific API documentation for your instance

2. **Install the SDK**
   ```bash
   cd emerging-markets-agent
   pip install ibm-watsonx-orchestrate
   ```

3. **Update api.py to use SDK**
   Replace the manual HTTP calls with SDK calls

4. **Alternative: Keep Using Embed Widget**
   - The UI already works with the embed widget
   - For external API access, use the LangGraph agent (`/analyse` endpoint)
   - Use wxO agent only through the UI embed

## Current Working Configuration

### LangGraph Agent (✓ Working)
```bash
# Start API
uvicorn api:app --reload

# Test endpoint
curl -X POST http://localhost:8000/analyse \
  -H "Content-Type: application/json" \
  -d '{"query": "Should we expand into Vietnam?"}'
```

### wxO Embed Widget (✓ Working)
Open `meridian-ui.html` in browser - the embed chat widget works correctly.

## Configuration Details

From your embed script:
```javascript
orchestrationID: "42379027d430475b88345e10c0b3a286_c1d67b02-6cda-4be5-894b-736fbd491e51"
hostURL: "https://us-south.watson-orchestrate.cloud.ibm.com"
agentId: "446cb76b-ed0c-49e7-90d2-11f134ab7c84"
agentEnvironmentId: "553dc9d1-990a-46ad-a7aa-3a0c88c7efc9"
```

Environment variables:
```
WXO_API_KEY=ebsucH5_3W...
WXO_URL=https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/c1d67b02-6cda-4be5-894b-736fbd491e51