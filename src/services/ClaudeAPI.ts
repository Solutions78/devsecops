import axios from 'axios';

const CLAUDE_BASE = process.env.CLAUDE_API_URL;
const API_KEY = process.env.CLAUDE_API_KEY;

export async function runAgent(agentId: string, input: string) {
  const response = await axios.post(
    `${CLAUDE_BASE}/agents/${agentId}/invoke`,
    { input },
    {
      headers: {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json',
      },
    }
  );

  return response.data;
}
