"""Session Manager - Handles user sessions and memory"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict
from threading import Timer
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Session


class SessionManager:
    """Manages user sessions and memory"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.SESSION_TIMEOUT = timedelta(minutes=30)
        self._start_cleanup_timer()
    
    def create_session(self, user_id: Optional[str] = None) -> Session:
        """Create a new session"""
        # #region agent log
        import json
        import sys
        import os
        log_path = r"c:\Users\VICKY\Downloads\gemini-live-voice-chat (1)\.cursor\debug.log"
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"session_manager.py:20","message":"create_session called","data":{"user_id":user_id},"sessionId":"debug-session","runId":"run1","hypothesisId":"G","timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        try:
            session_id = str(uuid.uuid4())
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"session_manager.py:28","message":"UUID generated","data":{"session_id":session_id},"sessionId":"debug-session","runId":"run1","hypothesisId":"G","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            created_at = datetime.now()
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"session_manager.py:34","message":"Creating Session object","data":{"created_at":created_at.isoformat()},"sessionId":"debug-session","runId":"run1","hypothesisId":"G","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            session = Session(
                id=session_id,
                user_id=user_id,
                created_at=created_at,
                gemini_session=None,
                memory=[]
            )
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"session_manager.py:47","message":"Session object created","data":{"session_id":session.id,"has_created_at":hasattr(session, 'created_at')},"sessionId":"debug-session","runId":"run1","hypothesisId":"G","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            self.sessions[session.id] = session
            
            # Auto-cleanup after timeout
            timer = Timer(self.SESSION_TIMEOUT.total_seconds(), self.delete_session, args=[session.id])
            timer.daemon = True
            timer.start()
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"session_manager.py:58","message":"Session stored and timer started","data":{"session_id":session.id},"sessionId":"debug-session","runId":"run1","hypothesisId":"G","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            return session
        except Exception as e:
            # #region agent log
            try:
                import traceback
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"session_manager.py:65","message":"create_session error","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"G","timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            raise
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict) -> bool:
        """Update a session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        for key, value in updates.items():
            setattr(session, key, value)
        
        return True
    
    def add_to_memory(self, session_id: str, role: str, content: str):
        """Add a message to session memory"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        session.memory.append({'role': role, 'content': content})
        
        # Keep only last 50 messages in memory
        if len(session.memory) > 50:
            session.memory = session.memory[-50:]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.now()
        expired_ids = []
        
        for session_id, session in self.sessions.items():
            age = now - session.created_at
            if age > self.SESSION_TIMEOUT:
                expired_ids.append(session_id)
        
        for session_id in expired_ids:
            self.delete_session(session_id)
    
    def _start_cleanup_timer(self):
        """Start the periodic cleanup timer"""
        def cleanup():
            self.cleanup_expired_sessions()
            self._start_cleanup_timer()  # Reschedule
        
        timer = Timer(5 * 60, cleanup)  # Every 5 minutes
        timer.daemon = True
        timer.start()
    
    def get_all_sessions(self) -> list:
        """Get all sessions"""
        return list(self.sessions.values())


# Global instance
session_manager = SessionManager()

