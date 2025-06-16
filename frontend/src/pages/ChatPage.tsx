import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  Avatar,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
} from '@mui/material'
import { Send, Person, SmartToy, ExpandMore } from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { format } from 'date-fns'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

interface Conversation {
  id: string
  title: string
  messages: Message[]
}

interface ChatSource {
  content: string
  metadata: any
  similarity: number
}

interface ChatResponse {
  conversation_id: string
  message: string
  sources: ChatSource[]
}

export default function ChatPage() {
  const { id: conversationId } = useParams()
  const [message, setMessage] = useState('')
  const [currentSources, setCurrentSources] = useState<ChatSource[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  const { data: conversation, isLoading } = useQuery<Conversation>({
    queryKey: ['conversation', conversationId],
    queryFn: async () => {
      if (!conversationId) return null
      const response = await axios.get(`/api/v1/chat/conversations/${conversationId}`)
      return response.data
    },
    enabled: !!conversationId,
  })

  const chatMutation = useMutation({
    mutationFn: async ({ message, conversationId }: { message: string; conversationId?: string }) => {
      const response = await axios.post<ChatResponse>('/api/v1/chat/', {
        message,
        conversation_id: conversationId || null,
      })
      return response.data
    },
    onSuccess: (data) => {
      setCurrentSources(data.sources)
      queryClient.invalidateQueries({ queryKey: ['conversation', data.conversation_id] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      setMessage('')
      
      if (!conversationId) {
        window.history.replaceState(null, '', `/chat/${data.conversation_id}`)
      }
    },
  })

  const handleSendMessage = () => {
    if (message.trim()) {
      chatMutation.mutate({
        message: message.trim(),
        conversationId: conversationId || undefined,
      })
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation?.messages, chatMutation.isPending])

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box display="flex" height="calc(100vh - 200px)">
      <Box flex={1} display="flex" flexDirection="column">
        <Typography variant="h5" gutterBottom>
          {conversation?.title || 'New Conversation'}
        </Typography>

        <Paper sx={{ flex: 1, mb: 2, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
            {!conversation?.messages?.length && !chatMutation.isPending && (
              <Box
                display="flex"
                flexDirection="column"
                justifyContent="center"
                alignItems="center"
                height="100%"
                textAlign="center"
              >
                <SmartToy sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Start a conversation
                </Typography>
                <Typography color="text.secondary">
                  Ask questions about your uploaded documents and I'll help you find answers.
                </Typography>
              </Box>
            )}

            <List>
              {conversation?.messages.map((msg) => (
                <ListItem key={msg.id} sx={{ alignItems: 'flex-start', mb: 1 }}>
                  <Avatar sx={{ mr: 2, mt: 0.5 }}>
                    {msg.role === 'user' ? <Person /> : <SmartToy />}
                  </Avatar>
                  <Box sx={{ flex: 1 }}>
                    <Box display="flex" alignItems="center" mb={0.5}>
                      <Typography variant="subtitle2" sx={{ mr: 1 }}>
                        {msg.role === 'user' ? 'You' : 'DocIntell'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {format(new Date(msg.created_at), 'HH:mm')}
                      </Typography>
                    </Box>
                    <Paper sx={{ p: 2, backgroundColor: msg.role === 'user' ? 'primary.light' : 'grey.100' }}>
                      {msg.role === 'assistant' ? (
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      ) : (
                        <Typography>{msg.content}</Typography>
                      )}
                    </Paper>
                  </Box>
                </ListItem>
              ))}

              {chatMutation.isPending && (
                <ListItem sx={{ alignItems: 'flex-start', mb: 1 }}>
                  <Avatar sx={{ mr: 2, mt: 0.5 }}>
                    <SmartToy />
                  </Avatar>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
                      DocIntell
                    </Typography>
                    <Paper sx={{ p: 2, backgroundColor: 'grey.100' }}>
                      <Box display="flex" alignItems="center">
                        <CircularProgress size={16} sx={{ mr: 1 }} />
                        <Typography>Thinking...</Typography>
                      </Box>
                    </Paper>
                  </Box>
                </ListItem>
              )}
            </List>
            <div ref={messagesEndRef} />
          </Box>

          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Box display="flex" gap={1}>
              <TextField
                fullWidth
                multiline
                maxRows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your documents..."
                disabled={chatMutation.isPending}
              />
              <IconButton
                onClick={handleSendMessage}
                disabled={!message.trim() || chatMutation.isPending}
                color="primary"
              >
                <Send />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      </Box>

      {currentSources.length > 0 && (
        <Paper sx={{ width: 300, ml: 2, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Sources
          </Typography>
          {currentSources.map((source, index) => (
            <Accordion key={index} sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box>
                  <Typography variant="subtitle2">
                    {source.metadata.filename}
                  </Typography>
                  <Chip
                    label={`${Math.round(source.similarity * 100)}% match`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2">
                  {source.content}
                </Typography>
              </AccordionDetails>
            </Accordion>
          ))}
        </Paper>
      )}
    </Box>
  )
}