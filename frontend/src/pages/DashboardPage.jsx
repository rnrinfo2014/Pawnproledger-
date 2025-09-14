import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  LinearProgress,
  Chip,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  People,
  Assignment,
  AttachMoney,
  Inventory,
  MoreVert,
  ArrowUpward,
  ArrowDownward,
  Visibility,
} from '@mui/icons-material';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';
import { formatCurrency, formatDate, getStatusColor } from '../utils/helpers';
import { pledgeAPI, customerAPI, itemAPI } from '../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

// Mock data for charts (replace with real API data)
const chartData = {
  revenue: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Revenue',
        data: [65000, 59000, 80000, 81000, 56000, 95000],
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        tension: 0.4,
      },
    ],
  },
  pledgeStatus: {
    labels: ['Active', 'Redeemed', 'Auctioned', 'Overdue'],
    datasets: [
      {
        data: [45, 25, 15, 15],
        backgroundColor: ['#4caf50', '#2196f3', '#ff9800', '#f44336'],
        borderWidth: 0,
      },
    ],
  },
  monthlyPledges: {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'New Pledges',
        data: [12, 19, 15, 25],
        backgroundColor: '#1976d2',
      },
    ],
  },
};

const chartOptions = {
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
        borderDash: [5, 5],
      },
    },
  },
};

const DashboardPage = () => {
  const [dashboardData, setDashboardData] = useState({
    totalCustomers: 0,
    totalPledges: 0,
    totalRevenue: 0,
    totalItems: 0,
    recentPledges: [],
    loading: true,
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Fetch data from APIs
      const [customers, pledges, items] = await Promise.all([
        customerAPI.getAll(0, 100),
        pledgeAPI.getAll(0, 100),
        itemAPI.getAll(0, 100),
      ]);

      // Calculate total revenue from pledges
      const totalRevenue = pledges.reduce((sum, pledge) => sum + (pledge.total_loan_amount || 0), 0);

      setDashboardData({
        totalCustomers: customers.length,
        totalPledges: pledges.length,
        totalRevenue: totalRevenue,
        totalItems: items.length,
        recentPledges: pledges.slice(0, 5), // Get 5 most recent
        loading: false,
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setDashboardData(prev => ({ ...prev, loading: false }));
    }
  };

  const statsCards = [
    {
      title: 'Total Customers',
      value: dashboardData.totalCustomers,
      icon: <People />,
      color: '#2e7d32',
      change: '+12%',
      trend: 'up',
    },
    {
      title: 'Active Pledges',
      value: dashboardData.totalPledges,
      icon: <Assignment />,
      color: '#ed6c02',
      change: '+8%',
      trend: 'up',
    },
    {
      title: 'Total Revenue',
      value: formatCurrency(dashboardData.totalRevenue),
      icon: <AttachMoney />,
      color: '#1976d2',
      change: '+15%',
      trend: 'up',
    },
    {
      title: 'Total Items',
      value: dashboardData.totalItems,
      icon: <Inventory />,
      color: '#9c27b0',
      change: '-5%',
      trend: 'down',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statsCards.map((card, index) => (
          <Grid item xs={12} sm={6} lg={3} key={index}>
            <Card
              sx={{
                height: '100%',
                background: `linear-gradient(135deg, ${card.color}15 0%, ${card.color}25 100%)`,
                border: `1px solid ${card.color}30`,
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {card.title}
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
                      {dashboardData.loading ? '-' : card.value}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {card.trend === 'up' ? (
                        <ArrowUpward sx={{ fontSize: 16, color: 'success.main' }} />
                      ) : (
                        <ArrowDownward sx={{ fontSize: 16, color: 'error.main' }} />
                      )}
                      <Typography
                        variant="caption"
                        sx={{ color: card.trend === 'up' ? 'success.main' : 'error.main' }}
                      >
                        {card.change}
                      </Typography>
                    </Box>
                  </Box>
                  <Avatar
                    sx={{
                      bgcolor: card.color,
                      width: 56,
                      height: 56,
                    }}
                  >
                    {card.icon}
                  </Avatar>
                </Box>
                {dashboardData.loading && <LinearProgress sx={{ mt: 2 }} />}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Revenue Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Revenue Trend
                </Typography>
                <IconButton size="small">
                  <MoreVert />
                </IconButton>
              </Box>
              <Box sx={{ height: 300 }}>
                <Line data={chartData.revenue} options={chartOptions} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Pledge Status Chart */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Pledge Status
              </Typography>
              <Box sx={{ height: 300 }}>
                <Doughnut
                  data={chartData.pledgeStatus}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                      },
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Bottom Row */}
      <Grid container spacing={3}>
        {/* Recent Pledges */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Recent Pledges
                </Typography>
                <Button size="small" endIcon={<Visibility />}>
                  View All
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Pledge No</TableCell>
                      <TableCell>Customer</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {dashboardData.recentPledges.map((pledge, index) => (
                      <TableRow key={index}>
                        <TableCell sx={{ fontWeight: 500 }}>
                          {pledge.pledge_no || `PL-${String(index + 1).padStart(4, '0')}`}
                        </TableCell>
                        <TableCell>Customer {pledge.customer_id}</TableCell>
                        <TableCell>{formatCurrency(pledge.total_loan_amount)}</TableCell>
                        <TableCell>{formatDate(pledge.pledge_date)}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={pledge.status || 'Active'}
                            color={getStatusColor(pledge.status)}
                            variant="outlined"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                    {dashboardData.recentPledges.length === 0 && !dashboardData.loading && (
                      <TableRow>
                        <TableCell colSpan={5} align="center">
                          No recent pledges found
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Weekly Pledges */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Weekly Pledges
              </Typography>
              <Box sx={{ height: 200 }}>
                <Bar
                  data={chartData.monthlyPledges}
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
                          borderDash: [5, 5],
                        },
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
