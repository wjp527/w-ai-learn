import { View, Text, Button } from '@tarojs/components'
import Taro, { useLoad } from '@tarojs/taro'
import { Mascot } from '@/components/Mascot'
import { useAuthStore } from '@/stores/authStore'
import './index.scss'

export default function WelcomePage() {
  useLoad(() => {
    void useAuthStore.getState().silentLogin()
  })
  return (
    <View className='welcome-page blackboard page-flex-col'>
      <View className='welcome-halftone' />
      <View className='welcome-glow' />
      <View className='welcome-desk' />

      <View className='welcome-sign comic-border'>
        <View className='tape' />
        <Text className='welcome-sign-chalk font-chalk'>怕踢中学</Text>
        <Text className='welcome-sign-sub font-comic'>知识闯关分校</Text>
      </View>

      <View className='welcome-body'>
        <Mascot variant='full' />
        <View className='welcome-bubble bubble'>
          <Text className='welcome-bubble-title font-comic'>我是小衰神助手</Text>
          <Text className='welcome-bubble-desc font-body'>贴笔记、闯关卡、告别 0 分恐惧（大概）</Text>
        </View>
      </View>

      <View className='welcome-footer page-footer'>
        <Button
          className='comic-btn comic-btn--press welcome-start font-comic'
          onClick={() => Taro.switchTab({ url: '/pages/input/index' })}
        >
          开始闯！
        </Button>
        <Text className='welcome-note font-body'>登录后同步学习记录</Text>
      </View>
    </View>
  )
}
