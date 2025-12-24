import express from 'express';
import { WebSocketServer } from 'ws';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { v4 as uuidv4 } from 'uuid';
import { GeminiProxy } from './services/geminiProxy';
import { WebSocketHandler } from './services/websocketHandler';
import { sessionManager } from './services/sessionManager';
import { toolRegistry } from './tools/toolRegistry';
import './tools/exampleTools'; // Register example tools

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;
const WS_PORT = process.env.WS_PORT || 3002;

// Middleware
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000', 'http://localhost:5173','http://127.0.0.1:5500'],
  credentials: true,
}));
app.use(express.json());

// Serve static files from public directory (test frontend)
app.use(express.static(path.join(__dirname, '../public')));

// Serve index.html for root route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Initialize services
const geminiProxy = new GeminiProxy(process.env.GEMINI_API_KEY || '');
const wsHandler = new WebSocketHandler(geminiProxy);

// REST API Routes

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Create a new session
app.post('/api/sessions', (req, res) => {
  const userId = req.body.userId || req.headers['x-user-id'] as string;
  const session = sessionManager.createSession(userId);
  
  res.json({
    sessionId: session.id,
    createdAt: session.createdAt,
  });
});

// Get session info
app.get('/api/sessions/:sessionId', (req, res) => {
  const session = sessionManager.getSession(req.params.sessionId);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }
  
  res.json({
    sessionId: session.id,
    userId: session.userId,
    createdAt: session.createdAt,
    memoryLength: session.memory.length,
  });
});

// Delete session
app.delete('/api/sessions/:sessionId', (req, res) => {
  const deleted = sessionManager.deleteSession(req.params.sessionId);
  if (!deleted) {
    return res.status(404).json({ error: 'Session not found' });
  }
  
  res.json({ success: true });
});

// Get available tools
app.get('/api/tools', (req, res) => {
  const tools = toolRegistry.getAll();
  res.json({
    tools: tools.map(tool => ({
      name: tool.name,
      description: tool.description,
      parameters: tool.parameters,
    })),
  });
});

// Start HTTP server
app.listen(PORT, () => {
  console.log(`[HTTP] Server running on http://localhost:${PORT}`);
  console.log(`[HTTP] Health check: http://localhost:${PORT}/health`);
});

// Start WebSocket server
const wss = new WebSocketServer({ port: parseInt(WS_PORT.toString()) });

wss.on('connection', (ws, req) => {
  // Extract session ID from query parameter or create new one
  const url = new URL(req.url || '', `http://${req.headers.host}`);
  let sessionId = url.searchParams.get('sessionId');

  if (!sessionId) {
    // Create new session if not provided
    const session = sessionManager.createSession();
    sessionId = session.id;
  } else {
    // Verify session exists
    const session = sessionManager.getSession(sessionId);
    if (!session) {
      ws.close(1008, 'Session not found');
      return;
    }
  }

  console.log(`[WS] New connection: ${sessionId}`);
  wsHandler.handleConnection(ws, sessionId);
});

wss.on('listening', () => {
  console.log(`[WS] WebSocket server running on ws://localhost:${WS_PORT}`);
  console.log(`[WS] Connect with: ws://localhost:${WS_PORT}?sessionId=<your-session-id>`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[Server] SIGTERM received, shutting down gracefully...');
  wss.close(() => {
    console.log('[WS] WebSocket server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('[Server] SIGINT received, shutting down gracefully...');
  wss.close(() => {
    console.log('[WS] WebSocket server closed');
    process.exit(0);
  });
});

