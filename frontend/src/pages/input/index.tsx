import { useCallback, useState } from 'react'
import { View, Text, Textarea, Button } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'

import { Mascot } from '@/components/Mascot'
import { createSession, getSession } from '@/services/api'
import { getMyResume } from '@/services/userApi'
import { useAuthStore } from '@/stores/authStore'
import { useSessionStore } from '@/stores/sessionStore'
import type { ResumeInfo } from '@/types/user'
import { getStatusBarHeight } from '@/utils/system'
import { setTabBarIndex } from '@/utils/tabBar'
import './index.scss'

const STATUS_BAR_HEIGHT = getStatusBarHeight()

const MIN_LENGTH = 5
const MAX_LENGTH = 2000

export default function InputPage() {
  const { isLoggedIn } = useAuthStore()
  const { sourceText, questionCount, setInput, setSession, setSessionDetail } = useSessionStore()
  const [text, setText] = useState(sourceText)
  const [count, setCount] = useState(questionCount)
  const [loading, setLoading] = useState(false)
  const [resume, setResume] = useState<ResumeInfo | null>(null)

  const loadResume = useCallback(async () => {
    if (!useAuthStore.getState().isLoggedIn) {
      setResume(null)
      return
    }
    try {
      const data = await getMyResume()
      setResume(data.hasResume ? data : null)
    } catch {
      setResume(null)
    }
  }, [])

  useDidShow(() => {
    setTabBarIndex(0)
    void loadResume()
  })

  const handleSubmit = async () => {
    const trimmed = text.trim()
    if (trimmed.length < MIN_LENGTH) {
      Taro.showToast({ title: `至少输入 ${MIN_LENGTH} 字`, icon: 'none' })
      return
    }

    setLoading(true)
    try {
      setInput(trimmed, count)
      const result = await createSession(trimmed, count)
      setSession(result.sessionId)
      Taro.navigateTo({ url: '/pages/generating/index' })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '生成失败',
        icon: 'none',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCountChange = (delta: number) => {
    setCount((prev) => Math.min(10, Math.max(5, prev + delta)))
  }

  const handleResume = async () => {
    if (!resume?.sessionId) return
    try {
      setSession(resume.sessionId)
      const detail = await getSession(resume.sessionId)
      setSessionDetail(detail)
      if (detail.status === 'ready') {
        Taro.navigateTo({ url: '/pages/quiz/index' })
      } else if (detail.status === 'processing') {
        Taro.navigateTo({ url: '/pages/generating/index' })
      }
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '恢复失败',
        icon: 'none',
      })
    }
  }

  return (
    <View className='input-page paper-texture page-flex-col'>
      <View
        className='input-top blackboard comic-border'
        style={{ paddingTop: `${STATUS_BAR_HEIGHT + 10}px` }}
      >
        <Text className='input-menu'>☰</Text>
        <Text className='input-title font-comic'>知识闯关</Text>
        <Text className='input-badge font-body'>怕踢分校</Text>
      </View>

      <View className='page-scroll input-scroll'>
        {isLoggedIn && resume && (
          <View className='input-resume-block'>
            <View className='input-resume-head'>
              <Text className='input-resume-title'>继续上次</Text>
            </View>
            <View className='input-resume-card' onClick={() => void handleResume()}>
              <View className='input-resume-icon'>+</View>
              <View className='input-resume-main'>
                <Text className='input-resume-name'>{resume.title}</Text>
                <Text className='input-resume-meta'>
                  {resume.updatedAtDisplay}
                  {resume.type === 'in_progress'
                    ? ` · 完成 ${resume.answeredCount}/${resume.totalQuestions} 题`
                    : ' · 最近完成'}
                </Text>
              </View>
              {resume.accuracy != null && (
                <Text className='input-resume-badge'>{resume.accuracy}%</Text>
              )}
            </View>
          </View>
        )}

        <View className='input-tip-row'>
          <Mascot variant='mini' />
          <View className='bubble input-tip font-body'>
            <Text>把笔记贴上来，本衰帮你出题！</Text>
            <Text className='input-tip-sub'>（臭豆腐味优先）</Text>
          </View>
        </View>

        <View className='comic-panel input-editor'>
          <View className='tape input-tape' />
          <View className='input-editor-head font-body'>
            <Text>📝 作业纸模式</Text>
            <Text className='input-char-count'>
              {text.length} / {MAX_LENGTH} 字
            </Text>
          </View>
          <Textarea
            className='input-textarea lined-paper margin-line font-body'
            value={text}
            maxlength={MAX_LENGTH}
            placeholder='粘贴你的学习笔记，例如：赤壁之战发生于208年…'
            placeholderClass='input-placeholder'
            onInput={(e) => setText(e.detail.value)}
          />
        </View>

        <View className='comic-panel input-count-panel'>
          <View className='input-count-head'>
            <Text className='font-comic input-count-label'>出题数量</Text>
            <Text className='font-body input-count-range'>5 ~ 10 题</Text>
          </View>
          <View className='input-count-row'>
            <Button
              className='count-btn comic-border comic-btn font-comic'
              onClick={() => handleCountChange(-1)}
            >
              −
            </Button>
            <View className='input-count-value-wrap'>
              <Text className='input-count-value font-comic'>{count}</Text>
              <Text className='input-count-default font-body'>默认</Text>
            </View>
            <Button
              className='count-btn comic-border comic-btn font-comic'
              onClick={() => handleCountChange(1)}
            >
              +
            </Button>
          </View>
        </View>
      </View>

      <View className='page-footer input-footer'>
        <Button
          className='comic-btn comic-btn--press input-submit font-comic'
          loading={loading}
          disabled={loading}
          onClick={handleSubmit}
        >
          让 AI 出题！ ▶
        </Button>
        <Text className='input-footer-note font-body'>答完可在「我的」查看记录</Text>
      </View>
    </View>
  )
}
