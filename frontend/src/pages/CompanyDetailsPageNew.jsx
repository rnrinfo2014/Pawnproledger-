import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Divider,
  Stack,
  Chip,
  Avatar,
  Skeleton,
  InputAdornment,
  IconButton,
  Switch,
  FormControlLabel,
  Grid
} from "@mui/material";
import {
  Business,
  Edit,
  Save,
  Cancel,
  Phone,
  LocationOn,
  Email,
  CalendarToday,
  Upload,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { companyAPI } from '../services/api';

const CompanyDetailsPage = () => {
  const { user } = useAuth();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    fetchCompanyDetails();
  }, []);

  const fetchCompanyDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Use company ID 1 as shown in your API example, or get from user context
      const companyId = user?.company_id || 1;
      const response = await companyAPI.getById(companyId);
      
      // Handle the API response structure
      const companyData = response.data || response;
      setCompany(companyData);
      setFormData(companyData);
    } catch (err) {
      console.error('Error fetching company details:', err);
      if (err.response?.status === 404) {
        setError('Company not found. Please check the company ID.');
      } else if (err.response?.status === 401) {
        setError('Unauthorized access. Please check your login credentials.');
      } else {
        setError('Failed to load company details. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      // Prepare the data according to the API schema
      const updateData = {
        name: formData.name,
        address: formData.address,
        city: formData.city,
        phone_number: formData.phone_number,
        logo: formData.logo,
        license_no: formData.license_no,
        status: formData.status || 'active',
        financial_year_start: formData.financial_year_start,
        financial_year_end: formData.financial_year_end
      };
      
      const response = await companyAPI.update(company.id, updateData);
      const updatedCompany = response.data || response;
      
      setCompany(updatedCompany);
      setFormData(updatedCompany);
      setEditing(false);
      setSuccess(true);
      
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Error updating company:', err);
      if (err.response?.status === 422) {
        setError('Validation error. Please check your input data.');
      } else if (err.response?.status === 404) {
        setError('Company not found. Unable to update.');
      } else {
        setError('Failed to update company details. Please try again.');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData(company);
    setEditing(false);
    setError(null);
  };

  const handleLogoUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        setSaving(true);
        setError(null);
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
          setError('Please select a valid image file.');
          setSaving(false);
          return;
        }
        
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
          setError('File size must be less than 5MB.');
          setSaving(false);
          return;
        }
        
        // Upload logo using the API
        const response = await companyAPI.uploadLogo(company.id, file);
        
        // Update the company data with the new logo path
        const updatedCompany = { ...company, logo: response };
        setCompany(updatedCompany);
        setFormData(updatedCompany);
        
        // Show success message
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
        
        console.log('Logo uploaded successfully:', response);
        
      } catch (err) {
        console.error('Error uploading logo:', err);
        if (err.response?.status === 422) {
          setError('Invalid file format or size. Please try a different image.');
        } else {
          setError('Failed to upload logo. Please try again.');
        }
      } finally {
        setSaving(false);
      }
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="rectangular" width="100%" height={200} sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <Grid item xs={12} md={6} key={item}>
              <Skeleton variant="rectangular" width="100%" height={80} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (!company) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Company not found. Please contact your administrator.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      bgcolor: 'grey.50',
      py: 4
    }}>
      <Box sx={{ maxWidth: 1400, mx: 'auto', px: 3 }}>
        {/* Header */}
        <Paper 
          elevation={0} 
          sx={{ 
            p: 4, 
            mb: 4, 
            borderRadius: 3,
            background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
            color: 'white'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              <Avatar 
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.2)', 
                  width: 64, 
                  height: 64,
                  backdropFilter: 'blur(10px)'
                }}
              >
                <Business sx={{ fontSize: 32 }} />
              </Avatar>
              <Box>
                <Typography variant="h3" fontWeight="bold" sx={{ mb: 1 }}>
                  Company Management
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                  Manage your company information and settings
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              {editing ? (
                <>
                  <Button
                    variant="outlined"
                    startIcon={<Cancel />}
                    onClick={handleCancel}
                    disabled={saving}
                    sx={{ 
                      color: 'white', 
                      borderColor: 'rgba(255,255,255,0.5)',
                      '&:hover': { 
                        borderColor: 'white',
                        bgcolor: 'rgba(255,255,255,0.1)'
                      }
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<Save />}
                    onClick={handleSave}
                    disabled={saving}
                    sx={{ 
                      minWidth: 120,
                      bgcolor: 'success.main',
                      '&:hover': { bgcolor: 'success.dark' }
                    }}
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </Button>
                </>
              ) : (
                <Button
                  variant="contained"
                  startIcon={<Edit />}
                  onClick={() => setEditing(true)}
                  sx={{ 
                    bgcolor: 'white',
                    color: 'primary.main',
                    '&:hover': { 
                      bgcolor: 'grey.100',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  Edit Company
                </Button>
              )}
            </Box>
          </Box>

          {/* Status Alerts */}
          {success && (
            <Alert 
              severity="success" 
              sx={{ 
                mt: 3,
                bgcolor: 'rgba(255,255,255,0.15)',
                color: 'white',
                '& .MuiAlert-icon': { color: 'white' }
              }}
            >
              Company details updated successfully!
            </Alert>
          )}

          {error && (
            <Alert 
              severity="error" 
              sx={{ 
                mt: 3,
                bgcolor: 'rgba(255,255,255,0.15)',
                color: 'white',
                '& .MuiAlert-icon': { color: 'white' }
              }}
            >
              {error}
            </Alert>
          )}

          {/* Company Info */}
          {company && (
            <Box sx={{ mt: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                label={`ID: ${company.id}`}
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.2)', 
                  color: 'white',
                  fontWeight: 'bold'
                }}
              />
              <Chip
                label={`Created: ${new Date(company.created_at).toLocaleDateString()}`}
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.2)', 
                  color: 'white',
                  fontWeight: 'bold'
                }}
              />
            </Box>
          )}
        </Paper>

        {/* Company Logo and Basic Info */}
        <Paper 
          elevation={0} 
          sx={{ 
            mb: 4, 
            borderRadius: 3,
            overflow: 'hidden',
            border: '1px solid',
            borderColor: 'grey.200'
          }}
        >
          <CardContent sx={{ p: 0 }}>
            {/* Logo Section */}
            <Box sx={{ 
              background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
              p: 4,
              textAlign: 'center',
              borderBottom: '1px solid',
              borderColor: 'grey.200'
            }}>
              <Box sx={{ position: 'relative', display: 'inline-block' }}>
                <Avatar
                  src={company.logo ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/${company.logo}` : undefined}
                  sx={{
                    width: 140,
                    height: 140,
                    mb: 2,
                    mx: 'auto',
                    bgcolor: 'primary.main',
                    fontSize: 48,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
                    border: '4px solid white'
                  }}
                >
                  <Business sx={{ fontSize: 56 }} />
                </Avatar>
                
                {editing && (
                  <IconButton
                    component="label"
                    sx={{
                      position: 'absolute',
                      bottom: 20,
                      right: -10,
                      bgcolor: 'primary.main',
                      color: 'white',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                      '&:hover': { 
                        bgcolor: 'primary.dark',
                        transform: 'scale(1.1)'
                      },
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <Upload />
                    <input
                      type="file"
                      hidden
                      accept="image/*"
                      onChange={handleLogoUpload}
                    />
                  </IconButton>
                )}
              </Box>
              {company.logo && typeof company.logo === 'string' && (
                <Chip
                  label={company.logo.split('/').pop()}
                  size="small"
                  variant="outlined"
                  sx={{ mt: 1 }}
                />
              )}
            </Box>

            {/* Company Details */}
            <Box sx={{ p: 4 }}>
              <Grid container spacing={4}>
                <Grid item xs={12}>
                  <TextField
                    label="Company Name"
                    value={formData.name || ''}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    disabled={!editing}
                    fullWidth
                    variant={editing ? "outlined" : "filled"}
                    sx={{
                      '& .MuiFilledInput-root': {
                        bgcolor: 'grey.50',
                        '&:hover': { bgcolor: 'grey.100' },
                        '&.Mui-focused': { bgcolor: 'grey.50' }
                      }
                    }}
                    InputProps={{
                      readOnly: !editing,
                      style: { fontSize: '1.2rem', fontWeight: 500 }
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    label="License Number"
                    value={formData.license_no || ''}
                    onChange={(e) => handleInputChange('license_no', e.target.value)}
                    disabled={!editing}
                    fullWidth
                    variant={editing ? "outlined" : "filled"}
                    sx={{
                      '& .MuiFilledInput-root': {
                        bgcolor: 'grey.50',
                        '&:hover': { bgcolor: 'grey.100' }
                      }
                    }}
                    InputProps={{
                      readOnly: !editing,
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between',
                    p: 2,
                    bgcolor: 'grey.50',
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'grey.200'
                  }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formData.status === 'active'}
                          onChange={(e) => handleInputChange('status', e.target.checked ? 'active' : 'inactive')}
                          disabled={!editing}
                          size="medium"
                        />
                      }
                      label={<Typography variant="body1" fontWeight={500}>Active Status</Typography>}
                    />
                    <Chip
                      label={formData.status === 'active' ? 'Active' : 'Inactive'}
                      color={formData.status === 'active' ? 'success' : 'error'}
                      icon={formData.status === 'active' ? <CheckCircle /> : <Error />}
                      sx={{ fontWeight: 'bold' }}
                    />
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </CardContent>
        </Paper>

        {/* Contact Information */}
        <Paper 
          elevation={0} 
          sx={{ 
            mb: 4, 
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'grey.200'
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 2, 
              mb: 3,
              pb: 2,
              borderBottom: '2px solid',
              borderColor: 'primary.main'
            }}>
              <Avatar sx={{ bgcolor: 'primary.main', width: 48, height: 48 }}>
                <Phone />
              </Avatar>
              <Typography variant="h5" fontWeight="bold" color="primary.main">
                Contact Information
              </Typography>
            </Box>
            
            <Grid container spacing={4}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Phone Number"
                  value={formData.phone_number || ''}
                  onChange={(e) => handleInputChange('phone_number', e.target.value)}
                  disabled={!editing}
                  fullWidth
                  variant={editing ? "outlined" : "filled"}
                  sx={{
                    '& .MuiFilledInput-root': {
                      bgcolor: 'grey.50',
                      '&:hover': { bgcolor: 'grey.100' }
                    }
                  }}
                  InputProps={{
                    readOnly: !editing,
                    startAdornment: (
                      <InputAdornment position="start">
                        <Phone color="primary" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  label="City"
                  value={formData.city || ''}
                  onChange={(e) => handleInputChange('city', e.target.value)}
                  disabled={!editing}
                  fullWidth
                  variant={editing ? "outlined" : "filled"}
                  sx={{
                    '& .MuiFilledInput-root': {
                      bgcolor: 'grey.50',
                      '&:hover': { bgcolor: 'grey.100' }
                    }
                  }}
                  InputProps={{
                    readOnly: !editing,
                    startAdornment: (
                      <InputAdornment position="start">
                        <LocationOn color="primary" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  label="Address"
                  value={formData.address || ''}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  disabled={!editing}
                  fullWidth
                  multiline
                  rows={3}
                  variant={editing ? "outlined" : "filled"}
                  sx={{
                    '& .MuiFilledInput-root': {
                      bgcolor: 'grey.50',
                      '&:hover': { bgcolor: 'grey.100' }
                    }
                  }}
                  InputProps={{
                    readOnly: !editing,
                    startAdornment: (
                      <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 1 }}>
                        <LocationOn color="primary" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Paper>

        {/* Financial Year Information */}
        <Paper 
          elevation={0} 
          sx={{ 
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'grey.200'
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 2, 
              mb: 3,
              pb: 2,
              borderBottom: '2px solid',
              borderColor: 'success.main'
            }}>
              <Avatar sx={{ bgcolor: 'success.main', width: 48, height: 48 }}>
                <CalendarToday />
              </Avatar>
              <Typography variant="h5" fontWeight="bold" color="success.main">
                Financial Year
              </Typography>
            </Box>
            
            <Grid container spacing={4}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Financial Year Start"
                  type="date"
                  value={formData.financial_year_start || ''}
                  onChange={(e) => handleInputChange('financial_year_start', e.target.value)}
                  disabled={!editing}
                  fullWidth
                  variant={editing ? "outlined" : "filled"}
                  sx={{
                    '& .MuiFilledInput-root': {
                      bgcolor: 'grey.50',
                      '&:hover': { bgcolor: 'grey.100' }
                    }
                  }}
                  InputLabelProps={{
                    shrink: true,
                  }}
                  InputProps={{
                    readOnly: !editing,
                  }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  label="Financial Year End"
                  type="date"
                  value={formData.financial_year_end || ''}
                  onChange={(e) => handleInputChange('financial_year_end', e.target.value)}
                  disabled={!editing}
                  fullWidth
                  variant={editing ? "outlined" : "filled"}
                  sx={{
                    '& .MuiFilledInput-root': {
                      bgcolor: 'grey.50',
                      '&:hover': { bgcolor: 'grey.100' }
                    }
                  }}
                  InputLabelProps={{
                    shrink: true,
                  }}
                  InputProps={{
                    readOnly: !editing,
                  }}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Paper>
      </Box>
    </Box>
  );
};

export default CompanyDetailsPage;
