import { create } from 'zustand'
import Taro from '@tarojs/taro'

import { getMe, loginWithWechat, updateMe } from '@/services/userApi'
import type { UserProfile } from '@/types/user'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

interface AuthState {
  token: string | null
  user: UserProfile | null
  isLoggedIn: boolean
  silentLogin: () => Promise<void>
  refreshUser: () => Promise<void>
  updateProfile: (payload: { nickname?: string; avatarUrl?: string }) => Promise<void>
  logout: () => void
  hydrate: () => void
}

function readStoredUser(): UserProfile | null {
  try {
    return Taro.getStorageSync(USER_KEY) || null
  } catch {
    return null
  }
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: null,
  user: null,
  isLoggedIn: false,

  hydrate: () => {
    const token = Taro.getStorageSync(TOKEN_KEY) || null
    const user = readStoredUser()
    set({ token, user, isLoggedIn: Boolean(token && user) })
  },

  silentLogin: async () => {
    try {
      const loginResult = await Taro.login()
      if (!loginResult.code) {
        return
      }
      const response = await loginWithWechat(loginResult.code)
      Taro.setStorageSync(TOKEN_KEY, response.token)
      Taro.setStorageSync(USER_KEY, response.user)
      set({ token: response.token, user: response.user, isLoggedIn: true })
    } catch (error) {
      console.warn('silentLogin failed', error)
    }
  },

  refreshUser: async () => {
    const { token } = get()
    if (!token) return
    try {
      const user = await getMe()
      Taro.setStorageSync(USER_KEY, user)
      set({ user, isLoggedIn: true })
    } catch {
      get().logout()
    }
  },

  updateProfile: async (payload) => {
    const user = await updateMe(payload)
    Taro.setStorageSync(USER_KEY, user)
    set({ user })
  },

  logout: () => {
    Taro.removeStorageSync(TOKEN_KEY)
    Taro.removeStorageSync(USER_KEY)
    set({ token: null, user: null, isLoggedIn: false })
  },
}))

useAuthStore.getState().hydrate()
