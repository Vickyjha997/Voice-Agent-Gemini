"""Gemini Live API Proxy Service"""
import sys
import os
import asyncio
import urllib.parse  # Workaround for google-genai library bug: ensure urllib is imported before library uses it
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Callable, Optional, Any, Dict, Awaitable
try:
    # Monkey-patch fix for google-genai library bug: urllib is not imported in _api_client.py
    # Import the module first, then inject urllib into its namespace
    import google.genai._api_client as api_client_module
    if not hasattr(api_client_module, 'urllib'):
        import urllib
        api_client_module.urllib = urllib
    
    from google.genai import Client, types
except ImportError:
    # Fallback if google.genai is not available
    Client = None
    types = None
except Exception as e:
    # Log but don't fail if monkey-patch fails
    print(f"[Warning] Could not apply urllib monkey-patch: {e}")
    try:
        from google.genai import Client, types
    except ImportError:
        Client = None
        types = None
from models import Session
from services.session_manager import session_manager
from tools.tool_registry import tool_registry


class GeminiProxy:
    """Handles connection to Gemini Live API and manages function calling"""
    
    MODEL_NAME = 'gemini-2.5-flash-native-audio-preview-12-2025'
    
    def __init__(self, api_key: str):
        """Initialize Gemini client"""
        # #region agent log
        import json
        log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"gemini_proxy.py:20","message":"Initializing GeminiProxy","data":{"has_api_key":bool(api_key),"api_key_length":len(api_key) if api_key else 0},"sessionId":"debug-session","runId":"run1","hypothesisId":"D","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        try:
            if not Client:
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:28","message":"Client is None - google.genai not imported","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"D","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                raise ImportError("google.genai package is not installed. Install it with: pip install google-genai")
            self.client = Client(api_key=api_key)
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:35","message":"GeminiProxy client created successfully","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"D","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
        except Exception as e:
            # #region agent log
            try:
                import traceback
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:40","message":"GeminiProxy initialization error","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"D","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            raise
    
    async def connect_session(
        self,
        session_id: str,
        on_message: Callable[[Dict[str, Any]], Awaitable[None]],
        on_error: Callable[[Exception], Awaitable[None]]
    ) -> Any:
        """Connect to Gemini Live API for a session"""
        session = session_manager.get_session(session_id)
        if not session:
            raise ValueError('Session not found')
        
        # Get available tools for function calling
        tools = tool_registry.get_gemini_tools_format()
        
        # Format per Live API documentation: [{"function_declarations": [...]}]
        tools_to_use = None
        if tools:
            tools_to_use = [{
                'function_declarations': [
                    {
                        'name': tool['name'],
                        'description': tool['description'],
                        'parameters': tool['parameters']
                    }
                    for tool in tools
                ]
            }]
        
        try:
            # Connect to Gemini Live API per official documentation
            if not self.client:
                raise ImportError("google.genai package is not installed. Install it with: pip install google-genai")
            
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:95","message":"Connecting to Gemini Live API","data":{"model":self.MODEL_NAME,"has_tools":bool(tools_to_use)},"sessionId":"debug-session","runId":"run1","hypothesisId":"H","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            config = {
                'response_modalities': ['AUDIO'],
                'input_audio_transcription': {},
                'output_audio_transcription': {},
                'system_instruction': (
                    "You are a helpful AI voice assistant with access to various tools and APIs.\n\n"
                    "LANGUAGE POLICY:\n"
                    "- You MUST initially speak ONLY in English.\n"
                    "- Do NOT switch to other languages (like Hindi, Spanish, etc.) unless the user explicitly asks you to speak in that language.\n"
                    "- If a user speaks to you in another language, respond in English and ask if they would like you to switch to their language.\n"
                    "- Only switch languages when the user explicitly requests it (e.g., 'speak in Hindi', 'talk in Spanish', etc.).\n\n"
                    "IMPORTANT: You have access to function calling tools. When a user asks about:\n"
                    "- Weather information → Use the get_weather function\n"
                    "- Analytics or data queries → Use get_analytics or execute_sql_query functions\n"
                    "- Searching for information → Use search_knowledge_base function\n"
                    "- External API calls → Use call_external_api function\n\n"
                    "You MUST use function calls when users request data, information retrieval, or external service interactions. "
                    "Do not just respond without calling functions when they are needed.\n\n"
                    "Always explain what you're doing when calling functions."
                )
            }
            
            if tools_to_use:
                config['tools'] = tools_to_use
            
            # Connect returns an async context manager, need to enter it manually
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:120","message":"Getting context manager from connect","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            # Get the context manager
            context_manager = self.client.aio.live.connect(
                model=self.MODEL_NAME,
                config=config
            )
            
            # Enter the context manager to get the actual session
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:132","message":"Entering context manager","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            gemini_session = await context_manager.__aenter__()
            
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:140","message":"Context manager entered, session obtained","data":{"has_session":bool(gemini_session)},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            # Store the context manager so we can exit it later
            session_manager.update_session(session_id, {'gemini_context_manager': context_manager})
            
            # Start background task to receive messages using receive() pattern
            asyncio.create_task(self._receive_messages(gemini_session, session_id, on_message, on_error))
            
            # Store gemini session
            session_manager.update_session(session_id, {'gemini_session': gemini_session})
            
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:145","message":"Gemini session connected and stored","data":{"session_id":session_id},"sessionId":"debug-session","runId":"run1","hypothesisId":"H","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            return gemini_session
            
        except Exception as e:
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                import traceback
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:155","message":"connect_session error","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"H","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            raise
    
    async def _receive_messages(
        self,
        session: Any,
        session_id: str,
        on_message: Callable[[Dict[str, Any]], Awaitable[None]],
        on_error: Callable[[Exception], Awaitable[None]]
    ):
        """Receive messages using async iterator pattern"""
        # #region agent log
        try:
            import json
            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"gemini_proxy.py:195","message":"Starting message receiver","data":{"session_id":session_id,"has_receive":hasattr(session, 'receive')},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        try:
            if hasattr(session, 'receive'):
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:203","message":"Starting receive() iterator","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                
                async for response in session.receive():
                    # #region agent log
                    try:
                        import json
                        log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                        # Get all attributes of response
                        response_attrs = [attr for attr in dir(response) if not attr.startswith('_')]
                        response_data = None
                        response_data_type = None
                        if hasattr(response, 'data'):
                            response_data = response.data
                            response_data_type = type(response.data).__name__
                            if isinstance(response.data, bytes):
                                response_data = f"<bytes: {len(response.data)}>"
                        server_content_data = None
                        if hasattr(response, 'server_content') and response.server_content:
                            sc = response.server_content
                            server_content_data = {
                                "has_model_turn": hasattr(sc, 'model_turn') and sc.model_turn is not None,
                                "has_parts": hasattr(sc, 'model_turn') and hasattr(sc.model_turn, 'parts') if sc.model_turn else False
                            }
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({"location":"gemini_proxy.py:236","message":"Received message from Gemini","data":{"response_attrs":response_attrs[:20],"has_data":hasattr(response, 'data'),"data_type":response_data_type,"data_len":len(response.data) if hasattr(response, 'data') and isinstance(response.data, bytes) else None,"has_server_content":hasattr(response, 'server_content'),"server_content":server_content_data,"has_tool_call":hasattr(response, 'tool_call')},"sessionId":"debug-session","runId":"run1","hypothesisId":"L","timestamp":int(__import__('time').time()*1000)}) + '\n')
                    except Exception as log_err:
                        try:
                            import json
                            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                            with open(log_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({"location":"gemini_proxy.py:236","message":"Error logging response","data":{"error":str(log_err)},"sessionId":"debug-session","runId":"run1","hypothesisId":"L","timestamp":int(__import__('time').time()*1000)}) + '\n')
                        except: pass
                    # #endregion
                    
                    # Handle function calls before passing message to client
                    await self._handle_function_calls(response, session_id)
                    # Pass the message to client
                    await on_message(response)
            else:
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:220","message":"Session does not have receive() method","data":{"session_type":type(session).__name__},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                print(f"[Gemini] Session {session_id} does not support receive() method")
        except Exception as e:
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                import traceback
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:227","message":"Error in receive loop","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            await on_error(e)
    
    async def _handle_message(
        self,
        message: Any,
        session_id: str,
        on_message: Callable[[Dict[str, Any]], Awaitable[None]]
    ):
        """Handle messages from Gemini, including function calls"""
        # Handle function calls before passing message to client
        await self._handle_function_calls(message, session_id)
        
        # Pass the message to client
        await on_message(message)
    
    async def _handle_function_calls(
        self,
        message: Any,
        session_id: str
    ):
        """Handle function calls from Gemini"""
        # Check for toolCall at top level (per Live API documentation)
        if not hasattr(message, 'tool_call') or not message.tool_call:
            return
        
        tool_call = message.tool_call
        if not hasattr(tool_call, 'function_calls') or not tool_call.function_calls:
            return
        
        session = session_manager.get_session(session_id)
        if not session or not session.gemini_session:
            return
        
        function_calls = tool_call.function_calls
        function_responses = []
        
        # Process each function call
        for fc in function_calls:
            tool_name = getattr(fc, 'name', '') or ''
            args = getattr(fc, 'args', {}) or {}
            call_id = getattr(fc, 'id', '') or (tool_name + '_' + str(int(__import__('time').time() * 1000)))
            
            if not tool_name:
                continue
            
            print(f"[Function Call] {tool_name}", args)
            
            # Execute the function
            result = await tool_registry.execute(tool_name, args)
            
            # Build function response per Live API documentation using types.FunctionResponse
            if types:
                function_response = types.FunctionResponse(
                    id=call_id,
                    name=tool_name,
                    response={'error': result.error} if result.error else result.result
                )
            else:
                # Fallback if types not available
                function_response = {
                    'id': call_id,
                    'name': tool_name,
                    'response': {'error': result.error} if result.error else result.result
                }
            function_responses.append(function_response)
        
        # Send function results back to Gemini using send_tool_response
        try:
            if hasattr(session.gemini_session, 'send_tool_response'):
                await session.gemini_session.send_tool_response(function_responses=function_responses)
            elif hasattr(session.gemini_session, 'sendToolResponse'):
                await session.gemini_session.sendToolResponse({'functionResponses': function_responses})
            else:
                print("[Function Call] send_tool_response method not available on session")
        except Exception as e:
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                import traceback
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:203","message":"Function response send error","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"H","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            print(f"[Function Call] Error sending function responses: {e}")
    
    async def send_audio(self, session_id: str, audio_blob: Dict[str, Any]) -> None:
        """Send audio data to Gemini"""
        session = session_manager.get_session(session_id)
        if not session or not session.gemini_session:
            raise ValueError('Session not found or not connected')
        
        # #region agent log
        try:
            import json
            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
            # Get all methods/attributes of the session object
            session_attrs = [attr for attr in dir(session.gemini_session) if not attr.startswith('_')]
            # Check specifically for send_realtime_input
            has_send_realtime_input = hasattr(session.gemini_session, 'send_realtime_input')
            has_send = hasattr(session.gemini_session, 'send')
            # Get method signatures if possible
            send_sig = None
            send_realtime_sig = None
            try:
                import inspect
                if has_send:
                    send_sig = str(inspect.signature(session.gemini_session.send))
                if has_send_realtime_input:
                    send_realtime_sig = str(inspect.signature(session.gemini_session.send_realtime_input))
            except:
                pass
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"gemini_proxy.py:350","message":"Sending audio","data":{"session_id":session_id,"has_audio_data":bool(audio_blob.get('data')),"session_type":type(session.gemini_session).__name__,"session_attrs":session_attrs[:20],"has_send_realtime_input":has_send_realtime_input,"has_send":has_send,"send_sig":send_sig,"send_realtime_sig":send_realtime_sig},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        try:
            # The session is an AsyncSession with a 'send' method
            # Per Python SDK: use send() with types.Blob for audio
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                has_send = hasattr(session.gemini_session, 'send')
                send_callable = callable(getattr(session.gemini_session, 'send', None))
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:375","message":"Checking send method","data":{"has_send":has_send,"send_callable":send_callable,"has_types":types is not None},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            # Check for send_realtime_input method first (preferred for audio)
            # Based on official example: await session.send_realtime_input(audio={"data": bytes, "mime_type": "audio/pcm"})
            if hasattr(session.gemini_session, 'send_realtime_input'):
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:387","message":"Using send_realtime_input method","data":{"has_types":types is not None},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                
                # Convert audio_blob dict to the format expected by send_realtime_input
                # Signature shows: audio: Union[google.genai.types.Blob, google.genai.types.BlobDict]
                # Try using types.Blob first (preferred), fallback to dict format
                import base64
                audio_data = audio_blob.get('data', '')
                # Simplify mime_type to match user's example: "audio/pcm" not "audio/pcm;rate=16000"
                raw_mime_type = audio_blob.get('mimeType', 'audio/pcm')
                mime_type = 'audio/pcm' if raw_mime_type.startswith('audio/pcm') else raw_mime_type
                
                # Decode base64 if it's a string, otherwise use as-is
                if isinstance(audio_data, str):
                    audio_bytes = base64.b64decode(audio_data)
                else:
                    audio_bytes = audio_data
                
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    has_blob = types and hasattr(types, 'Blob')
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:413","message":"Preparing audio for send_realtime_input","data":{"has_types":types is not None,"has_blob":has_blob,"mime_type":mime_type,"audio_bytes_len":len(audio_bytes)},"sessionId":"debug-session","runId":"run1","hypothesisId":"K","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                
                # Try using types.Blob if available (signature expects Blob or BlobDict)
                if types and hasattr(types, 'Blob'):
                    try:
                        audio_blob_obj = types.Blob(data=audio_bytes, mime_type=mime_type)
                        # #region agent log
                        try:
                            import json
                            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                            with open(log_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({"location":"gemini_proxy.py:425","message":"Calling send_realtime_input with types.Blob","data":{"mime_type":mime_type,"audio_bytes_len":len(audio_bytes)},"sessionId":"debug-session","runId":"run1","hypothesisId":"K","timestamp":int(__import__('time').time()*1000)}) + '\n')
                        except: pass
                        # #endregion
                        await session.gemini_session.send_realtime_input(audio=audio_blob_obj)
                    except Exception as blob_error:
                        # #region agent log
                        try:
                            import json
                            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                            with open(log_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({"location":"gemini_proxy.py:432","message":"types.Blob failed, trying dict format","data":{"error":str(blob_error),"error_type":type(blob_error).__name__},"sessionId":"debug-session","runId":"run1","hypothesisId":"K","timestamp":int(__import__('time').time()*1000)}) + '\n')
                        except: pass
                        # #endregion
                        # Fallback to dict format (as shown in user's example)
                        audio_msg = {"data": audio_bytes, "mime_type": mime_type}
                        # #region agent log
                        try:
                            import json
                            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                            with open(log_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({"location":"gemini_proxy.py:440","message":"Calling send_realtime_input with audio dict (fallback)","data":{"mime_type":mime_type,"audio_bytes_len":len(audio_bytes)},"sessionId":"debug-session","runId":"run1","hypothesisId":"K","timestamp":int(__import__('time').time()*1000)}) + '\n')
                        except: pass
                        # #endregion
                        await session.gemini_session.send_realtime_input(audio=audio_msg)
                else:
                    # No types.Blob available, use dict format
                    audio_msg = {"data": audio_bytes, "mime_type": mime_type}
                    # #region agent log
                    try:
                        import json
                        log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({"location":"gemini_proxy.py:450","message":"Calling send_realtime_input with audio dict (no types.Blob)","data":{"mime_type":mime_type,"audio_bytes_len":len(audio_bytes)},"sessionId":"debug-session","runId":"run1","hypothesisId":"K","timestamp":int(__import__('time').time()*1000)}) + '\n')
                    except: pass
                    # #endregion
                    await session.gemini_session.send_realtime_input(audio=audio_msg)
            elif hasattr(session.gemini_session, 'send'):
                # Fallback to send() method if send_realtime_input doesn't exist
                # #region agent log
                try:
                    import json
                    import inspect
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    send_sig = None
                    try:
                        send_sig = str(inspect.signature(session.gemini_session.send))
                    except:
                        pass
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:447","message":"Using send method (fallback)","data":{"has_types":types is not None,"send_signature":send_sig},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                
                # Convert audio_blob dict to proper input format
                # Based on signature, send() accepts input as positional arg with types like LiveClientRealtimeInput
                if types:
                    import base64
                    audio_data = audio_blob.get('data', '')
                    mime_type = audio_blob.get('mimeType', 'audio/pcm;rate=16000')
                    
                    if isinstance(audio_data, str):
                        audio_bytes = base64.b64decode(audio_data)
                    else:
                        audio_bytes = audio_data
                    
                    audio_blob_obj = types.Blob(data=audio_bytes, mime_type=mime_type)
                    
                    # Try different approaches based on send() signature
                    # The signature shows it accepts Part, Content, LiveClientContent, etc.
                    # Based on documentation, audio should be sent as Part with inline_data
                    # #region agent log
                    try:
                        import json
                        log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({"location":"gemini_proxy.py:478","message":"Trying to send audio","data":{"mime_type":mime_type,"audio_bytes_len":len(audio_bytes),"has_Part":hasattr(types, 'Part'),"has_InlineData":hasattr(types, 'InlineData')},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                    except: pass
                    # #endregion
                    
                    # Option 1: Try Part with inline_data (most likely based on API structure)
                    try:
                        if hasattr(types, 'Part') and hasattr(types, 'InlineData'):
                            # Create InlineData with the Blob
                            inline_data = types.InlineData(data=audio_bytes, mime_type=mime_type)
                            # Create Part with inline_data
                            part = types.Part(inline_data=inline_data)
                            # #region agent log
                            try:
                                import json
                                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                                with open(log_path, 'a', encoding='utf-8') as f:
                                    f.write(json.dumps({"location":"gemini_proxy.py:490","message":"Trying send with Part(inline_data=InlineData)","data":{"mime_type":mime_type},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                            except: pass
                            # #endregion
                            await session.gemini_session.send(part)
                        else:
                            raise ValueError("Part or InlineData types not available")
                    except Exception as e1:
                        # Option 2: Try Part with inline_data using dict format
                        try:
                            part_dict = {'inline_data': {'data': audio_bytes, 'mime_type': mime_type}}
                            # #region agent log
                            try:
                                import json
                                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                                with open(log_path, 'a', encoding='utf-8') as f:
                                    f.write(json.dumps({"location":"gemini_proxy.py:500","message":"Trying send with Part dict format","data":{"error1":str(e1)[:100]},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                            except: pass
                            # #endregion
                            await session.gemini_session.send(part_dict)
                        except Exception as e2:
                            # Option 3: Try Content with parts containing Part
                            try:
                                if hasattr(types, 'Content'):
                                    if hasattr(types, 'Part') and hasattr(types, 'InlineData'):
                                        inline_data = types.InlineData(data=audio_bytes, mime_type=mime_type)
                                        part = types.Part(inline_data=inline_data)
                                        content = types.Content(parts=[part])
                                    else:
                                        # Use dict format
                                        part_dict = {'inline_data': {'data': audio_bytes, 'mime_type': mime_type}}
                                        content = types.Content(parts=[part_dict])
                                    # #region agent log
                                    try:
                                        import json
                                        log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                                        with open(log_path, 'a', encoding='utf-8') as f:
                                            f.write(json.dumps({"location":"gemini_proxy.py:515","message":"Trying send with Content(parts=[Part])","data":{"error2":str(e2)[:100]},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                                    except: pass
                                    # #endregion
                                    await session.gemini_session.send(content)
                                else:
                                    raise e2
                            except Exception as e3:
                                # Log all attempts and re-raise
                                # #region agent log
                                try:
                                    import json
                                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                                    with open(log_path, 'a', encoding='utf-8') as f:
                                        f.write(json.dumps({"location":"gemini_proxy.py:525","message":"All send attempts failed","data":{"error1":str(e1)[:100],"error2":str(e2)[:100],"error3":str(e3)[:100]},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                                except: pass
                                # #endregion
                                raise e3
                else:
                    # #region agent log
                    try:
                        import json
                        log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({"location":"gemini_proxy.py:478","message":"Trying send with dict (no types)","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                    except: pass
                    # #endregion
                    await session.gemini_session.send({'audio': audio_blob})
                
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:395","message":"Audio sent via send method","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
            # Fallback methods (for different SDK versions)
            elif hasattr(session.gemini_session, 'send_realtime_input'):
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:402","message":"Using send_realtime_input method","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                if types:
                    import base64
                    audio_data = audio_blob.get('data', '')
                    mime_type = audio_blob.get('mimeType', 'audio/pcm;rate=16000')
                    if isinstance(audio_data, str):
                        audio_bytes = base64.b64decode(audio_data)
                    else:
                        audio_bytes = audio_data
                    audio_blob_obj = types.Blob(data=audio_bytes, mime_type=mime_type)
                    await session.gemini_session.send_realtime_input(audio=audio_blob_obj)
                else:
                    await session.gemini_session.send_realtime_input(media=audio_blob)
            elif hasattr(session.gemini_session, 'send_client_content'):
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:420","message":"Using send_client_content method","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                await session.gemini_session.send_client_content(
                    turns={"parts": [{"inline_data": audio_blob}]}
                )
            else:
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    session_attrs = [attr for attr in dir(session.gemini_session) if not attr.startswith('_')]
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:430","message":"No audio send method found","data":{"session_attrs":session_attrs},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                raise ValueError('Session does not support sending audio input')
        except Exception as e:
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                import traceback
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"gemini_proxy.py:405","message":"Audio send error","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"J","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            raise
    
    async def disconnect_session(self, session_id: str) -> None:
        """Disconnect a Gemini session"""
        session = session_manager.get_session(session_id)
        if not session:
            return
        
        # #region agent log
        try:
            import json
            log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"gemini_proxy.py:250","message":"Disconnecting session","data":{"session_id":session_id,"has_gemini_session":bool(session.gemini_session)},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        # Exit the context manager if it exists
        if hasattr(session, 'gemini_context_manager') and session.gemini_context_manager:
            try:
                await session.gemini_context_manager.__aexit__(None, None, None)
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:260","message":"Context manager exited","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
            except Exception as e:
                # #region agent log
                try:
                    import json
                    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                    import traceback
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"gemini_proxy.py:267","message":"Error exiting context manager","data":{"error":str(e)},"sessionId":"debug-session","runId":"run1","hypothesisId":"I","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                pass
        
        # Also try close method if available
        if session.gemini_session and hasattr(session.gemini_session, 'close'):
            try:
                await session.gemini_session.close()
            except:
                pass
        
        session_manager.update_session(session_id, {'gemini_session': None, 'gemini_context_manager': None})

