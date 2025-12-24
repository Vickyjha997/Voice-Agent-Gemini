"""Main FastAPI application for Gemini Live Backend"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from dotenv import load_dotenv
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.gemini_proxy import GeminiProxy
from services.websocket_handler import WebSocketHandler
from services.session_manager import session_manager
from tools.tool_registry import tool_registry
import tools.example_tools  # Register example tools

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Gemini Live Backend", version="1.0.0")

# CORS middleware
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://127.0.0.1:5500').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
# #region agent log
import json
log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
try:
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"main.py:38","message":"Initializing services","data":{"has_api_key":bool(os.getenv('GEMINI_API_KEY'))},"sessionId":"debug-session","runId":"run1","hypothesisId":"B","timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

try:
    gemini_proxy = GeminiProxy(os.getenv('GEMINI_API_KEY', ''))
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:46","message":"GeminiProxy created","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"B","timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    ws_handler = WebSocketHandler(gemini_proxy)
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:50","message":"WebSocketHandler created","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"B","timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
except Exception as e:
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:54","message":"Service initialization error","data":{"error":str(e),"error_type":type(e).__name__},"sessionId":"debug-session","runId":"run1","hypothesisId":"B","timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    raise

# REST API Routes (must be defined before static file mount)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/sessions")
async def create_session(request: Request):
    """Create a new session"""
    # #region agent log
    import json
    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:84","message":"create_session called","data":{"content_type":request.headers.get("content-type"),"has_body":hasattr(request, '_body')},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    try:
        # Try to parse JSON body
        body = {}
        content_type = request.headers.get("content-type", "")
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:92","message":"Parsing request body","data":{"content_type":content_type},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        if "application/json" in content_type:
            try:
                # Check if there's actually a body to parse
                body_bytes = await request.body()
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"main.py:99","message":"Request body read","data":{"body_length":len(body_bytes),"body_preview":body_bytes[:100].decode('utf-8', errors='ignore') if body_bytes else "empty"},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                
                if body_bytes:
                    import json as json_lib
                    body = json_lib.loads(body_bytes.decode('utf-8'))
                    # #region agent log
                    try:
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({"location":"main.py:108","message":"JSON body parsed","data":{"body_keys":list(body.keys()) if isinstance(body, dict) else "not_dict"},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
                    except: pass
                    # #endregion
                else:
                    # #region agent log
                    try:
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({"location":"main.py:115","message":"Empty body, using empty dict","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
                    except: pass
                    # #endregion
                    body = {}
            except Exception as e:
                # #region agent log
                try:
                    import traceback
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"main.py:122","message":"JSON parse error","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                # If JSON parsing fails, body remains empty dict
                body = {}
        
        user_id = body.get('userId') or request.headers.get('x-user-id')
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:115","message":"Extracting user_id","data":{"user_id":user_id,"from_body":body.get('userId'),"from_header":request.headers.get('x-user-id')},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:122","message":"Calling session_manager.create_session","data":{"user_id":user_id},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        session = session_manager.create_session(user_id)
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:128","message":"Session created successfully","data":{"session_id":session.id,"user_id":session.user_id},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        return {
            "sessionId": session.id,
            "createdAt": session.created_at.isoformat()
        }
    except Exception as e:
        # #region agent log
        try:
            import traceback
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:138","message":"create_session error","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"F","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session info"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "sessionId": session.id,
        "userId": session.user_id,
        "createdAt": session.created_at.isoformat(),
        "memoryLength": len(session.memory)
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    deleted = session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True}


@app.get("/api/tools")
async def get_tools():
    """Get available tools"""
    tools = tool_registry.get_all()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in tools
        ]
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time audio communication"""
    # Extract session ID from query parameter
    session_id = websocket.query_params.get('sessionId')
    
    if not session_id:
        # Create new session if not provided
        session = session_manager.create_session()
        session_id = session.id
    else:
        # Verify session exists
        session = session_manager.get_session(session_id)
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return
    
    print(f"[WS] New connection: {session_id}")
    await ws_handler.handle_connection(websocket, session_id)


