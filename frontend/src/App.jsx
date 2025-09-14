import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import theme from './utils/theme';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/MainLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPageNew';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              
              {/* Placeholder routes for future pages */}
              <Route path="/customers" element={<div>Customers Page - Coming Soon</div>} />
              <Route path="/pledges" element={<div>Pledges Page - Coming Soon</div>} />
              <Route path="/items" element={<div>Items Page - Coming Soon</div>} />
              <Route path="/schemes" element={<div>Schemes Page - Coming Soon</div>} />
              <Route path="/accounts" element={<div>Accounts Page - Coming Soon</div>} />
              <Route path="/reports" element={<div>Reports Page - Coming Soon</div>} />
              <Route path="/transactions" element={<div>Transactions Page - Coming Soon</div>} />
            </Route>
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
