import { useEffect, useState } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'

import { Mascot } from '@/components/Mascot'
import { getSession } from '@/services/api'
import { useSessionStore } from '@/stores/sessionStore'
import './index.scss'

const STEPS = ['清洗原文', '提取知识点…', '生成题目', '结构校验']

export default function GeneratingPage() {
  const { sessionId, questionCount, setSessionDetail } = useSessionStore()
  const [activeStep, setActiveStep] = useState(1)
  const [error, setError] = useState('')

  useDidShow(() => {
    if (!sessionId) {
      Taro.switchTab({ url: '/pages/input/index' })
    }
  })

  useEffect(() => {
    if (!sessionId) return

    let cancelled = false
    let stepIndex = 1

    const stepTimer = setInterval(() => {
      stepIndex = Math.min(stepIndex + 1, STEPS.length - 1)
      setActiveStep(stepIndex)
    }, 1200)

    const poll = async () => {
      try {
        const detail = await getSession(sessionId)
        if (cancelled) return

        if (detail.status === 'ready') {
          setSessionDetail(detail)
          clearInterval(stepTimer)
          Taro.redirectTo({ url: '/pages/quiz/index' })
          return
        }

        if (detail.status === 'failed') {
          clearInterval(stepTimer)
          setError(detail.errorMessage || '生成失败，请重试')
          return
        }

        setTimeout(poll, 1500)
      } catch (err) {
        if (cancelled) return
        clearInterval(stepTimer)
        setError(err instanceof Error ? err.message : '网络异常')
      }
    }

    poll()

    return () => {
      cancelled = true
      clearInterval(stepTimer)
    }
  }, [sessionId, setSessionDetail])

  const getStepLabel = (index: number) => {
    if (index === 2) return `生成 ${questionCount} 道题`
    return STEPS[index]
  }

  return (
    <View className='generating-page paper-texture page-flex-col'>
      <View className='generating-center'>
        <View className='generating-spinner-wrap'>
          <View className='generating-ring generating-ring--bg' />
          <View className='generating-ring generating-ring--fg' />
          <View className='generating-mascot-center'>
            <Mascot variant='sleep' className='generating-mascot-wiggle' />
          </View>
        </View>

        <Text className='generating-title font-comic'>学霸模式启动中…</Text>
        <Text className='generating-subtitle font-body'>阿…啊不，正在抽知识点</Text>

        <View className='generating-steps'>
          {STEPS.map((_, index) => (
            <View
              key={index}
              className={`generating-step ${index <= activeStep ? 'generating-step--on' : ''} ${
                index < activeStep ? '' : index > activeStep ? 'generating-step--dim' : ''
              }`}
            >
              <View
                className={`step-dot ${
                  index < activeStep ? 'step-dot--done' : index === activeStep ? 'step-dot--active' : ''
                }`}
              >
                {index < activeStep ? '✓' : index === activeStep ? '●' : ''}
              </View>
              <Text
                className={`font-body generating-step-text ${
                  index === activeStep ? 'generating-step-text--active font-comic' : ''
                }`}
              >
                {getStepLabel(index)}
              </Text>
            </View>
          ))}
        </View>

        {error ? (
          <View className='generating-error-wrap'>
            <Text className='generating-error font-body'>{error}</Text>
            <Button
              className='comic-btn comic-btn--press generating-back-btn font-comic'
              onClick={() => Taro.switchTab({ url: '/pages/input/index' })}
            >
              返回重新输入
            </Button>
          </View>
        ) : (
          <>
            <Text className='generating-hint font-body'>预计还需 12 秒</Text>
            <Text
              className='generating-back-link font-body'
              onClick={() => Taro.switchTab({ url: '/pages/input/index' })}
            >
              返回重新输入
            </Text>
          </>
        )}
      </View>
    </View>
  )
}