# Serve static files from public directory (must be after all API routes)
public_dir = Path(__file__).parent / 'public'
if public_dir.exists():
    # Serve index.html at root
    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        """Serve index.html"""
        index_file = public_dir / 'index.html'
        if index_file.exists():
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"main.py:165","message":"Serving index.html","data":{"index_file":str(index_file)},"sessionId":"debug-session","runId":"run1","hypothesisId":"E","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            return FileResponse(str(index_file))
        return HTMLResponse(content="<h1>Gemini Live Backend API</h1><p>Frontend not found. <a href='/docs'>API Docs</a></p>")
    
    # Mount static files for assets (app.js, etc.) - this will serve files from public directory
    # We use a catch-all approach but API routes defined above take precedence
    from fastapi.responses import FileResponse as FR
    @app.get("/{file_path:path}")
    async def serve_static(file_path: str):
        """Serve static files like app.js"""
        # Don't serve API routes or WebSocket
        if file_path.startswith("api/") or file_path == "ws" or file_path.startswith("docs") or file_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Not found")
        
        file_full_path = public_dir / file_path
        if file_full_path.exists() and file_full_path.is_file():
            # #region agent log
            try:
                import json
                log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"main.py:182","message":"Serving static file","data":{"file_path":file_path,"exists":file_full_path.exists()},"sessionId":"debug-session","runId":"run1","hypothesisId":"E","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            return FR(str(file_full_path))
        raise HTTPException(status_code=404, detail="File not found")
    
    # #region agent log
    try:
        import json
        log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:192","message":"Static file routes configured","data":{"public_dir":str(public_dir),"exists":public_dir.exists()},"sessionId":"debug-session","runId":"run1","hypothesisId":"E","timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
else:
    # #region agent log
    try:
        import json
        log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:200","message":"Public directory not found","data":{"public_dir":str(public_dir)},"sessionId":"debug-session","runId":"run1","hypothesisId":"E","timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    # Fallback if public directory doesn't exist
    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        """Serve API info if no frontend"""
        return HTMLResponse(content="<h1>Gemini Live Backend API</h1><p>Frontend not found. <a href='/docs'>API Docs</a></p>")


if __name__ == "__main__":
    # #region agent log
    import json
    log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:147","message":"Server startup initiated","data":{"timestamp":__import__('time').time()},"sessionId":"debug-session","runId":"run1","hypothesisId":"A","timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    port = int(os.getenv('PORT', 3001))
    ws_port = int(os.getenv('WS_PORT', 3002))
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:155","message":"Port configuration","data":{"port":port,"ws_port":ws_port,"env_port":os.getenv('PORT'),"env_ws_port":os.getenv('WS_PORT')},"sessionId":"debug-session","runId":"run1","hypothesisId":"A","timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    print(f"[HTTP] Server starting on http://localhost:{port}")
    print(f"[HTTP] Health check: http://localhost:{port}/health")
    print(f"[WS] WebSocket server will be available at ws://localhost:{port}/ws")
    print(f"[WS] Connect with: ws://localhost:{port}/ws?sessionId=<your-session-id>")
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"main.py:164","message":"About to start uvicorn","data":{"host":"0.0.0.0","port":port},"sessionId":"debug-session","runId":"run1","hypothesisId":"A","timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    try:
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:172","message":"Calling uvicorn.run","data":{"app":"main:app","host":"0.0.0.0","port":port},"sessionId":"debug-session","runId":"run1","hypothesisId":"C","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:185","message":"Server stopped by user","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"C","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        print("\n[Server] Shutting down...")
    except Exception as e:
        # #region agent log
        try:
            import traceback
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"main.py:192","message":"Uvicorn startup error","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"C","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        print(f"[ERROR] Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        raise

