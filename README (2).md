# Emerging Markets Intelligence Agent

A LangGraph agent that analyses emerging markets and produces investment entry briefs.

## Setup (copy these commands one by one into your terminal)

### 1. Create a project folder and enter it
```bash
mkdir emerging-markets-agent
cd emerging-markets-agent
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate it
# On Mac/Linux:
```bash
source venv/bin/activate
```
# On Windows:
```bash
venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install langgraph langchain-google-genai langchain-core tavily-python python-dotenv rich
```

### 5. Create your .env file
Create a file called `.env` in the project folder and add:
```
GOOGLE_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here
```

### 6. Copy all the .py files from this project into the folder

### 7. Run the agent
```bash
python main.py
```
