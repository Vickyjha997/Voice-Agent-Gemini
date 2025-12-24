/**
 * Example Frontend Client for connecting to the Backend WebSocket Server
 * 
 * This shows how to update your frontend to connect through the backend proxy
 * instead of directly to Gemini Live API.
 */

import { createPcmBlob } from '../../services/audioUtils'; // Adjust path as needed

export class BackendWebSocketClient {
  private ws: WebSocket | null = null;
  private sessionId: string | null = null;
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private inputSource: MediaStreamAudioSourceNode | null = null;
  private outputAudioContext: AudioContext | null = null;
  private outputNode: GainNode | null = null;
  private nextStartTime: number = 0;
  private audioSources: Set<AudioBufferSourceNode> = new Set();

  private onStatusChange?: (status: string) => void;
  private onTranscription?: (text: string, isUser: boolean, isFinal: boolean) => void;
  private onVolumeChange?: (input: number, output: number) => void;

  constructor(
    onStatusChange?: (status: string) => void,
    onTranscription?: (text: string, isUser: boolean, isFinal: boolean) => void,
    onVolumeChange?: (input: number, output: number) => void
  ) {
    this.onStatusChange = onStatusChange;
    this.onTranscription = onTranscription;
    this.onVolumeChange = onVolumeChange;
  }

  async connect(backendUrl: string = 'http://localhost:3001', wsUrl: string = 'ws://localhost:3002') {
    try {
      // 1. Create a session via REST API
      const response = await fetch(`${backendUrl}/api/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const { sessionId } = await response.json();
      this.sessionId = sessionId;

      // 2. Setup audio contexts
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000,
      });
      this.outputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 24000,
      });

      // 3. Setup input audio
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.inputSource = this.audioContext.createMediaStreamSource(stream);
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
      this.inputSource.connect(this.processor);
      this.processor.connect(this.audioContext.destination);

      // 4. Setup output audio
      this.outputNode = this.outputAudioContext.createGain();
      this.outputNode.connect(this.outputAudioContext.destination);

      // 5. Connect WebSocket
      this.ws = new WebSocket(`${wsUrl}?sessionId=${sessionId}`);

      this.ws.onopen = () => {
        // Send connect message
        this.ws?.send(JSON.stringify({
          type: 'connect',
          sessionId: this.sessionId,
        }));
        this.onStatusChange?.('CONNECTING');
      };

      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.onStatusChange?.('ERROR');
      };

      this.ws.onclose = () => {
        this.onStatusChange?.('DISCONNECTED');
        this.cleanup();
      };

      // 6. Start audio processing
      this.setupAudioProcessing();

    } catch (error) {
      console.error('Connection failed:', error);
      this.onStatusChange?.('ERROR');
      this.cleanup();
    }
  }

  private setupAudioProcessing() {
    if (!this.processor) return;

    this.processor.onaudioprocess = (e) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.sessionId) return;

      const inputData = e.inputBuffer.getChannelData(0);
      const pcmBlob = createPcmBlob(inputData);

      this.ws.send(JSON.stringify({
        type: 'audio',
        data: pcmBlob,
        sessionId: this.sessionId,
      }));
    };
  }

  private handleMessage(message: any) {
    switch (message.type) {
      case 'status':
        this.onStatusChange?.(message.data.status);
        break;

      case 'audio':
        if (message.data.interrupt) {
          this.stopAllAudio();
          this.nextStartTime = this.outputAudioContext?.currentTime || 0;
        } else if (message.data.audio && this.outputAudioContext && this.outputNode) {
          this.playAudio(message.data.audio, message.data.mimeType);
        }
        break;

      case 'transcription':
        this.onTranscription?.(
          message.data.text,
          message.data.isUser,
          message.data.isFinal
        );
        break;

      case 'error':
        console.error('Server error:', message.data.message);
        break;
    }
  }

  private async playAudio(base64Audio: string, mimeType: string) {
    if (!this.outputAudioContext || !this.outputNode) return;

    try {
      // Decode base64 audio
      const binaryString = atob(base64Audio);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Convert PCM to AudioBuffer
      const dataInt16 = new Int16Array(bytes.buffer);
      const frameCount = dataInt16.length;
      const buffer = this.outputAudioContext.createBuffer(1, frameCount, 24000);
      const channelData = buffer.getChannelData(0);

      for (let i = 0; i < frameCount; i++) {
        channelData[i] = dataInt16[i] / 32768.0;
      }

      // Schedule playback
      this.nextStartTime = Math.max(this.nextStartTime, this.outputAudioContext.currentTime);
      const source = this.outputAudioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(this.outputNode);
      source.start(this.nextStartTime);

      this.nextStartTime += buffer.duration;
      this.audioSources.add(source);

      source.onended = () => {
        this.audioSources.delete(source);
      };
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  }

  private stopAllAudio() {
    this.audioSources.forEach(source => {
      try { source.stop(); } catch (e) {}
    });
    this.audioSources.clear();
  }

  async disconnect() {
    if (this.ws && this.sessionId) {
      this.ws.send(JSON.stringify({
        type: 'disconnect',
        sessionId: this.sessionId,
      }));
      this.ws.close();
    }
    this.cleanup();
  }

  private cleanup() {
    if (this.processor) {
      this.processor.disconnect();
      this.processor.onaudioprocess = null;
      this.processor = null;
    }

    if (this.inputSource) {
      this.inputSource.disconnect();
      this.inputSource = null;
    }

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    if (this.outputAudioContext) {
      this.outputAudioContext.close();
      this.outputAudioContext = null;
    }

    this.stopAllAudio();
    this.ws = null;
    this.sessionId = null;
  }
}

// Usage example:
/*
const client = new BackendWebSocketClient(
  (status) => console.log('Status:', status),
  (text, isUser, isFinal) => console.log('Transcription:', text, isUser, isFinal),
  (input, output) => console.log('Volume:', input, output)
);

await client.connect();
// ... later
await client.disconnect();
*/

