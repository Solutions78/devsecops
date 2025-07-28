import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
} from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'

export default function Tasks() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Tasks
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Submit tasks and monitor execution across agents
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          disabled // TODO: Implement task submission
        >
          New Task
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Task Management Interface
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Coming soon: Task submission, monitoring, and results viewing
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}