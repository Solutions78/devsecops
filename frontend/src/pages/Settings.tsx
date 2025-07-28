import {
  Box,
  Typography,
  Card,
  CardContent,
} from '@mui/material'

export default function Settings() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Configure system settings and preferences
      </Typography>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Coming soon: System settings and configuration management
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}