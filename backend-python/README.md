# Gemini Live Backend - Python Implementation

A Python backend proxy server for Gemini Live API that enables function calling, session management, and WebSocket-based real-time audio communication.

## Architecture

```
┌────────────┐
│  User Mic  │
└─────┬──────┘
      ↓
┌─────────────────┐
│ Frontend (WS)   │
│ Audio Capture   │
└─────┬───────────┘
      ↓
┌─────────────────────────┐
│ Your Backend (Proxy)    │
│ - Auth                  │
│ - Session Memory        │
│ - Tool Router           │
└─────┬──────────────────┘
      ↓
┌─────────────────────────┐
│ Gemini Live API         │
│ (Native Audio Brain)   │
│                         │
│  - Emotion              │
│  - Proactive Audio      │
│  - Barge-in             │
│  - Function Calling     │
└─────┬──────────────────┘
      ↓ function call
┌─────────────────────────┐
│ External LLM / RAG / DB │
│ - SQL Agent             │
│ - Analytics             │
│ - Knowledge Engine      │
└─────────┬───────────────┘
          ↓
     Tool Result
          ↓
┌─────────────────────────┐
│ Gemini Live             │
│ (Formats + speaks)      │
└─────────────────────────┘
```

## Features

- ✅ **WebSocket Proxy**: Real-time bidirectional audio streaming
- ✅ **Function Calling**: Execute external APIs, SQL queries, analytics, and more
- ✅ **Session Management**: Per-user session tracking with memory
- ✅ **Tool Registry**: Extensible system for adding custom tools
- ✅ **Authentication Ready**: Structure for adding auth middleware
- ✅ **CORS Support**: Configurable allowed origins

## Prerequisites

- Python 3.9+
- Gemini API Key

## Quick Start

1. **Setup environment:**
   ```bash
   cd backend-python
   python -m venv venv
   # Activate: venv\Scripts\activate (Windows) or source venv/bin/activate (macOS/Linux)
   pip install -r requirements.txt
   ```

2. **Configure:**
   ```bash
   # Copy example env file
   copy .env.example .env  # Windows
   # or
   cp .env.example .env    # macOS/Linux
   
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Run:**
   ```bash
   python main.py
   ```

4. **Test:**
   - Open browser: `http://localhost:3001`
   - Click "Connect" and allow microphone access
   - Start speaking!

For detailed instructions, see [RUN_AND_TEST.md](RUN_AND_TEST.md)

## Installation

1. Create a virtual environment (recommended):
```bash
cd backend-python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the `backend-python` directory with the following content:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=3001
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5500
```

Replace `your_gemini_api_key_here` with your actual Gemini API key.

## Running

### Development Mode
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --port 3001
```

The server will start and serve the API at `http://localhost:3001`

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 3001
```

## API Endpoints

### REST API

- `GET /health` - Health check
- `POST /api/sessions` - Create a new session
- `GET /api/sessions/:sessionId` - Get session info
- `DELETE /api/sessions/:sessionId` - Delete a session
- `GET /api/tools` - List available function calling tools

### WebSocket API

Connect to: `ws://localhost:3001/ws?sessionId=<session-id>`

## Testing

### Using the Test Frontend

1. Start the backend server:
   ```bash
   python main.py
   ```

2. The test frontend from the TypeScript backend can be used, or you can create your own frontend that connects to the WebSocket endpoint.

3. Connect to the WebSocket and start sending audio data.

### Testing Function Calls

Try asking questions that trigger function calls:
- "What's the weather in New York?"
- "Execute a SQL query to get user data"
- "Get analytics for the last week"
- "Search the knowledge base for information about AI"

The backend will intercept these function calls, execute the tools, and return results to Gemini.

## Project Structure

```
backend-python/
├── main.py                 # FastAPI application entry point
├── models.py               # Data models and types
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── services/
│   ├── gemini_proxy.py    # Gemini Live API proxy
│   ├── session_manager.py # Session management
│   └── websocket_handler.py # WebSocket connection handling
├── tools/
│   ├── tool_registry.py   # Tool registry system
│   └── example_tools.py   # Example function calling tools
└── utils/
    └── audio_utils.py     # Audio utility functions
```

## Differences from TypeScript Version

1. **Framework**: Uses FastAPI instead of Express
2. **WebSocket**: Uses FastAPI's built-in WebSocket support
3. **Async**: Uses Python's `async/await` syntax
4. **Package Management**: Uses `requirements.txt` instead of `package.json`
5. **Type System**: Uses Python type hints and dataclasses

## Development

### Adding New Tools

To add a new function calling tool, edit `tools/example_tools.py`:

```python
async def my_custom_tool_handler(args: dict):
    """Custom tool handler"""
    # Your implementation
    return {"result": "success"}

tool_registry.register(ToolDefinition(
    name='my_custom_tool',
    description='Description of what the tool does',
    parameters={
        'type': 'object',
        'properties': {
            'param1': {
                'type': 'string',
                'description': 'Parameter description'
            }
        },
        'required': ['param1']
    },
    handler=my_custom_tool_handler
))
```

## Notes

- The Python implementation follows the same architecture and API as the TypeScript version
- All endpoints and WebSocket message formats are compatible
- The frontend from the TypeScript version should work with this Python backend

## Important: Google GenAI SDK API

The `google-genai` Python SDK API may differ from the TypeScript version. The implementation in `services/gemini_proxy.py` uses a structure that should work, but you may need to adjust it based on:

1. The actual `google-genai` Python SDK version you're using
2. The official Python SDK documentation

If you encounter issues with the Gemini Live API connection, please refer to the official Google GenAI Python SDK documentation and adjust the `connect_session` method in `services/gemini_proxy.py` accordingly.

The key methods that may need adjustment:
- `client.aio.live.connect()` - Connection method
- `session.send_realtime_input()` or `session.sendRealtimeInput()` - Sending audio
- `session.send_tool_response()` or `session.sendToolResponse()` - Sending function results
- `session.close()` - Closing the session

## Getting Help

If you have the official Google GenAI Python SDK documentation, please share it and we can update the implementation to match the exact API structure.

