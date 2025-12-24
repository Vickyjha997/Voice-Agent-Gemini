import { WebSocket } from 'ws';
import { ClientMessage, ServerMessage, ConnectionState, TranscriptionData } from '../types';
import { sessionManager } from './sessionManager';
import { GeminiProxy } from './geminiProxy';
import { validateAudioData } from '../utils/audioUtils';

/**
 * WebSocket Handler - Manages client connections and message routing
 */
export class WebSocketHandler {
  private geminiProxy: GeminiProxy;
  private clients: Map<string, WebSocket> = new Map();

  constructor(geminiProxy: GeminiProxy) {
    this.geminiProxy = geminiProxy;
  }

  handleConnection(ws: WebSocket, sessionId: string) {
    this.clients.set(sessionId, ws);

    ws.on('message', async (data: Buffer) => {
      try {
        const message: ClientMessage = JSON.parse(data.toString());
        await this.handleMessage(sessionId, message);
      } catch (error) {
        console.error(`[WS] Error handling message from ${sessionId}:`, error);
        this.send(sessionId, {
          type: 'error',
          data: { message: 'Invalid message format' },
          sessionId,
        });
      }
    });

    ws.on('close', () => {
      console.log(`[WS] Client ${sessionId} disconnected`);
      this.handleDisconnect(sessionId);
      this.clients.delete(sessionId);
    });

    ws.on('error', (error) => {
      console.error(`[WS] Error for ${sessionId}:`, error);
      this.handleDisconnect(sessionId);
      this.clients.delete(sessionId);
    });

    // Send connection confirmation
    this.send(sessionId, {
      type: 'status',
      data: { status: ConnectionState.CONNECTING },
      sessionId,
    });
  }

  private async handleMessage(sessionId: string, message: ClientMessage) {
    // #region agent log
    fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'websocketHandler.ts:55',message:'handleMessage called',data:{sessionId,messageType:message.type},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    switch (message.type) {
      case 'connect':
        // #region agent log
        fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'websocketHandler.ts:58',message:'connect message received',data:{sessionId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
        await this.handleConnect(sessionId);
        break;

      case 'audio':
        // #region agent log
        const sessionBeforeAudio = sessionManager.getSession(sessionId);
        fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'websocketHandler.ts:62',message:'audio message received',data:{sessionId,hasSession:!!sessionBeforeAudio,hasGeminiSession:!!sessionBeforeAudio?.geminiSession},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
        // #endregion
        await this.handleAudio(sessionId, message.data);
        break;

      case 'disconnect':
        await this.handleDisconnect(sessionId);
        break;

      case 'ping':
        this.send(sessionId, { type: 'pong', sessionId });
        break;

      default:
        console.warn(`[WS] Unknown message type: ${message.type}`);
    }
  }

  private async handleConnect(sessionId: string) {
    // #region agent log
    fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'websocketHandler.ts:78',message:'handleConnect started',data:{sessionId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    const session = sessionManager.getSession(sessionId);
    if (!session) {
      this.send(sessionId, {
        type: 'error',
        data: { message: 'Session not found' },
        sessionId,
      });
      return;
    }

    try {
      // #region agent log
      fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'websocketHandler.ts:90',message:'calling connectSession',data:{sessionId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      await this.geminiProxy.connectSession(
        sessionId,
        (geminiMessage) => this.handleGeminiMessage(sessionId, geminiMessage),
        (error) => {
          console.error(`[Gemini] Error for session ${sessionId}:`, error);
          this.send(sessionId, {
            type: 'error',
            data: { message: error.message },
            sessionId,
          });
        }
      );
      // #region agent log
      const sessionAfterConnect = sessionManager.getSession(sessionId);
      fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'websocketHandler.ts:102',message:'connectSession completed',data:{sessionId,hasGeminiSession:!!sessionAfterConnect?.geminiSession},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion

      this.send(sessionId, {
        type: 'status',
        data: { status: ConnectionState.CONNECTED },
        sessionId,
      });
      // #region agent log
      fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'websocketHandler.ts:107',message:'CONNECTED status sent to client',data:{sessionId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
    } catch (error: any) {
      console.error(`[WS] Connection error for ${sessionId}:`, error);
      this.send(sessionId, {
        type: 'status',
        data: { status: ConnectionState.ERROR },
        sessionId,
      });
    }
  }

  private async handleAudio(sessionId: string, audioData: any) {
    if (!validateAudioData(audioData)) {
      this.send(sessionId, {
        type: 'error',
        data: { message: 'Invalid audio data format' },
        sessionId,
      });
      return;
    }

    try {
      await this.geminiProxy.sendAudio(sessionId, audioData);
    } catch (error: any) {
      console.error(`[WS] Audio send error for ${sessionId}:`, error);
      this.send(sessionId, {
        type: 'error',
        data: { message: error.message },
        sessionId,
      });
    }
  }

  private async handleDisconnect(sessionId: string) {
    try {
      await this.geminiProxy.disconnectSession(sessionId);
      this.send(sessionId, {
        type: 'status',
        data: { status: ConnectionState.DISCONNECTED },
        sessionId,
      });
    } catch (error) {
      console.error(`[WS] Disconnect error for ${sessionId}:`, error);
    }
  }

  private handleGeminiMessage(sessionId: string, message: any) {
    // Extract function calls (for testing/debugging visibility)
    const functionCalls = message.serverContent?.modelTurn?.parts?.filter(
      (part: any) => part.functionCall
    );
    if (functionCalls && functionCalls.length > 0) {
      functionCalls.forEach((part: any) => {
        const functionCall = part.functionCall;
        this.send(sessionId, {
          type: 'function_call',
          data: {
            name: functionCall.name,
            args: functionCall.args || {},
            callId: functionCall.name + '_' + Date.now(),
          },
          sessionId,
        });
      });
    }

    // Extract audio data
    const base64Audio = message.serverContent?.modelTurn?.parts?.[0]?.inlineData?.data;
    if (base64Audio) {
      this.send(sessionId, {
        type: 'audio',
        data: { audio: base64Audio, mimeType: 'audio/pcm;rate=24000' },
        sessionId,
      });
    }

    // Extract transcriptions
    const inputTranscript = message.serverContent?.inputTranscription;
    if (inputTranscript) {
      const transcription: TranscriptionData = {
        text: inputTranscript.text,
        isUser: true,
        isFinal: false,
      };
      this.send(sessionId, {
        type: 'transcription',
        data: transcription,
        sessionId,
      });
    }

    const outputTranscript = message.serverContent?.outputTranscription;
    if (outputTranscript) {
      const transcription: TranscriptionData = {
        text: outputTranscript.text,
        isUser: false,
        isFinal: false,
      };
      this.send(sessionId, {
        type: 'transcription',
        data: transcription,
        sessionId,
      });
    }

    // Handle turn complete
    if (message.serverContent?.turnComplete) {
      this.send(sessionId, {
        type: 'transcription',
        data: { text: '', isUser: true, isFinal: true },
        sessionId,
      });
      this.send(sessionId, {
        type: 'transcription',
        data: { text: '', isUser: false, isFinal: true },
        sessionId,
      });
    }

    // Handle interruptions
    if (message.serverContent?.interrupted) {
      this.send(sessionId, {
        type: 'audio',
        data: { interrupt: true },
        sessionId,
      });
    }
  }

  send(sessionId: string, message: ServerMessage) {
    const client = this.clients.get(sessionId);
    if (client && client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  }

  broadcast(message: ServerMessage) {
    for (const [sessionId, client] of this.clients.entries()) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({ ...message, sessionId }));
      }
    }
  }
}

