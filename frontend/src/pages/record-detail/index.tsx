import { useEffect, useState } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useDidShow, useRouter } from '@tarojs/taro'

import { getMyRecordDetail, practiceQuestionSet } from '@/services/userApi'
import { useSessionStore } from '@/stores/sessionStore'
import type { StudyRecordDetail } from '@/types/user'
import './index.scss'

export default function RecordDetailPage() {
  const router = useRouter()
  const recordId = router.params.id || ''
  const { setSession } = useSessionStore()
  const [detail, setDetail] = useState<StudyRecordDetail | null>(null)

  useDidShow(() => {
    Taro.hideTabBar({ animation: false }).catch(() => undefined)
  })

  useEffect(() => {
    return () => {
      Taro.showTabBar({ animation: false }).catch(() => undefined)
    }
  }, [])

  useEffect(() => {
    if (!recordId) return
    void getMyRecordDetail(recordId)
      .then(setDetail)
      .catch((error) => {
        Taro.showToast({
          title: error instanceof Error ? error.message : '加载失败',
          icon: 'none',
        })
      })
  }, [recordId])

  const handleBack = () => {
    Taro.navigateBack()
  }

  const handlePractice = async () => {
    if (!detail) return
    try {
      const result = await practiceQuestionSet(detail.questionSetId)
      setSession(result.sessionId)
      Taro.navigateTo({ url: '/pages/quiz/index' })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '启动失败',
        icon: 'none',
      })
    }
  }

  if (!detail) {
    return <View className='record-detail-page' />
  }

  return (
    <View className='record-detail-page'>
      <View className='record-detail-header'>
        <View className='record-detail-back' onClick={handleBack}>
          <Text>{'<'}</Text>
        </View>
        <Text className='record-detail-title'>学习详情</Text>
      </View>

      <View className='record-detail-scroll'>
        <View className='tab02-card record-detail-summary'>
          <Text className='record-detail-subtitle'>{detail.title}</Text>
          <Text className='tab02-display record-detail-percent'>{detail.accuracy}%</Text>
          <Text className='record-detail-meta'>
            答对 {detail.correctCount} / {detail.totalQuestions} 题 · 用时 {detail.durationDisplay}
          </Text>
          <Text className='record-detail-time'>{detail.finishedAtDisplay}</Text>
        </View>

        <View className='tab02-card record-detail-section'>
          <Text className='record-detail-section-title'>
            错题（{detail.wrongQuestions.length}）
          </Text>
          {detail.wrongQuestions.length === 0 ? (
            <Text className='record-detail-empty'>本次无错题</Text>
          ) : (
            detail.wrongQuestions.map((item, index) => (
              <View key={item.questionId} className='record-detail-wrong'>
                <Text className='record-detail-wrong-stem'>
                  Q{index + 1} · {item.stem}
                </Text>
                <Text className='record-detail-wrong-answer'>
                  你的答案：{item.selectedAnswer} · 正确答案：{item.correctAnswer}
                </Text>
              </View>
            ))
          )}
        </View>

        <View className='tab02-card record-detail-section'>
          <Text className='record-detail-ai-title'>AI 总结</Text>
          <Text className='record-detail-ai-text'>{detail.summary}</Text>
        </View>

        <View className='record-detail-actions'>
          <Button className='tab02-btn-primary record-detail-btn-primary' onClick={() => void handlePractice()}>
            再练一次
          </Button>
          <Button className='record-detail-btn-p1' onClick={() => Taro.showToast({ title: '错题强化（P1 敬请期待）', icon: 'none' })}>
            加入错题强化 · P1
          </Button>
        </View>
      </View>
    </View>
  )
}
