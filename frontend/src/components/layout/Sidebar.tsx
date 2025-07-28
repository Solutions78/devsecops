import { useLocation, useNavigate } from 'react-router-dom'
import {
  Box,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Chip,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  SmartToy as AgentsIcon,
  Assignment as TasksIcon,
  Security as SecurityIcon,
  Monitor as MonitoringIcon,
  Settings as SettingsIcon,
  CloudQueue as AzureIcon,
} from '@mui/icons-material'

interface SidebarProps {
  onMobileClose?: () => void
}

const navigation = [
  {
    title: 'Dashboard',
    path: '/',
    icon: DashboardIcon,
  },
  {
    title: 'Agents',
    path: '/agents',
    icon: AgentsIcon,
    badge: '9',
  },
  {
    title: 'Tasks',
    path: '/tasks',
    icon: TasksIcon,
  },
  {
    title: 'Security',
    path: '/security',
    icon: SecurityIcon,
    description: 'Azure Key Vault',
  },
  {
    title: 'Monitoring',
    path: '/monitoring',
    icon: MonitoringIcon,
  },
  {
    title: 'Settings',
    path: '/settings',
    icon: SettingsIcon,
  },
]

export default function Sidebar({ onMobileClose }: SidebarProps) {
  const location = useLocation()
  const navigate = useNavigate()

  const handleNavigation = (path: string) => {
    navigate(path)
    onMobileClose?.()
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SecurityIcon color="primary" />
          <Typography variant="h6" noWrap>
            DevSecOps
          </Typography>
        </Box>
      </Toolbar>
      
      <Divider />
      
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            p: 1.5,
            backgroundColor: 'primary.main',
            borderRadius: 1,
            color: 'white',
          }}
        >
          <AzureIcon />
          <Box>
            <Typography variant="body2" fontWeight={600}>
              Azure Integration
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              Active Directory + Key Vault
            </Typography>
          </Box>
        </Box>
      </Box>

      <List sx={{ flex: 1, px: 1 }}>
        {navigation.map((item) => {
          const isActive = location.pathname === item.path
          const IconComponent = item.icon

          return (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                selected={isActive}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 1,
                  mx: 1,
                  mb: 0.5,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                  },
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? 'white' : 'text.secondary',
                    minWidth: 40,
                  }}
                >
                  <IconComponent />
                </ListItemIcon>
                <ListItemText 
                  primary={item.title}
                  secondary={item.description}
                  secondaryTypographyProps={{
                    variant: 'caption',
                    sx: { 
                      color: isActive ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                    },
                  }}
                />
                {item.badge && (
                  <Chip
                    label={item.badge}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.75rem',
                      backgroundColor: isActive ? 'rgba(255,255,255,0.2)' : 'action.selected',
                      color: isActive ? 'white' : 'text.primary',
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>

      <Divider />
      
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary">
          © 2024 DevSecOps Orchestrator
        </Typography>
      </Box>
    </Box>
  )
}