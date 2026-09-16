const TOKEN_KEY = 'satquery_auth_token';

export const auth = {
  setToken: (token) => {
    localStorage.setItem(TOKEN_KEY, token);
  },
  
  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },
  
  removeToken: () => {
    localStorage.removeItem(TOKEN_KEY);
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem(TOKEN_KEY);
  },
  
  getAuthHeader: () => {
    const token = auth.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
};
