import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext({});

const API_BASE_URL = 'http://localhost:8001'; // Backend API URL
const WS_URL = 'ws://localhost:8001/ws'; // Backend WebSocket URL

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);
  const [ws, setWs] = useState(null);

  // Helper to attach auth header
  const authHeaders = useCallback(() => ({
    'Content-Type': 'application/json',
    Authorization: token ? `Bearer ${token}` : '',
  }), [token]);

  // Fetch initial data from backend
  const fetchInitialData = useCallback(async () => {
    if (!token) return;
    try {
      const [usersRes, sessionsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/users/`, { headers: authHeaders() }),
        fetch(`${API_BASE_URL}/sessions/`, { headers: authHeaders() }),
      ]);
      if (!usersRes.ok || !sessionsRes.ok) {
        throw new Error('Failed to fetch data');
      }
      const usersData = await usersRes.json();
      const sessionsData = await sessionsRes.json();
      setUsers(usersData);
      setSessions(sessionsData);
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  }, [token, authHeaders]);

  // WebSocket message handler
  const handleWsMessage = useCallback((event) => {
    try {
      const message = JSON.parse(event.data);
      switch (message.type) {
        case 'user_created':
          setUsers(prev => [...prev, message.data.user]);
          break;
        case 'user_updated':
          setUsers(prev => prev.map(u => u.id === message.data.user_id ? message.data.user : u));
          if (user && user.id === message.data.user_id) {
            setUser(message.data.user);
          }
          break;
        case 'user_deleted':
          setUsers(prev => prev.filter(u => u.id !== message.data.user_id));
          if (user && user.id === message.data.user_id) {
            setUser(null);
            setToken(null);
            localStorage.removeItem('token');
            localStorage.removeItem('user');
          }
          break;
        case 'session_created':
          setSessions(prev => [...prev, message.data]);
          break;
        case 'session_updated':
          setSessions(prev => prev.map(s => s.id === message.data.session_id ? { ...s, status: message.data.status, updated_at: message.data.updated_at } : s));
          break;
        case 'session_deleted':
          setSessions(prev => prev.filter(s => s.id !== message.data.session_id));
          break;
        default:
          console.warn('Unknown WebSocket message type:', message.type);
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
    }
  }, [user]);

  // Setup WebSocket connection
  useEffect(() => {
    if (!token) return;

    const socket = new WebSocket(WS_URL);
    socket.onopen = () => {
      console.log('WebSocket connected');
    };
    socket.onmessage = handleWsMessage;
    socket.onclose = () => {
      console.log('WebSocket disconnected');
    };
    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setWs(socket);

    return () => {
      socket.close();
    };
  }, [token, handleWsMessage]);

  // Fetch initial data on token change
  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  // Load user and token from localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
      setToken(storedToken);
    }
    setLoading(false);
  }, []);

  // Login function
  const login = async (username, password) => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        return { success: false, error: errorData.detail || 'Login failed' };
      }
      const data = await res.json();
      setUser(data.user);
      setToken(data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      localStorage.setItem('token', data.access_token);
      return { success: true, forcePasswordChange: data.force_password_change };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login error' };
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    setToken(null);
    setUsers([]);
    setSessions([]);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    if (ws) {
      ws.close();
      setWs(null);
    }
  };

  // Create user via API
  const createUser = async (userData) => {
    if (!token) return null;
    try {
      const res = await fetch(`${API_BASE_URL}/users/`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(userData),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to create user');
      }
      const newUser = await res.json();
      // No need to update users here, WebSocket will handle it
      return newUser;
    } catch (error) {
      console.error('Create user error:', error);
      return null;
    }
  };

  // Update user via API
  const updateUserById = async (id, updates) => {
    if (!token) return null;
    try {
      const res = await fetch(`${API_BASE_URL}/users/${id}`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify(updates),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to update user');
      }
      const updatedUser = await res.json();
      // WebSocket will update state
      return updatedUser;
    } catch (error) {
      console.error('Update user error:', error);
      return null;
    }
  };

  // Delete user via API
  const deleteUser = async (id) => {
    if (!token) return false;
    try {
      const res = await fetch(`${API_BASE_URL}/users/${id}`, {
        method: 'DELETE',
        headers: authHeaders(),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to delete user');
      }
      // WebSocket will update state
      return true;
    } catch (error) {
      console.error('Delete user error:', error);
      return false;
    }
  };

  // Create session via API
  const createSession = async (sessionData) => {
    if (!token) return null;
    try {
      const res = await fetch(`${API_BASE_URL}/sessions/`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(sessionData),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to create session');
      }
      const newSession = await res.json();
      // WebSocket will update state
      return newSession;
    } catch (error) {
      console.error('Create session error:', error);
      return null;
    }
  };

  // Update session via API
  const updateSession = async (id, updates) => {
    if (!token) return null;
    try {
      const res = await fetch(`${API_BASE_URL}/sessions/${id}`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify(updates),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to update session');
      }
      const updatedSession = await res.json();
      // WebSocket will update state
      return updatedSession;
    } catch (error) {
      console.error('Update session error:', error);
      return null;
    }
  };

  // Delete session via API
  const deleteSession = async (id) => {
    if (!token) return false;
    try {
      const res = await fetch(`${API_BASE_URL}/sessions/${id}`, {
        method: 'DELETE',
        headers: authHeaders(),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to delete session');
      }
      // WebSocket will update state
      return true;
    } catch (error) {
      console.error('Delete session error:', error);
      return false;
    }
  };

  // Mark notification as read
  const markNotificationAsRead = (id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const value = {
    user,
    users,
    sessions,
    notifications,
    loading,
    login,
    logout,
    createUser,
    updateUserById,
    deleteUser,
    createSession,
    updateSession,
    deleteSession,
    markNotificationAsRead,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
