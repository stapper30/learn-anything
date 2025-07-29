'use client';

import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState({
    username: '',
    name: '',
    user_id: null
  });

  const clearUser = () => setUser({
    username: '',
    name: '',
    user_id: null
  });

  return (
    <AuthContext.Provider value={{user, setUser, clearUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useToken must be used within a TokenProvider');
  }
  return context;
}
