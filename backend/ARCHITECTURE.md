# Architecture Overview

## System Architecture

```
┌────────────┐
│  User Mic  │
└─────┬──────┘
      ↓
┌─────────────────┐
│ Frontend (WS)   │
│ Audio Capture   │
└─────┬───────────┘
      ↓ WebSocket
┌─────────────────────────┐
│ Your Backend (Proxy)    │
│ - Auth                  │
│ - Session Memory        │
│ - Tool Router           │
└─────┬──────────────────┘
      ↓ HTTP/WebSocket
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

## Component Breakdown

### 1. Frontend Layer
- Captures audio from user's microphone
- Connects to backend via WebSocket
- Sends audio chunks in real-time
- Receives and plays back audio responses
- Displays transcriptions

### 2. Backend Proxy Layer

#### WebSocket Handler (`websocketHandler.ts`)
- Manages WebSocket connections from frontend
- Routes messages between frontend and Gemini
- Handles connection lifecycle

#### Gemini Proxy (`geminiProxy.ts`)
- Establishes connection to Gemini Live API
- Manages Gemini session lifecycle
- Intercepts function calls
- Routes function responses back to Gemini

#### Session Manager (`sessionManager.ts`)
- Creates and manages user sessions
- Stores conversation memory
- Auto-cleans expired sessions
- Tracks session metadata

#### Tool Registry (`toolRegistry.ts`)
- Central registry for all function calling tools
- Executes tool handlers
- Formats tools for Gemini API
- Manages tool lifecycle

### 3. Gemini Live API
- Processes audio input
- Generates audio responses
- Handles emotion, barge-in, proactive audio
- Initiates function calls when needed

### 4. External Services (via Function Calls)
- SQL databases
- Analytics APIs
- RAG/Vector databases
- External APIs
- Knowledge bases

## Data Flow

### Audio Input Flow
1. User speaks → Frontend captures audio
2. Frontend → WebSocket → Backend
3. Backend → Gemini Live API
4. Gemini processes audio

### Function Call Flow
1. Gemini decides to call a function
2. Backend intercepts function call
3. Backend executes registered tool handler
4. Tool handler calls external API/DB
5. Backend sends result back to Gemini
6. Gemini continues with audio response

### Audio Output Flow
1. Gemini generates audio response
2. Backend receives audio from Gemini
3. Backend → WebSocket → Frontend
4. Frontend plays audio to user

## Session Management

Each session:
- Has unique ID (UUID)
- Maintains conversation memory (last 50 messages)
- Auto-expires after 30 minutes
- Can be associated with user ID
- Stores Gemini session reference

## Function Calling

### Tool Registration
Tools are registered at startup in `exampleTools.ts`:
```typescript
toolRegistry.register({
  name: 'tool_name',
  description: '...',
  parameters: {...},
  handler: async (args) => {...}
});
```

### Tool Execution
1. Gemini sends function call request
2. Backend finds tool in registry
3. Executes handler with provided args
4. Returns result to Gemini
5. Gemini incorporates result into response

## Security Considerations

### Current Implementation
- Basic CORS protection
- Session-based isolation
- No authentication (add for production)

### Production Recommendations
- Add JWT authentication
- Rate limiting
- Input validation
- HTTPS/WSS only
- API key rotation
- Request logging
- Error sanitization

## Scalability

### Current Limitations
- In-memory session storage (single server)
- No load balancing
- No persistent storage

### Production Scaling
- Use Redis for session storage
- Add load balancer
- Implement database for memory persistence
- Add message queue for async operations
- Horizontal scaling with multiple instances

## Error Handling

- WebSocket connection errors → Reconnect logic
- Gemini API errors → Error messages to frontend
- Function call errors → Error responses to Gemini
- Session errors → Cleanup and notification

## Monitoring

Recommended metrics:
- Active sessions count
- WebSocket connection count
- Function call execution time
- Audio processing latency
- Error rates
- API response times

