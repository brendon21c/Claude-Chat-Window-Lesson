# Workflow: Claude Chat Window

## Objective
Build a simple browser-based chat interface that sends multi-turn conversations to the Anthropic API and streams responses back to the user.

## Required Inputs
- `ANTHROPIC_API_KEY` in `.env`
- Python 3.8+

## Stack
- **Backend**: Python + Flask (`tools/app.py`)
- **Frontend**: Single HTML file served by Flask (`tools/templates/index.html`)
- **API**: Anthropic Python SDK (`anthropic`)
- **Model**: `claude-haiku-4-5` (fast and cheap for learning)

## Tools Used
- `tools/app.py` — Flask server, API calls, streaming
- `tools/templates/index.html` — Chat UI

## Steps
1. Install dependencies: `pip install flask anthropic python-dotenv`
2. Run: `python tools/app.py`
3. Open browser at `http://localhost:5000`

## Expected Output
A working chat window at `http://localhost:5000` that:
- Displays a message history
- Sends user messages to Claude
- Streams the response back token-by-token
- Maintains multi-turn conversation history in the session

## Edge Cases & Known Constraints
- API key must be set in `.env` (not committed to git)
- Conversation history lives in-memory per Flask session; restarting the server clears it
- Streaming requires the Flask response to use `text/event-stream` content type
