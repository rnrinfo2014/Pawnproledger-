import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stack,
  Chip,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  IconButton,
  Avatar,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  useTheme,
  Divider,
  Grid
} from "@mui/material";
import {
  TrendingUp,
  People,
  Assignment,
  MonetizationOn,
  MoreVert,
  Visibility,
  BusinessCenter,
  Assessment,
  Warning,
  CheckCircle,
  ArrowUpward,
  ArrowDownward,
  AttachMoney,
  Inventory,
  AccountBalance,
  Receipt,
  Schedule,
  Star,
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler,
} from 'chart.js';
import { Bar, Pie, Line, Doughnut } from 'react-chartjs-2';
import { formatCurrency, formatDate, getStatusColor } from '../utils/helpers';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler
);

const DashboardPage = () => {
  const theme = useTheme();
  const [dashboardData, setDashboardData] = useState({
    totalCustomers: 156,
    totalPledges: 89,
    totalRevenue: 2850000,
    totalItems: 234,
    activePledges: 67,
    overdueAmount: 145000,
    loading: false,
  });

  const statsCards = [
    {
      title: 'Total Customers',
      value: dashboardData.totalCustomers,
      icon: <People />,
      color: '#2e7d32',
      change: '+12%',
      trend: 'up',
      bgGradient: 'linear-gradient(135deg, #66bb6a 0%, #4caf50 100%)',
    },
    {
      title: 'Active Pledges',
      value: dashboardData.activePledges,
      icon: <Assignment />,
      color: '#ed6c02',
      change: '+8%',
      trend: 'up',
      bgGradient: 'linear-gradient(135deg, #ffb74d 0%, #ff9800 100%)',
    },
    {
      title: 'Total Revenue',
      value: formatCurrency(dashboardData.totalRevenue),
      icon: <AttachMoney />,
      color: '#1976d2',
      change: '+15%',
      trend: 'up',
      bgGradient: 'linear-gradient(135deg, #64b5f6 0%, #2196f3 100%)',
    },
    {
      title: 'Total Items',
      value: dashboardData.totalItems,
      icon: <Inventory />,
      color: '#9c27b0',
      change: '+5%',
      trend: 'up',
      bgGradient: 'linear-gradient(135deg, #ba68c8 0%, #9c27b0 100%)',
    },
  ];

  // Sample recent pledges data
  const recentPledges = [
    { id: 1, pledgeNo: 'PLG-0001', customer: 'Rajesh Kumar', amount: 50000, status: 'active', date: '2025-09-10' },
    { id: 2, pledgeNo: 'PLG-0002', customer: 'Priya Sharma', amount: 75000, status: 'active', date: '2025-09-09' },
    { id: 3, pledgeNo: 'PLG-0003', customer: 'Anil Gupta', amount: 45000, status: 'redeemed', date: '2025-09-08' },
    { id: 4, pledgeNo: 'PLG-0004', customer: 'Sunita Patel', amount: 65000, status: 'active', date: '2025-09-07' },
    { id: 5, pledgeNo: 'PLG-0005', customer: 'Vikram Singh', amount: 85000, status: 'overdue', date: '2025-09-06' },
  ];

  // Chart configurations
  const pledgeStatusData = {
    labels: ['Active', 'Redeemed', 'Overdue', 'Auctioned'],
    datasets: [
      {
        data: [45, 30, 15, 10],
        backgroundColor: ['#4caf50', '#2196f3', '#f44336', '#ff9800'],
        borderWidth: 0,
        cutout: '65%',
      },
    ],
  };

  const monthlyRevenueData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
    datasets: [
      {
        label: 'Revenue',
        data: [1200000, 1500000, 1800000, 2000000, 2300000, 2500000, 2400000, 2650000, 2850000],
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#1976d2',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
      },
    ],
  };

  const weeklyPledgesData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'New Pledges',
        data: [12, 15, 8, 18, 22, 25, 16],
        backgroundColor: [
          '#FF6384',
          '#36A2EB', 
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
          '#FF6384'
        ],
        borderRadius: 6,
        borderSkipped: false,
      },
    ],
  };

  const quickActions = [
    { icon: <Assignment />, label: 'New Pledge', color: '#1976d2' },
    { icon: <People />, label: 'Add Customer', color: '#2e7d32' },
    { icon: <Inventory />, label: 'Add Item', color: '#ed6c02' },
    { icon: <Receipt />, label: 'Payment', color: '#9c27b0' },
  ];

  if (dashboardData.loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', overflow: 'auto', p: 0 }}>
      {/* Enhanced Header */}
      <Paper 
        elevation={0} 
        sx={{ 
          p: 3, 
          mb: 2, 
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
          color: 'white',
          borderRadius: 3,
        }}
      >
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Dashboard Overview
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9 }}>
              Monitor your pawn business performance and key metrics
            </Typography>
          </Box>
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              startIcon={<Assessment />}
              sx={{ 
                backgroundColor: 'rgba(255,255,255,0.2)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.3)',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.3)',
                }
              }}
            >
              Reports
            </Button>
            <Button
              variant="outlined"
              startIcon={<Schedule />}
              sx={{ 
                color: 'white',
                borderColor: 'rgba(255,255,255,0.5)',
                '&:hover': {
                  borderColor: 'white',
                  backgroundColor: 'rgba(255,255,255,0.1)',
                }
              }}
            >
              Today's Summary
            </Button>
          </Stack>
        </Stack>
      </Paper>

      {/* Stats Cards with Better Design */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        {statsCards.map((card, index) => (
          <Grid xs={12} sm={6} lg={3} key={index}>
            <Card
              sx={{
                height: 140,
                background: card.bgGradient,
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
                },
                transition: 'all 0.3s ease',
              }}
            >
              <CardContent sx={{ position: 'relative', zIndex: 2 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                      {card.title}
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" sx={{ mb: 1 }}>
                      {card.value}
                    </Typography>
                    <Stack direction="row" alignItems="center" spacing={0.5}>
                      {card.trend === 'up' ? (
                        <ArrowUpward sx={{ fontSize: 16 }} />
                      ) : (
                        <ArrowDownward sx={{ fontSize: 16 }} />
                      )}
                      <Typography variant="caption" fontWeight="600">
                        {card.change} from last month
                      </Typography>
                    </Stack>
                  </Box>
                  <Avatar
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      width: 48,
                      height: 48,
                    }}
                  >
                    {card.icon}
                  </Avatar>
                </Stack>
              </CardContent>
              {/* Decorative background element */}
              <Box
                sx={{
                  position: 'absolute',
                  top: -20,
                  right: -20,
                  width: 100,
                  height: 100,
                  borderRadius: '50%',
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  zIndex: 1,
                }}
              />
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Content Grid */}
      <Grid container spacing={2}>
        {/* Revenue Chart - Takes more space */}
        <Grid xs={12} lg={8}>
          <Card sx={{ height: 400, borderRadius: 3 }}>
            <CardContent sx={{ height: '100%' }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="h6" fontWeight="600">
                  Revenue Trend Analysis
                </Typography>
                <IconButton size="small">
                  <MoreVert />
                </IconButton>
              </Stack>
              <Box sx={{ height: 320 }}>
                <Line
                  data={monthlyRevenueData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                      tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        cornerRadius: 8,
                        displayColors: false,
                      },
                    },
                    scales: {
                      x: {
                        grid: {
                          display: false,
                        },
                      },
                      y: {
                        grid: {
                          color: 'rgba(0,0,0,0.05)',
                        },
                        ticks: {
                          callback: function(value) {
                            return '₹' + (value / 100000) + 'L';
                          },
                        },
                      },
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid xs={12} lg={4}>
          <Card sx={{ height: 400, borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                Quick Actions
              </Typography>
              <Stack spacing={2}>
                {quickActions.map((action, index) => (
                  <Button
                    key={index}
                    variant="outlined"
                    startIcon={action.icon}
                    fullWidth
                    sx={{
                      justifyContent: 'flex-start',
                      py: 1.5,
                      borderColor: action.color,
                      color: action.color,
                      '&:hover': {
                        backgroundColor: `${action.color}10`,
                        borderColor: action.color,
                      }
                    }}
                  >
                    {action.label}
                  </Button>
                ))}
              </Stack>
              
              <Divider sx={{ my: 3 }} />
              
              {/* Pledge Status Pie Chart */}
              <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                Pledge Status
              </Typography>
              <Box sx={{ height: 200, display: 'flex', justifyContent: 'center' }}>
                <Doughnut
                  data={pledgeStatusData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                        labels: {
                          padding: 15,
                          usePointStyle: true,
                          font: {
                            size: 12,
                          },
                        },
                      },
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Pledges */}
        <Grid xs={12} lg={8}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="h6" fontWeight="600">
                  Recent Pledges
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<Visibility />}
                  sx={{ borderRadius: 2 }}
                >
                  View All
                </Button>
              </Stack>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Pledge No</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Customer</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Amount</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentPledges.map((pledge) => (
                      <TableRow 
                        key={pledge.id} 
                        hover
                        sx={{
                          '&:hover': {
                            backgroundColor: 'rgba(25, 118, 210, 0.04)',
                          }
                        }}
                      >
                        <TableCell>
                          <Typography variant="body2" fontWeight="600" color="primary">
                            {pledge.pledgeNo}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {pledge.customer}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="600">
                            {formatCurrency(pledge.amount)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {formatDate(pledge.date)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={pledge.status}
                            size="small"
                            color={getStatusColor(pledge.status)}
                            sx={{ 
                              textTransform: 'capitalize',
                              fontWeight: 500,
                              borderRadius: 2,
                            }}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Weekly Performance */}
        <Grid xs={12} lg={4}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                Weekly Performance
              </Typography>
              <Box sx={{ height: 250 }}>
                <Bar
                  data={weeklyPledgesData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      x: {
                        grid: {
                          display: false,
                        },
                      },
                      y: {
                        grid: {
                          color: 'rgba(0,0,0,0.05)',
                        },
                        beginAtZero: true,
                      },
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
