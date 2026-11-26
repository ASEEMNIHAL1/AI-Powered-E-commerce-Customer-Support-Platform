import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '../types'

interface AuthState {
  token: string | null
  user: User | null
  setToken: (token: string) => void
  setAuth: (token: string, user: User) => void
  logout: () => void
  isAuthenticated: () => boolean
  isStaff: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      setToken: (token) => set({ token }),
      setAuth: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
      isAuthenticated: () => !!get().token,
      isStaff: () => ['staff', 'admin'].includes(get().user?.role ?? ''),
    }),
    { name: 'auth-storage' }
  )
)
