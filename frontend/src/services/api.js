import { auth } from '../utils/auth';

export const authFetch = async (url, options = {}) => {
  const headers = {
    ...options.headers,
    ...auth.getAuthHeader()
  };
  const response = await fetch(url, { ...options, headers });
  
  if (response.status === 401) {
    auth.removeToken();
    window.location.href = '/'; // or window.location.reload() since App.jsx likely redirects to login if no token
  }
  
  return response;
};

export const api = {
  signup: async (userData) => {
    const response = await fetch('http://127.0.0.1:8000/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    
    if (!response.ok) {
        let errorMsg = 'Signup failed';
        try {
            const errData = await response.json();
            if (errData.detail) errorMsg = errData.detail;
        } catch(e) {}
        throw new Error(errorMsg);
    }
    return response.json();
  },

  login: async (credentials) => {
    const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    
    if (!response.ok) {
        let errorMsg = 'Login failed';
        try {
            const errData = await response.json();
            if (errData.detail) errorMsg = errData.detail;
        } catch(e) {}
        throw new Error(errorMsg);
    }
    return response.json();
  },

  uploadImage: async (file, conversationId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }
    
    const response = await authFetch('http://127.0.0.1:8000/api/upload', {
      method: 'POST',
      body: formData,
      // The browser will automatically set the correct Content-Type header with the multipart boundary
    });
    
    if (!response.ok) {
        let errorMsg = 'Upload failed';
        try {
            const errData = await response.json();
            if (errData.detail) {
                errorMsg = errData.detail;
            }
        } catch(e) {}
        throw new Error(errorMsg);
    }
    
    return response.json();
  },

  submitQuery: async (data) => {
    const response = await authFetch('http://127.0.0.1:8000/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
        let errorMsg = 'Query failed';
        try {
            const errData = await response.json();
            if (errData.detail) {
                errorMsg = errData.detail;
            }
        } catch(e) {}
        throw new Error(errorMsg);
    }

    return response.json();
  },

  createConversation: async (context = null) => {
    const payload = context ? { context } : {};
    const response = await authFetch('http://127.0.0.1:8000/api/conversations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('Failed to create conversation');
    return response.json();
  },

  getConversations: async () => {
    const response = await authFetch('http://127.0.0.1:8000/api/conversations');
    if (!response.ok) throw new Error('Failed to fetch conversations');
    return response.json();
  },

  getConversation: async (conversationId) => {
    const response = await authFetch(`http://127.0.0.1:8000/api/conversations/${conversationId}`);
    if (!response.ok) throw new Error('Failed to fetch conversation');
    return response.json();
  },

  getSatelliteImagery: async ({ latitude, longitude, target_date, start_date, end_date }) => {
    const params = new URLSearchParams({ latitude, longitude });
    if (target_date) params.append('target_date', target_date);
    if (start_date) params.append('start_date', start_date);
    if (end_date) params.append('end_date', end_date);

    const response = await authFetch(`http://127.0.0.1:8000/api/satellite/imagery?${params.toString()}`);
    if (!response.ok) {
        let errorMsg = 'Failed to fetch satellite imagery';
        try {
            const errData = await response.json();
            if (errData.detail) errorMsg = errData.detail;
        } catch(e) {}
        throw new Error(errorMsg);
    }
    return response.json();
  },

  getHistoricalImagery: async ({ latitude, longitude }) => {
    const params = new URLSearchParams({ latitude, longitude });
    const response = await authFetch(`http://127.0.0.1:8000/api/satellite/history?${params.toString()}`);
    if (!response.ok) {
        let errorMsg = 'Failed to fetch historical imagery';
        try {
            const errData = await response.json();
            if (errData.detail) errorMsg = errData.detail;
        } catch(e) {}
        throw new Error(errorMsg);
    }
    return response.json();
  },

  getSatelliteChangeDetection: async (beforeAssetUrl, afterAssetUrl) => {
    const response = await authFetch("http://127.0.0.1:8000/api/satellite/change-detection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            before_asset_url: beforeAssetUrl,
            after_asset_url: afterAssetUrl
        })
    });
    
    if (!response.ok) {
        let errorMsg = 'Failed to fetch change detection result';
        try {
            const errData = await response.json();
            if (errData.detail) errorMsg = errData.detail;
        } catch(e) {}
        throw new Error(errorMsg);
    }
    return response.json();
  },

  getLandCoverAnalysis: async (beforeAssetUrl, afterAssetUrl) => {
    const response = await authFetch("http://127.0.0.1:8000/api/satellite/land-cover-analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            before_asset_url: beforeAssetUrl,
            after_asset_url: afterAssetUrl
        })
    });
    
    if (!response.ok) {
        let errorMsg = 'Failed to fetch land cover analysis result';
        try {
            const errData = await response.json();
            if (errData.detail) errorMsg = errData.detail;
        } catch(e) {}
        throw new Error(errorMsg);
    }
    return response.json();
  },

  getSatelliteSummary: async (latitude, longitude) => {
    const response = await authFetch("http://127.0.0.1:8000/api/satellite/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latitude, longitude })
    });
    
    if (!response.ok) {
        let errorMsg = 'Failed to fetch satellite summary';
        try {
            const errData = await response.json();
            if (errData.detail) errorMsg = errData.detail;
        } catch(e) {}
        throw new Error(errorMsg);
    }
    return response.json();
  },

  getRealEstateAnalysis: async (latitude, longitude) => {
    const response = await authFetch("http://127.0.0.1:8000/api/satellite/real-estate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latitude, longitude })
    });
    
    if (!response.ok) {
        let errorMsg = 'Failed to fetch real-estate analysis';
        try {
            const errData = await response.json();
            if (errData.detail) errorMsg = errData.detail;
        } catch(e) {}
        throw new Error(errorMsg);
    }
    return response.json();
  },

  getSatelliteEvidence: async (latitude, longitude) => {
    const response = await authFetch("http://127.0.0.1:8000/api/satellite/evidence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latitude, longitude })
    });
    
    if (!response.ok) {
        let errorMsg = 'Failed to fetch satellite evidence';
        try {
            const errData = await response.json();
            if (errData.detail) errorMsg = errData.detail;
        } catch(e) {}
        throw new Error(errorMsg);
    }
    return response.json();
  }
};
