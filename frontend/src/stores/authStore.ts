import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  register: (userData: {
    email: string
    username: string
    password: string
    full_name?: string
  }) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (username: string, _password: string) => {
        try {
          // Simulate successful login for demo purposes
          const mockUser: User = {
            id: 1,
            email: 'demo@example.com',
            username: username,
            full_name: 'Demo User',
            is_active: true,
            created_at: new Date().toISOString(),
          }

          set({
            token: 'demo-token-123',
            isAuthenticated: true,
            user: mockUser,
          })

        } catch (error) {
          console.error('Login failed:', error)
          throw error
        }
      },

      register: async (userData) => {
        try {
          // Simulate successful registration for demo purposes
          const mockUser: User = {
            id: 1,
            email: userData.email,
            username: userData.username,
            full_name: userData.full_name,
            is_active: true,
            created_at: new Date().toISOString(),
          }

          set({
            token: 'demo-token-123',
            isAuthenticated: true,
            user: mockUser,
          })
        } catch (error) {
          console.error('Registration failed:', error)
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      setUser: (user: User) => {
        set({ user })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)