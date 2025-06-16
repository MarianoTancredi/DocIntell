import { Grid, Paper, Typography, Box, Card, CardContent, Avatar, List, ListItem, ListItemText, Chip } from '@mui/material'
import { Description, Chat, CloudUpload } from '@mui/icons-material'
import { useAuthStore } from '../stores/authStore'

// Mock data for demo purposes
const mockDocuments = [
  {
    id: '1',
    filename: 'Sample Document 1.pdf',
    processing_status: 'completed',
    created_at: '2024-01-15T10:30:00Z',
    metadata: { file_size: 1024000 }
  },
  {
    id: '2', 
    filename: 'Report Q4 2023.docx',
    processing_status: 'completed',
    created_at: '2024-01-14T14:20:00Z',
    metadata: { file_size: 512000 }
  },
  {
    id: '3',
    filename: 'Meeting Notes.txt',
    processing_status: 'processing',
    created_at: '2024-01-16T09:15:00Z',
    metadata: { file_size: 256000 }
  }
]

const mockConversations = [
  {
    id: '1',
    title: 'Analysis of Q4 Report',
    created_at: '2024-01-15T11:00:00Z',
    updated_at: '2024-01-15T11:30:00Z'
  },
  {
    id: '2',
    title: 'Document Summary Request',
    created_at: '2024-01-14T15:00:00Z', 
    updated_at: '2024-01-14T15:45:00Z'
  }
]

export default function DashboardPage() {
  const { user } = useAuthStore()

  const recentDocuments = mockDocuments.slice(0, 5)
  const recentConversations = mockConversations.slice(0, 5)

  const stats = [
    {
      title: 'Total Documents',
      value: mockDocuments.length,
      icon: <Description />,
      color: '#1976d2',
    },
    {
      title: 'Active Conversations',
      value: mockConversations.length,
      icon: <Chat />,
      color: '#2e7d32',
    },
    {
      title: 'Documents Processed',
      value: mockDocuments.filter(d => d.processing_status === 'completed').length,
      icon: <CloudUpload />,
      color: '#ed6c02',
    },
  ]

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric', 
      year: 'numeric'
    })
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome back, {user?.full_name || user?.username}!
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: stat.color, mr: 2 }}>
                    {stat.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h4" component="div">
                      {stat.value}
                    </Typography>
                    <Typography color="text.secondary">
                      {stat.title}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Documents
            </Typography>
            {recentDocuments.length > 0 ? (
              <List>
                {recentDocuments.map((doc) => (
                  <ListItem key={doc.id} divider>
                    <ListItemText
                      primary={doc.filename}
                      secondary={`Uploaded ${formatDate(doc.created_at)}`}
                    />
                    <Chip
                      label={doc.processing_status}
                      color={doc.processing_status === 'completed' ? 'success' : 'warning'}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="text.secondary">
                No documents uploaded yet
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Conversations
            </Typography>
            {recentConversations.length > 0 ? (
              <List>
                {recentConversations.map((conv) => (
                  <ListItem key={conv.id} divider>
                    <ListItemText
                      primary={conv.title}
                      secondary={`Last activity ${formatDate(conv.updated_at || conv.created_at)}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="text.secondary">
                No conversations started yet
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}