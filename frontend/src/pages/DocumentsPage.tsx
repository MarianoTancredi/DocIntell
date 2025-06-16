import { useState } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  IconButton,
  Alert,
  LinearProgress,
} from '@mui/material'
import { CloudUpload, Delete, Visibility } from '@mui/icons-material'
import { useDropzone } from 'react-dropzone'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { format } from 'date-fns'

interface Document {
  id: string
  filename: string
  file_type: string
  file_size: number
  processing_status: string
  created_at: string
  content?: string
  metadata: any
}

export default function DocumentsPage() {
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const queryClient = useQueryClient()

  const { data: documents = [] } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/documents/')
      return response.data
    },
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post('/api/v1/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0
          setUploadProgress(progress)
        },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      setIsUploading(false)
      setUploadProgress(0)
    },
    onError: () => {
      setIsUploading(false)
      setUploadProgress(0)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (documentId: string) => {
      await axios.delete(`/api/v1/documents/${documentId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setIsUploading(true)
      uploadMutation.mutate(acceptedFiles[0])
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: false,
  })

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'processing':
        return 'warning'
      case 'failed':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Documents
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed #ccc',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? '#f5f5f5' : 'transparent',
              '&:hover': {
                backgroundColor: '#f5f5f5',
              },
            }}
          >
            <input {...getInputProps()} />
            <CloudUpload sx={{ fontSize: 48, color: '#ccc', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'Drop the file here...'
                : 'Drag & drop a document here, or click to select'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Supported formats: PDF, TXT, DOC, DOCX (Max 10MB)
            </Typography>
          </Box>
          
          {isUploading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress variant="determinate" value={uploadProgress} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Uploading... {uploadProgress}%
              </Typography>
            </Box>
          )}

          {uploadMutation.isError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              Upload failed. Please try again.
            </Alert>
          )}
        </CardContent>
      </Card>

      <Grid container spacing={2}>
        {documents.map((doc) => (
          <Grid item xs={12} sm={6} md={4} key={doc.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" noWrap title={doc.filename}>
                  {doc.filename}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatFileSize(doc.file_size)}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {format(new Date(doc.created_at), 'MMM dd, yyyy HH:mm')}
                </Typography>
                
                <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                  <Chip
                    label={doc.processing_status}
                    color={getStatusColor(doc.processing_status) as any}
                    size="small"
                  />
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => setSelectedDocument(doc)}
                      disabled={doc.processing_status !== 'completed'}
                    >
                      <Visibility />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => deleteMutation.mutate(doc.id)}
                      color="error"
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog
        open={!!selectedDocument}
        onClose={() => setSelectedDocument(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{selectedDocument?.filename}</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {selectedDocument?.content}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedDocument(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}