"""WebSocket Handler - Manages client connections and message routing"""
import sys
import os
import json
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, Optional
from fastapi import WebSocket
from models import ConnectionState, TranscriptionData
from services.session_manager import session_manager
from services.gemini_proxy import GeminiProxy
from utils.audio_utils import validate_audio_data


class WebSocketHandler:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self, gemini_proxy: GeminiProxy):
        """Initialize WebSocket handler"""
        self.gemini_proxy = gemini_proxy
        self.clients: Dict[str, WebSocket] = {}
    
    async def handle_connection(self, ws: WebSocket, session_id: str):
        """Handle a new WebSocket connection"""
        await ws.accept()
        self.clients[session_id] = ws
        
        # Send connection confirmation
        await self.send(session_id, {
            'type': 'status',
            'data': {'status': ConnectionState.CONNECTING.value},
            'sessionId': session_id
        })
        
        try:
            while True:
                data = await ws.receive_text()
                try:
                    message = json.loads(data)
                    await self.handle_message(session_id, message)
                except json.JSONDecodeError:
                    await self.send(session_id, {
                        'type': 'error',
                        'data': {'message': 'Invalid message format'},
                        'sessionId': session_id
                    })
        except Exception as e:
            print(f"[WS] Error handling connection {session_id}: {e}")
        finally:
            await self.handle_disconnect(session_id)
            if session_id in self.clients:
                del self.clients[session_id]
    
    async def handle_message(self, session_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        msg_type = message.get('type')
        
        if msg_type == 'connect':
            await self.handle_connect(session_id)
        elif msg_type == 'audio':
            await self.handle_audio(session_id, message.get('data'))
        elif msg_type == 'disconnect':
            await self.handle_disconnect(session_id)
        elif msg_type == 'ping':
            await self.send(session_id, {'type': 'pong', 'sessionId': session_id})
        else:
            print(f"[WS] Unknown message type: {msg_type}")
    
    async def handle_connect(self, session_id: str):
        """Handle connect message"""
        session = session_manager.get_session(session_id)
        if not session:
            await self.send(session_id, {
                'type': 'error',
                'data': {'message': 'Session not found'},
                'sessionId': session_id
            })
            return
        
        try:
            async def on_message(msg):
                await self.handle_gemini_message(session_id, msg)
            
            async def on_error(err):
                await self.send(session_id, {
                    'type': 'error',
                    'data': {'message': str(err)},
                    'sessionId': session_id
                })
            
            await self.gemini_proxy.connect_session(session_id, on_message, on_error)
            
            await self.send(session_id, {
                'type': 'status',
                'data': {'status': ConnectionState.CONNECTED.value},
                'sessionId': session_id
            })
        except Exception as e:
            print(f"[WS] Connection error for {session_id}: {e}")
            await self.send(session_id, {
                'type': 'status',
                'data': {'status': ConnectionState.ERROR.value},
                'sessionId': session_id
            })
    
    async def handle_audio(self, session_id: str, audio_data: Any):
        """Handle audio data from client"""
        # #region agent log
        try:
            import json
            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
            has_data = audio_data is not None
            data_keys = list(audio_data.keys()) if isinstance(audio_data, dict) else None
            data_len = len(audio_data.get('data', '')) if isinstance(audio_data, dict) and 'data' in audio_data else None
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"websocket_handler.py:107","message":"Received audio from client","data":{"has_data":has_data,"data_keys":data_keys,"data_len":data_len,"is_valid":validate_audio_data(audio_data) if audio_data else False},"sessionId":"debug-session","runId":"run1","hypothesisId":"O","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        if not validate_audio_data(audio_data):
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"websocket_handler.py:120","message":"Invalid audio data format","data":{"audio_data_type":type(audio_data).__name__},"sessionId":"debug-session","runId":"run1","hypothesisId":"O","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            await self.send(session_id, {
                'type': 'error',
                'data': {'message': 'Invalid audio data format'},
                'sessionId': session_id
            })
            return
        
        try:
            await self.gemini_proxy.send_audio(session_id, audio_data)
        except Exception as e:
            # #region agent log
            try:
                import json
                import traceback
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"websocket_handler.py:135","message":"Audio send error","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"O","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            print(f"[WS] Audio send error for {session_id}: {e}")
            await self.send(session_id, {
                'type': 'error',
                'data': {'message': str(e)},
                'sessionId': session_id
            })
    
    async def handle_disconnect(self, session_id: str):
        """Handle disconnect"""
        try:
            await self.gemini_proxy.disconnect_session(session_id)
            await self.send(session_id, {
                'type': 'status',
                'data': {'status': ConnectionState.DISCONNECTED.value},
                'sessionId': session_id
            })
        except Exception as e:
            print(f"[WS] Disconnect error for {session_id}: {e}")
    
    async def handle_gemini_message(self, session_id: str, message: Any):
        """Handle message from Gemini"""
        # #region agent log
        try:
            import json
            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"websocket_handler.py:139","message":"handle_gemini_message called","data":{"session_id":session_id,"has_message":message is not None,"message_type":type(message).__name__},"sessionId":"debug-session","runId":"run1","hypothesisId":"M","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        # Extract function calls (for testing/debugging visibility)
        if hasattr(message, 'tool_call') and message.tool_call:
            tool_call = message.tool_call
            if hasattr(tool_call, 'function_calls') and tool_call.function_calls:
                for fc in tool_call.function_calls:
                    await self.send(session_id, {
                        'type': 'function_call',
                        'data': {
                            'name': getattr(fc, 'name', ''),
                            'args': getattr(fc, 'args', {}),
                            'callId': getattr(fc, 'name', '') + '_' + str(int(__import__('time').time() * 1000))
                        },
                        'sessionId': session_id
                    })
        
        # Extract audio data
        # #region agent log
        try:
            import json
            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
            has_data = hasattr(message, 'data')
            data_value = getattr(message, 'data', None)
            data_type = type(data_value).__name__ if data_value is not None else None
            has_server_content = hasattr(message, 'server_content')
            server_content_val = getattr(message, 'server_content', None)
            sc_info = None
            if server_content_val:
                sc_info = {
                    "has_model_turn": hasattr(server_content_val, 'model_turn'),
                    "model_turn": None
                }
                if hasattr(server_content_val, 'model_turn') and server_content_val.model_turn:
                    mt = server_content_val.model_turn
                    sc_info["model_turn"] = {
                        "has_parts": hasattr(mt, 'parts'),
                        "parts_count": len(mt.parts) if hasattr(mt, 'parts') and mt.parts else 0
                    }
                    if hasattr(mt, 'parts') and mt.parts:
                        parts_info = []
                        for i, part in enumerate(mt.parts):
                            part_info = {"index": i}
                            if hasattr(part, 'inline_data') and part.inline_data:
                                idata = part.inline_data
                                part_info["has_inline_data"] = True
                                part_info["has_data"] = hasattr(idata, 'data')
                                if hasattr(idata, 'data'):
                                    part_info["data_type"] = type(idata.data).__name__
                                    if isinstance(idata.data, bytes):
                                        part_info["data_len"] = len(idata.data)
                            else:
                                part_info["has_inline_data"] = False
                            parts_info.append(part_info)
                        sc_info["model_turn"]["parts_info"] = parts_info
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"websocket_handler.py:156","message":"Processing message for audio extraction","data":{"has_data":has_data,"data_type":data_type,"has_server_content":has_server_content,"server_content":sc_info},"sessionId":"debug-session","runId":"run1","hypothesisId":"M","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except Exception as log_err:
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"websocket_handler.py:156","message":"Error logging message structure","data":{"error":str(log_err)},"sessionId":"debug-session","runId":"run1","hypothesisId":"M","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
        # #endregion
        
        # Check response.data directly first (as shown in user's example)
        # Prefer response.data if available, otherwise check server_content
        audio_sent = False
        if hasattr(message, 'data') and message.data is not None:
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"websocket_handler.py:157","message":"Found response.data (direct audio)","data":{"data_type":type(message.data).__name__,"data_len":len(message.data) if isinstance(message.data, bytes) else None},"sessionId":"debug-session","runId":"run1","hypothesisId":"L","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            if isinstance(message.data, bytes):
                import base64
                audio_base64 = base64.b64encode(message.data).decode('utf-8')
                await self.send(session_id, {
                    'type': 'audio',
                    'data': {
                        'audio': audio_base64,
                        'mimeType': 'audio/pcm;rate=24000'
                    },
                    'sessionId': session_id
                })
                audio_sent = True
        
        # Also check server_content.model_turn.parts[].inline_data.data (structured format)
        # Only if we haven't already sent audio from response.data
        if not audio_sent and hasattr(message, 'server_content') and message.server_content:
            server_content = message.server_content
            if hasattr(server_content, 'model_turn') and server_content.model_turn:
                model_turn = server_content.model_turn
                if hasattr(model_turn, 'parts') and model_turn.parts:
                    for part in model_turn.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            inline_data = part.inline_data
                            if hasattr(inline_data, 'data'):
                                # #region agent log
                                try:
                                    import json
                                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                                    with open(log_path, 'a', encoding='utf-8') as f:
                                        f.write(json.dumps({"location":"websocket_handler.py:180","message":"Found audio in server_content.model_turn.parts","data":{"data_type":type(inline_data.data).__name__,"data_len":len(inline_data.data) if isinstance(inline_data.data, bytes) else None},"sessionId":"debug-session","runId":"run1","hypothesisId":"L","timestamp":int(__import__('time').time()*1000)}) + '\n')
                                except: pass
                                # #endregion
                                import base64
                                audio_data = inline_data.data
                                if isinstance(audio_data, bytes):
                                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                                else:
                                    audio_base64 = audio_data  # Already base64 string
                                await self.send(session_id, {
                                    'type': 'audio',
                                    'data': {
                                        'audio': audio_base64,
                                        'mimeType': 'audio/pcm;rate=24000'
                                    },
                                    'sessionId': session_id
                                })
        
        # Extract transcriptions
        if hasattr(message, 'server_content') and message.server_content:
            server_content = message.server_content
            
            # Input transcription
            if hasattr(server_content, 'input_transcription') and server_content.input_transcription:
                input_transcript = server_content.input_transcription
                if hasattr(input_transcript, 'text'):
                    transcription = TranscriptionData(
                        text=input_transcript.text,
                        is_user=True,
                        is_final=False
                    )
                    await self.send(session_id, {
                        'type': 'transcription',
                        'data': {
                            'text': transcription.text,
                            'isUser': transcription.is_user,
                            'isFinal': transcription.is_final
                        },
                        'sessionId': session_id
                    })
            
            # Output transcription
            if hasattr(server_content, 'output_transcription') and server_content.output_transcription:
                output_transcript = server_content.output_transcription
                if hasattr(output_transcript, 'text'):
                    transcription = TranscriptionData(
                        text=output_transcript.text,
                        is_user=False,
                        is_final=False
                    )
                    await self.send(session_id, {
                        'type': 'transcription',
                        'data': {
                            'text': transcription.text,
                            'isUser': transcription.is_user,
                            'isFinal': transcription.is_final
                        },
                        'sessionId': session_id
                    })
            
            # Handle turn complete
            if hasattr(server_content, 'turn_complete') and server_content.turn_complete:
                await self.send(session_id, {
                    'type': 'transcription',
                    'data': {'text': '', 'isUser': True, 'isFinal': True},
                    'sessionId': session_id
                })
                await self.send(session_id, {
                    'type': 'transcription',
                    'data': {'text': '', 'isUser': False, 'isFinal': True},
                    'sessionId': session_id
                })
        
        # Handle interruptions
        if hasattr(message, 'server_content') and message.server_content:
            if hasattr(message.server_content, 'interrupted') and message.server_content.interrupted:
                await self.send(session_id, {
                    'type': 'audio',
                    'data': {'interrupt': True},
                    'sessionId': session_id
                })
    
    async def send(self, session_id: str, message: Dict[str, Any]):
        """Send message to client"""
        client = self.clients.get(session_id)
        if client:
            try:
                await client.send_json(message)
            except Exception as e:
                print(f"[WS] Error sending message to {session_id}: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all clients"""
        for session_id, client in self.clients.items():
            try:
                await client.send_json({**message, 'sessionId': session_id})
            except Exception as e:
                print(f"[WS] Error broadcasting to {session_id}: {e}")

