import { GoogleGenAI, LiveServerMessage, Modality } from '@google/genai';
import { Session, TranscriptionData, FunctionCall, FunctionResult } from '../types';
import { sessionManager } from './sessionManager';
import { toolRegistry } from '../tools/toolRegistry';
import { decodeBase64 } from '../utils/audioUtils';

/**
 * Gemini Live API Proxy Service
 * Handles connection to Gemini Live API and manages function calling
 */
export class GeminiProxy {
  private ai: GoogleGenAI;
  private readonly MODEL_NAME = 'gemini-2.5-flash-native-audio-preview-09-2025';

  constructor(apiKey: string) {
    this.ai = new GoogleGenAI({ apiKey });
  }

  async connectSession(
    sessionId: string,
    onMessage: (message: LiveServerMessage) => void,
    onError: (error: Error) => void
  ): Promise<any> {
    const session = sessionManager.getSession(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    // Get available tools for function calling
    const tools = toolRegistry.getGeminiToolsFormat();
    // Format per Live API documentation: [{ functionDeclarations: [...] }]
    const toolsToUse = tools.length > 0 ? [{
      functionDeclarations: tools.map(tool => ({
        name: tool.name,
        description: tool.description,
        parameters: tool.parameters,
      }))
    }] : undefined;

    let geminiSession;
    try {
      geminiSession = await this.ai.live.connect({
      model: this.MODEL_NAME,
      config: {
        responseModalities: [Modality.AUDIO],
        inputAudioTranscription: {},
        outputAudioTranscription: {},
        systemInstruction: `You are a helpful AI voice assistant with access to various tools and APIs. 

IMPORTANT: You have access to function calling tools. When a user asks about:
- Weather information → Use the get_weather function
- Analytics or data queries → Use get_analytics or execute_sql_query functions  
- Searching for information → Use search_knowledge_base function
- External API calls → Use call_external_api function

You MUST use function calls when users request data, information retrieval, or external service interactions. Do not just respond without calling functions when they are needed.

Always explain what you're doing when calling functions.
Mostly try to respond in English unless the user speaks in another language.`,
        tools: toolsToUse as any,
      },
      callbacks: {
        onopen: () => {
          console.log(`[Gemini] Session ${sessionId} connected`);
        },
        onmessage: async (message: LiveServerMessage) => {
          // Handle function calls before passing message to client
          await this.handleFunctionCalls(message, sessionId, onMessage);
          
          // Pass the message to client
          onMessage(message);
        },
        onclose: () => {
          console.log(`[Gemini] Session ${sessionId} closed`);
        },
        onerror: (err) => {
          console.error(`[Gemini] Session ${sessionId} error:`, err);
          onError(err);
        },
      },
    });
    } catch (error: any) {
      throw error;
    }

    // Store gemini session
    sessionManager.updateSession(sessionId, { geminiSession });

    return geminiSession;
  }

  private async handleFunctionCalls(
    message: LiveServerMessage,
    sessionId: string,
    onMessage: (message: LiveServerMessage) => void
  ) {
    // Check for toolCall at top level (per Live API documentation)
    if (!(message as any).toolCall || !(message as any).toolCall.functionCalls || (message as any).toolCall.functionCalls.length === 0) {
      return;
    }

    const session = sessionManager.getSession(sessionId);
    if (!session || !session.geminiSession) {
      return;
    }

    const functionCalls = (message as any).toolCall.functionCalls;
    const functionResponses: any[] = [];

    // Process each function call
    for (const fc of functionCalls) {
      const toolName = fc.name || '';
      const args = fc.args || {};
      const callId = fc.id || toolName + '_' + Date.now();
      
      if (!toolName) {
        continue;
      }

      console.log(`[Function Call] ${toolName}`, args);

      // Execute the function
      const result = await toolRegistry.execute(toolName, args);

      // Build function response per Live API documentation
      const functionResponse = {
        id: callId,
        name: toolName,
        response: result.error ? { error: result.error } : result.result
      };
      functionResponses.push(functionResponse);
    }

    // Send function results back to Gemini using sendToolResponse (per Live API documentation)
    try {
      if (typeof session.geminiSession.sendToolResponse === 'function') {
        await session.geminiSession.sendToolResponse({ functionResponses: functionResponses });
      } else {
        console.warn(`[Function Call] sendToolResponse method not available on session`);
      }
    } catch (error: any) {
      console.error(`[Function Call] Error sending function responses:`, error);
    }
  }

  async sendAudio(sessionId: string, audioBlob: any): Promise<void> {
    const session = sessionManager.getSession(sessionId);
    if (!session || !session.geminiSession) {
      throw new Error('Session not found or not connected');
    }

    await session.geminiSession.sendRealtimeInput({ media: audioBlob });
  }

  async disconnectSession(sessionId: string): Promise<void> {
    const session = sessionManager.getSession(sessionId);
    if (!session || !session.geminiSession) {
      return;
    }

    // Close Gemini session if it has a close method
    if (typeof session.geminiSession.close === 'function') {
      await session.geminiSession.close();
    }

    sessionManager.updateSession(sessionId, { geminiSession: null });
  }
}

