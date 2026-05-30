import { PropsWithChildren } from 'react'
import { useLaunch } from '@tarojs/taro'

import { useAuthStore } from '@/stores/authStore'
import { loadAppFonts } from '@/utils/loadFonts'
import './app.scss'

function App({ children }: PropsWithChildren) {
  useLaunch(() => {
    loadAppFonts()
    useAuthStore.getState().hydrate()
    void useAuthStore.getState().silentLogin()
  })

  return children
}

export default App
