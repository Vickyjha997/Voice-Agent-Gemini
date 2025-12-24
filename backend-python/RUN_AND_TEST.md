# How to Run and Test the Python Backend

This guide will walk you through setting up, running, and testing the Python backend.

## Prerequisites

1. **Python 3.9 or higher** - Check with: `python --version` or `python3 --version`
2. **pip** - Python package manager (usually comes with Python)
3. **Gemini API Key** - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Step 1: Setup Virtual Environment (Recommended)

```bash
# Navigate to the backend-python directory
cd backend-python

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- uvicorn (ASGI server)
- google-genai (Gemini API client)
- python-dotenv (environment variables)
- websockets (WebSocket support)

## Step 3: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   # On Windows PowerShell:
   Copy-Item .env.example .env
   # On macOS/Linux:
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   PORT=3001
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5500
   ```

   Replace `your_actual_api_key_here` with your actual Gemini API key.

## Step 4: Run the Backend Server

```bash
python main.py
```

You should see output like:
```
[HTTP] Server starting on http://localhost:3001
[HTTP] Health check: http://localhost:3001/health
[WS] WebSocket server will be available at ws://localhost:3001/ws
[WS] Connect with: ws://localhost:3001/ws?sessionId=<your-session-id>
INFO:     Uvicorn running on http://0.0.0.0:3001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The server is now running! Keep this terminal window open.

## Step 5: Test the Backend

### Option A: Using the Built-in Test Frontend

1. **Open your browser** and navigate to:
   ```
   http://localhost:3001
   ```

2. **You should see** the test interface with:
   - Connection status indicator
   - Connect/Disconnect buttons
   - Volume meters
   - Transcription box

3. **Click "Connect"** button
   - The browser will ask for microphone permission - **click "Allow"**
   - Wait for the status to change to "Connected"

4. **Start speaking!** 
   - You should see:
     - Your speech transcribed in the transcription box
     - The assistant's responses (both text and audio)
     - Volume meters showing input/output levels

### Option B: Test REST API Endpoints

Open a new terminal and test the endpoints:

#### 1. Health Check
```bash
# Using curl (macOS/Linux):
curl http://localhost:3001/health

# Using PowerShell (Windows):
Invoke-WebRequest -Uri http://localhost:3001/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2025-12-23T..."
}
```

#### 2. Create a Session
```bash
# Using curl:
curl -X POST http://localhost:3001/api/sessions \
  -H "Content-Type: application/json"

# Using PowerShell:
Invoke-WebRequest -Uri http://localhost:3001/api/sessions -Method POST -ContentType "application/json"
```

Expected response:
```json
{
  "sessionId": "uuid-here",
  "createdAt": "2025-12-23T..."
}
```

#### 3. Get Session Info
```bash
# Replace SESSION_ID with the sessionId from step 2
curl http://localhost:3001/api/sessions/SESSION_ID
```

#### 4. List Available Tools
```bash
curl http://localhost:3001/api/tools
```

Expected response:
```json
{
  "tools": [
    {
      "name": "get_weather",
      "description": "...",
      "parameters": {...}
    },
    ...
  ]
}
```

### Option C: Test WebSocket Connection

You can test the WebSocket using browser console or a WebSocket client:

1. **Open browser console** (F12) on `http://localhost:3001`
2. **Run this JavaScript**:
```javascript
// First create a session
fetch('http://localhost:3001/api/sessions', {method: 'POST'})
  .then(r => r.json())
  .then(data => {
    const sessionId = data.sessionId;
    console.log('Session ID:', sessionId);
    
    // Connect WebSocket
    const ws = new WebSocket(`ws://localhost:3001/ws?sessionId=${sessionId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      ws.send(JSON.stringify({type: 'connect', sessionId}));
    };
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      console.log('Message:', msg);
    };
    
    ws.onerror = (error) => console.error('Error:', error);
    ws.onclose = () => console.log('Closed');
  });
```

## Step 6: Test Function Calling

The backend includes example tools. To test function calling:

1. **Connect** using the test frontend
2. **Ask questions** that trigger function calls:
   - "What's the weather in New York?"
   - "Get analytics for the last week"
   - "Search the knowledge base for AI information"
   - "Execute a SQL query"

3. **Check the backend terminal** - you should see logs like:
   ```
   [Function Call] get_weather {'location': 'New York'}
   ```

4. **Check the frontend** - you should see function call notifications in the transcription box

## Troubleshooting

### Port Already in Use

If you get an error that port 3001 is already in use:

1. **Change the port** in `.env`:
   ```env
   PORT=3002
   ```

2. **Update the frontend** WebSocket URL to match

### Module Not Found Errors

If you get import errors:

```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Gemini API Errors

If you get Gemini API errors:

1. **Check your API key** in `.env` file
2. **Verify the key is valid** at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Check API quotas** - you may have hit rate limits

### WebSocket Connection Fails

1. **Check CORS settings** in `.env` - make sure your frontend URL is in `ALLOWED_ORIGINS`
2. **Check firewall** - make sure port 3001 is not blocked
3. **Check browser console** for detailed error messages

### Audio Not Working

1. **Check microphone permissions** - browser should prompt you
2. **Check browser compatibility** - Chrome/Edge work best
3. **Check volume meters** - if input volume is 0, microphone may not be working

## Development Mode

The server runs in development mode by default with auto-reload. Any changes to Python files will automatically restart the server.

To run in production mode:

```bash
uvicorn main:app --host 0.0.0.0 --port 3001 --workers 4
```

## Next Steps

- **Add custom tools**: Edit `tools/example_tools.py` to add your own function calling tools
- **Customize system prompt**: Edit the system instruction in `services/gemini_proxy.py`
- **Add authentication**: Implement JWT or session-based auth
- **Add database**: Connect to a database for persistent session storage

## Getting Help

If you encounter issues:

1. Check the terminal output for error messages
2. Check browser console (F12) for frontend errors
3. Verify all environment variables are set correctly
4. Make sure all dependencies are installed
5. Check that Python version is 3.9+

For issues with the Google GenAI SDK, refer to the official documentation and adjust `services/gemini_proxy.py` accordingly.

