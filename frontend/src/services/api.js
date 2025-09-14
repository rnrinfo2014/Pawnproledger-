import axios from 'axios';

// Base API URL - Update this to match your backend
const BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API endpoints
export const authAPI = {
  login: async (credentials) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },
};

// Company API endpoints
export const companyAPI = {
  getAll: async () => {
    const response = await api.get('/companies');
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/companies/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/companies', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/companies/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/companies/${id}`);
    return response.data;
  },
  
  uploadLogo: async (companyId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/upload/company-logo/${companyId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Customer API endpoints
export const customerAPI = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get(`/customers?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/customers/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/customers', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/customers/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/customers/${id}`);
    return response.data;
  },
};

// Pledge API endpoints
export const pledgeAPI = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get(`/pledges?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/pledges/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/pledges/', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/pledges/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/pledges/${id}`);
    return response.data;
  },
  
  getPledgeItems: async (pledgeId) => {
    const response = await api.get(`/pledges/${pledgeId}/items`);
    return response.data;
  },
};

// Item API endpoints
export const itemAPI = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get(`/items?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/items/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/items', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/items/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/items/${id}`);
    return response.data;
  },
  
  uploadPhotos: async (itemId, files) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    const response = await api.post(`/items/${itemId}/photos`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Scheme API endpoints
export const schemeAPI = {
  getAll: async () => {
    const response = await api.get('/schemes');
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/schemes/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/schemes', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/schemes/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/schemes/${id}`);
    return response.data;
  },
};

// Gold Silver Rate API endpoints
export const rateAPI = {
  getAll: async () => {
    const response = await api.get('/gold-silver-rates');
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/gold-silver-rates', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/gold-silver-rates/${id}`, data);
    return response.data;
  },
};

// Area API endpoints
export const areaAPI = {
  getAll: async () => {
    const response = await api.get('/areas');
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/areas', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/areas/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/areas/${id}`);
    return response.data;
  },
};

export default api;
