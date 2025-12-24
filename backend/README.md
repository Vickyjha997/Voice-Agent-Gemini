# Gemini Live Backend Proxy Server

A backend proxy server for Gemini Live API that enables function calling, session management, and WebSocket-based real-time audio communication.

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

- Node.js 18+ 
- Gemini API Key

## Installation

1. Install dependencies:
```bash
cd backend
npm install
```

2. Create a `.env` file in the `backend` directory with the following content:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=3001
WS_PORT=3002
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Replace `your_gemini_api_key_here` with your actual Gemini API key.

## Running

### Development Mode
```bash
npm run dev
```

The server will start and serve a test frontend at `http://localhost:3001`

### Production Mode
```bash
npm run build
npm start
```

## Testing

### Using the Built-in Test Frontend

1. Start the backend server:
   ```bash
   npm run dev
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:3001
   ```

3. Click "Connect" and allow microphone access when prompted

4. Start speaking! The test frontend will:
   - Show connection status
   - Display real-time transcriptions
   - Play audio responses
   - Show input/output volume levels

### Testing Function Calls

Try asking questions that trigger function calls:
- "What's the weather in New York?"
- "Execute a SQL query to get user data"
- "Get analytics for the last week"
- "Search the knowledge base for information about AI"

The backend will intercept these function calls, execute the tools, and return results to Gemini.

## API Endpoints

### REST API

- `GET /health` - Health check
- `POST /api/sessions` - Create a new session
- `GET /api/sessions/:sessionId` - Get session info
- `DELETE /api/sessions/:sessionId` - Delete a session
- `GET /api/tools` - List available function calling tools

### WebSocket API

Connect to: `ws://localhost:3002?sessionId=<session-id>`

#### Client → Server Messages

```typescript
// Connect to Gemini
{
  "type": "connect",
  "sessionId": "your-session-id"
}

// Send audio data
{
  "type": "audio",
  "data": {
    "data": "base64-encoded-pcm-audio",
    "mimeType": "audio/pcm;rate=16000"
  },
  "sessionId": "your-session-id"
}

// Disconnect
{
  "type": "disconnect",
  "sessionId": "your-session-id"
}

// Ping (keepalive)
{
  "type": "ping"
}
```

#### Server → Client Messages

```typescript
// Status update
{
  "type": "status",
  "data": { "status": "CONNECTED" },
  "sessionId": "your-session-id"
}

// Audio output
{
  "type": "audio",
  "data": {
    "audio": "base64-encoded-pcm-audio",
    "mimeType": "audio/pcm;rate=24000"
  },
  "sessionId": "your-session-id"
}

// Transcription
{
  "type": "transcription",
  "data": {
    "text": "Hello, how can I help?",
    "isUser": false,
    "isFinal": false
  },
  "sessionId": "your-session-id"
}

// Error
{
  "type": "error",
  "data": { "message": "Error description" },
  "sessionId": "your-session-id"
}
```

## Function Calling

The backend supports function calling through Gemini Live API. Tools are registered in `src/tools/exampleTools.ts`.

### Example Tools Included

1. **execute_sql_query** - Execute SQL queries (simulated)
2. **get_analytics** - Retrieve analytics data (simulated)
3. **search_knowledge_base** - RAG/vector search (simulated)
4. **call_external_api** - Generic external API calls (simulated)
5. **get_weather** - Weather information (simulated)

### Adding Custom Tools

1. Create a tool definition in `src/tools/exampleTools.ts` or a new file:

```typescript
import { toolRegistry } from './toolRegistry';

toolRegistry.register({
  name: 'my_custom_tool',
  description: 'Description of what the tool does',
  parameters: {
    type: 'object',
    properties: {
      param1: {
        type: 'string',
        description: 'Parameter description',
      },
    },
    required: ['param1'],
  },
  handler: async (args) => {
    // Your implementation
    const { param1 } = args;
    // Call external API, database, etc.
    return { result: 'success', data: {} };
  },
});
```

2. Import the tool file in `src/index.ts`:
```typescript
import './tools/myCustomTool';
```

### Real API Integration Example

Replace simulated responses with actual API calls:

```typescript
toolRegistry.register({
  name: 'get_weather',
  description: 'Get current weather information',
  parameters: {
    type: 'object',
    properties: {
      location: {
        type: 'string',
        description: 'City name',
      },
    },
    required: ['location'],
  },
  handler: async (args) => {
    const { location } = args;
    const apiKey = process.env.WEATHER_API_KEY;
    const response = await fetch(
      `https://api.weather.com/v1/current?location=${location}&key=${apiKey}`
    );
    const data = await response.json();
    return data;
  },
});
```

## Session Management

Sessions are automatically created when clients connect. Each session:
- Has a unique ID
- Maintains conversation memory (last 50 messages)
- Auto-expires after 30 minutes of inactivity
- Can be associated with a user ID

## Frontend Integration

Update your frontend to connect to the backend WebSocket server instead of directly to Gemini:

```typescript
// Create session first
const response = await fetch('http://localhost:3001/api/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
});
const { sessionId } = await response.json();

// Connect WebSocket
const ws = new WebSocket(`ws://localhost:3002?sessionId=${sessionId}`);

// Send connect message
ws.send(JSON.stringify({ type: 'connect', sessionId }));

// Send audio
ws.send(JSON.stringify({
  type: 'audio',
  data: audioBlob,
  sessionId,
}));
```

## Security Considerations

For production:
1. Add authentication middleware
2. Validate and sanitize all inputs
3. Rate limit WebSocket connections
4. Use HTTPS/WSS
5. Implement proper error handling
6. Add request logging and monitoring

## Troubleshooting

- **Connection refused**: Check if ports 3001 and 3002 are available
- **API key error**: Verify `GEMINI_API_KEY` in `.env`
- **CORS errors**: Update `ALLOWED_ORIGINS` in `.env`
- **Function calls not working**: Check tool registration in `src/tools/exampleTools.ts`

## License

MIT

