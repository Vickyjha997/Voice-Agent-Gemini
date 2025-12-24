# Quick Start Guide

## 1. Setup Environment

```bash
cd backend
npm install
```

Create a `.env` file:
```env
GEMINI_API_KEY=your_actual_api_key_here
PORT=3001
WS_PORT=3002
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 2. Start the Backend Server

```bash
npm run dev
```

You should see:
```
[HTTP] Server running on http://localhost:3001
[HTTP] Health check: http://localhost:3001/health
[WS] WebSocket server running on ws://localhost:3002
```

## 3. Test the API

### Create a Session
```bash
curl -X POST http://localhost:3001/api/sessions
```

Response:
```json
{
  "sessionId": "uuid-here",
  "createdAt": "2025-01-XX..."
}
```

### Check Available Tools
```bash
curl http://localhost:3001/api/tools
```

### Health Check
```bash
curl http://localhost:3001/health
```

## 4. Test with Built-in Frontend

The backend includes a test frontend! Just open your browser:

```
http://localhost:3001
```

Click "Connect" and start speaking. The test UI will show:
- Connection status
- Real-time transcriptions
- Audio playback
- Volume meters

## 5. Connect from Your Own Frontend

See `examples/frontend-client-example.ts` for a complete example of how to connect your frontend to the backend.

Basic connection flow:
1. Create session via REST API: `POST /api/sessions`
2. Connect WebSocket: `ws://localhost:3002?sessionId=<session-id>`
3. Send `{ type: 'connect' }` message
4. Send audio data: `{ type: 'audio', data: {...} }`
5. Receive audio/transcription messages

## 6. Function Calling

Function calling works automatically! When Gemini decides to call a function:
1. Backend intercepts the function call
2. Executes the registered tool handler
3. Sends result back to Gemini
4. Gemini continues with audio response

Try asking in the test UI:
- "What's the weather in New York?"
- "Execute a SQL query to get user data"
- "Get analytics for the last week"
- "Search the knowledge base for AI information"

## Troubleshooting

- **Port already in use**: Change `PORT` or `WS_PORT` in `.env`
- **API key error**: Verify `GEMINI_API_KEY` is set correctly
- **CORS errors**: Add your frontend URL to `ALLOWED_ORIGINS`
- **Function calls not working**: Check console logs for function call execution

