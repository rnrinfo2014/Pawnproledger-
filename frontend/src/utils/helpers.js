// Format currency values
export const formatCurrency = (amount, currency = '₹') => {
  if (amount === null || amount === undefined || isNaN(amount)) return `${currency}0.00`;
  
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency === '₹' ? 'INR' : 'USD',
    minimumFractionDigits: 2,
  }).format(amount);
};

// Format date
export const formatDate = (date, format = 'short') => {
  if (!date) return '';
  
  const dateObj = new Date(date);
  
  if (format === 'short') {
    return dateObj.toLocaleDateString('en-IN');
  } else if (format === 'long') {
    return dateObj.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } else if (format === 'datetime') {
    return dateObj.toLocaleString('en-IN');
  }
  
  return dateObj.toLocaleDateString('en-IN');
};

// Format weight
export const formatWeight = (weight, unit = 'g') => {
  if (weight === null || weight === undefined || isNaN(weight)) return '0g';
  return `${Number(weight).toFixed(2)}${unit}`;
};

// Get status color
export const getStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'active':
    case 'pawned':
      return 'success';
    case 'redeemed':
      return 'info';
    case 'auctioned':
      return 'warning';
    case 'inactive':
    case 'cancelled':
      return 'error';
    default:
      return 'default';
  }
};

// Capitalize first letter
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

// Generate random ID
export const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

// Validate email
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Validate phone number (Indian)
export const isValidPhone = (phone) => {
  const phoneRegex = /^[6-9]\d{9}$/;
  return phoneRegex.test(phone?.replace(/\D/g, ''));
};

// Format phone number
export const formatPhone = (phone) => {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
  }
  return phone;
};

// Calculate due date
export const calculateDueDate = (startDate, durationMonths) => {
  const date = new Date(startDate);
  date.setMonth(date.getMonth() + durationMonths);
  return date;
};

// Calculate interest
export const calculateInterest = (principal, rate, months = 1) => {
  return (principal * rate * months) / 100;
};

// Debounce function
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Local storage helpers
export const storage = {
  get: (key) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('Error getting from localStorage:', error);
      return null;
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error setting to localStorage:', error);
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing from localStorage:', error);
    }
  },
  
  clear: () => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  },
};

// Error handler
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    return error.response.data?.detail || error.response.data?.message || 'An error occurred';
  } else if (error.request) {
    // Request was made but no response received
    return 'Network error. Please check your connection.';
  } else {
    // Something else happened
    return error.message || 'An unexpected error occurred';
  }
};

// Generate pledge number
export const generatePledgeNumber = (prefix = 'PL', counter = 1) => {
  return `${prefix}-${String(counter).padStart(4, '0')}`;
};

// Color palette for charts
export const chartColors = [
  '#1976d2',
  '#dc004e',
  '#9c27b0',
  '#673ab7',
  '#3f51b5',
  '#2196f3',
  '#03a9f4',
  '#00bcd4',
  '#009688',
  '#4caf50',
  '#8bc34a',
  '#cddc39',
  '#ffeb3b',
  '#ffc107',
  '#ff9800',
  '#ff5722',
];

export default {
  formatCurrency,
  formatDate,
  formatWeight,
  getStatusColor,
  capitalize,
  generateId,
  isValidEmail,
  isValidPhone,
  formatPhone,
  calculateDueDate,
  calculateInterest,
  debounce,
  storage,
  handleApiError,
  generatePledgeNumber,
  chartColors,
};
