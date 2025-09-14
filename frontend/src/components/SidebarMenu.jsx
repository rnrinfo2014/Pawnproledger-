import React, { useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Typography,
  Divider,
} from '@mui/material';
import {
  Dashboard,
  People,
  Assignment,
  Inventory,
  Category,
  AccountBalance,
  Assessment,
  MonetizationOn,
  Settings,
  Business,
  ExpandLess,
  ExpandMore,
  LocationOn,
  Palette,
  Security,
  Person,
  CreditCard,
  Receipt,
  TrendingUp,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const SidebarMenu = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [expandedMenus, setExpandedMenus] = useState({});

  const handleExpandClick = (menuKey) => {
    setExpandedMenus(prev => ({
      ...prev,
      [menuKey]: !prev[menuKey]
    }));
  };

  const handleNavigation = (path) => {
    navigate(path);
  };

  const isActive = (path) => location.pathname === path;
  const isParentActive = (paths) => paths.some(path => location.pathname.startsWith(path));

  const menuItems = [
    {
      key: 'dashboard',
      text: 'Dashboard',
      icon: <Dashboard />,
      path: '/dashboard',
    },
    {
      key: 'company',
      text: 'Company',
      icon: <Business />,
      expandable: true,
      children: [
        {
          text: 'Branch Management',
          icon: <LocationOn />,
          path: '/company/branches',
        },
        {
          text: 'Settings',
          icon: <Settings />,
          path: '/company/settings',
        },
      ],
    },
    {
      key: 'customers',
      text: 'Customers',
      icon: <People />,
      expandable: true,
      children: [
        {
          text: 'All Customers',
          icon: <People />,
          path: '/customers',
        },
        {
          text: 'Add Customer',
          icon: <Person />,
          path: '/customers/new',
        },
        {
          text: 'Customer Reports',
          icon: <Assessment />,
          path: '/customers/reports',
        },
      ],
    },
    {
      key: 'pledges',
      text: 'Pledges',
      icon: <Assignment />,
      expandable: true,
      children: [
        {
          text: 'All Pledges',
          icon: <Assignment />,
          path: '/pledges',
        },
        {
          text: 'New Pledge',
          icon: <CreditCard />,
          path: '/pledges/new',
        },
        {
          text: 'Pledge Reports',
          icon: <TrendingUp />,
          path: '/pledges/reports',
        },
      ],
    },
    {
      key: 'items',
      text: 'Items',
      icon: <Inventory />,
      path: '/items',
    },
    {
      key: 'schemes',
      text: 'Schemes',
      icon: <Category />,
      path: '/schemes',
    },
    {
      key: 'accounts',
      text: 'Accounts',
      icon: <AccountBalance />,
      expandable: true,
      children: [
        {
          text: 'Chart of Accounts',
          icon: <AccountBalance />,
          path: '/accounts',
        },
        {
          text: 'Transactions',
          icon: <Receipt />,
          path: '/accounts/transactions',
        },
        {
          text: 'Financial Reports',
          icon: <Assessment />,
          path: '/accounts/reports',
        },
      ],
    },
    {
      key: 'reports',
      text: 'Reports',
      icon: <Assessment />,
      expandable: true,
      children: [
        {
          text: 'Business Reports',
          icon: <TrendingUp />,
          path: '/reports/business',
        },
        {
          text: 'Financial Reports',
          icon: <MonetizationOn />,
          path: '/reports/financial',
        },
        {
          text: 'Custom Reports',
          icon: <Palette />,
          path: '/reports/custom',
        },
      ],
    },
    {
      key: 'settings',
      text: 'System Settings',
      icon: <Settings />,
      expandable: true,
      children: [
        {
          text: 'User Management',
          icon: <Security />,
          path: '/settings/users',
        },
        {
          text: 'System Preferences',
          icon: <Settings />,
          path: '/settings/preferences',
        },
      ],
    },
  ];

  const renderMenuItem = (item) => {
    if (item.expandable) {
      const isExpanded = expandedMenus[item.key];
      const hasActiveChild = isParentActive(item.children.map(child => child.path));

      return (
        <React.Fragment key={item.key}>
          <ListItem disablePadding>
            <ListItemButton
              onClick={() => handleExpandClick(item.key)}
              sx={{
                mx: 1,
                borderRadius: 2,
                backgroundColor: hasActiveChild ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(25, 118, 210, 0.04)',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: hasActiveChild ? '#1976d2' : 'inherit',
                  minWidth: 40,
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontSize: '0.9rem',
                  fontWeight: hasActiveChild ? 600 : 400,
                  color: hasActiveChild ? '#1976d2' : 'inherit',
                }}
              />
              {isExpanded ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
          </ListItem>
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children.map((child, index) => (
                <ListItem key={index} disablePadding>
                  <ListItemButton
                    onClick={() => handleNavigation(child.path)}
                    sx={{
                      pl: 4,
                      mx: 1,
                      borderRadius: 2,
                      backgroundColor: isActive(child.path) ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
                      borderLeft: isActive(child.path) ? '3px solid #1976d2' : 'none',
                      '&:hover': {
                        backgroundColor: 'rgba(25, 118, 210, 0.04)',
                      },
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        color: isActive(child.path) ? '#1976d2' : 'inherit',
                        minWidth: 36,
                      }}
                    >
                      {child.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={child.text}
                      primaryTypographyProps={{
                        fontSize: '0.85rem',
                        fontWeight: isActive(child.path) ? 600 : 400,
                        color: isActive(child.path) ? '#1976d2' : 'inherit',
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Collapse>
        </React.Fragment>
      );
    } else {
      const active = isActive(item.path);
      return (
        <ListItem key={item.key} disablePadding>
          <ListItemButton
            onClick={() => handleNavigation(item.path)}
            sx={{
              mx: 1,
              borderRadius: 2,
              backgroundColor: active ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
              borderLeft: active ? '3px solid #1976d2' : 'none',
              '&:hover': {
                backgroundColor: 'rgba(25, 118, 210, 0.04)',
              },
            }}
          >
            <ListItemIcon
              sx={{
                color: active ? '#1976d2' : 'inherit',
                minWidth: 40,
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText
              primary={item.text}
              primaryTypographyProps={{
                fontSize: '0.9rem',
                fontWeight: active ? 600 : 400,
                color: active ? '#1976d2' : 'inherit',
              }}
            />
          </ListItemButton>
        </ListItem>
      );
    }
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography
        variant="overline"
        sx={{
          px: 3,
          color: 'text.secondary',
          fontWeight: 600,
          letterSpacing: 1,
        }}
      >
        Main Menu
      </Typography>
      <List sx={{ mt: 1 }}>
        {menuItems.map(renderMenuItem)}
      </List>
    </Box>
  );
};

export default SidebarMenu;
