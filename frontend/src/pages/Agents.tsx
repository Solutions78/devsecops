import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
} from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import { useAgents } from '../hooks/useWebSocket'
import AgentStatusCard from '../components/agents/AgentStatusCard'

export default function Agents() {
  const { data: agents, isLoading } = useAgents()

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            AI Agents
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage and monitor your DevSecOps AI agents
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          disabled // TODO: Implement agent configuration
        >
          Configure Agent
        </Button>
      </Box>

      {isLoading ? (
        <Typography>Loading agents...</Typography>
      ) : (
        <Grid container spacing={3}>
          {agents?.map((agent) => (
            <Grid item xs={12} sm={6} md={4} key={agent.name}>
              <AgentStatusCard agent={agent} />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  )
}