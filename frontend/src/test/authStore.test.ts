import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

vi.mock('axios')
const mockedAxios = vi.mocked(axios) as any

describe('AuthStore', () => {
  beforeEach(() => {
    useAuthStore.getState().logout()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('login', () => {
    it('should login successfully and set user data', async () => {
      const mockTokenResponse = {
        data: { access_token: 'fake-token', token_type: 'bearer' }
      }
      const mockUserResponse = {
        data: {
          id: 1,
          email: 'test@example.com',
          username: 'testuser',
          full_name: 'Test User',
          is_active: true,
          created_at: '2023-01-01T00:00:00Z'
        }
      }

      mockedAxios.post.mockResolvedValueOnce(mockTokenResponse)
      mockedAxios.get.mockResolvedValueOnce(mockUserResponse)

      const store = useAuthStore.getState()
      await store.login('testuser', 'password')

      expect(store.token).toBe('fake-token')
      expect(store.isAuthenticated).toBe(true)
      expect(store.user).toEqual(mockUserResponse.data)
      expect(axios.defaults.headers.common['Authorization']).toBe('Bearer fake-token')
    })

    it('should handle login failure', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Login failed'))

      const store = useAuthStore.getState()
      
      await expect(store.login('testuser', 'wrongpassword')).rejects.toThrow('Login failed')
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
    })
  })

  describe('register', () => {
    it('should register and login user', async () => {
      const mockRegisterResponse = {
        data: {
          id: 1,
          email: 'new@example.com',
          username: 'newuser',
          full_name: 'New User',
          is_active: true,
          created_at: '2023-01-01T00:00:00Z'
        }
      }
      const mockTokenResponse = {
        data: { access_token: 'fake-token', token_type: 'bearer' }
      }
      const mockUserResponse = {
        data: mockRegisterResponse.data
      }

      mockedAxios.post
        .mockResolvedValueOnce(mockRegisterResponse)
        .mockResolvedValueOnce(mockTokenResponse)
      mockedAxios.get.mockResolvedValueOnce(mockUserResponse)

      const store = useAuthStore.getState()
      await store.register({
        email: 'new@example.com',
        username: 'newuser',
        password: 'password',
        full_name: 'New User'
      })

      expect(store.isAuthenticated).toBe(true)
      expect(store.user?.email).toBe('new@example.com')
    })
  })

  describe('logout', () => {
    it('should clear user data and token', () => {
      const store = useAuthStore.getState()
      
      // Set some initial state
      store.setUser({
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        is_active: true,
        created_at: '2023-01-01T00:00:00Z'
      })

      store.logout()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(axios.defaults.headers.common['Authorization']).toBeUndefined()
    })
  })
})