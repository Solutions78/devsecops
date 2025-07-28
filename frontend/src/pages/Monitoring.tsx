import {
  Box,
  Typography,
  Card,
  CardContent,
} from '@mui/material'

export default function Monitoring() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Monitoring & Metrics
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        System performance and Prometheus metrics
      </Typography>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Prometheus Integration
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Coming soon: Real-time metrics dashboard with Prometheus integration
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}