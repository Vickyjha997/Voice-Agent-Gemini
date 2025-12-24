import { v4 as uuidv4 } from 'uuid';
import { Session } from '../types';

/**
 * Session Manager - Handles user sessions and memory
 */
class SessionManager {
  private sessions: Map<string, Session> = new Map();
  private readonly SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes

  createSession(userId?: string): Session {
    const session: Session = {
      id: uuidv4(),
      userId,
      createdAt: new Date(),
      geminiSession: null,
      memory: [],
    };

    this.sessions.set(session.id, session);
    
    // Auto-cleanup after timeout
    setTimeout(() => {
      this.deleteSession(session.id);
    }, this.SESSION_TIMEOUT);

    return session;
  }

  getSession(sessionId: string): Session | undefined {
    return this.sessions.get(sessionId);
  }

  updateSession(sessionId: string, updates: Partial<Session>): boolean {
    const session = this.sessions.get(sessionId);
    if (!session) return false;

    this.sessions.set(sessionId, { ...session, ...updates });
    return true;
  }

  addToMemory(sessionId: string, role: 'user' | 'assistant', content: string) {
    const session = this.sessions.get(sessionId);
    if (!session) return;

    session.memory.push({ role, content });
    
    // Keep only last 50 messages in memory
    if (session.memory.length > 50) {
      session.memory = session.memory.slice(-50);
    }
  }

  deleteSession(sessionId: string): boolean {
    return this.sessions.delete(sessionId);
  }

  cleanupExpiredSessions() {
    const now = Date.now();
    for (const [id, session] of this.sessions.entries()) {
      const age = now - session.createdAt.getTime();
      if (age > this.SESSION_TIMEOUT) {
        this.deleteSession(id);
      }
    }
  }

  getAllSessions(): Session[] {
    return Array.from(this.sessions.values());
  }
}

export const sessionManager = new SessionManager();

// Cleanup expired sessions every 5 minutes
setInterval(() => {
  sessionManager.cleanupExpiredSessions();
}, 5 * 60 * 1000);

