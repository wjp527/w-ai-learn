import { useCallback, useState } from 'react'
import { View, Text, Button } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'

import { Mascot } from '@/components/Mascot'
import {
  getMyQuestionSetDetail,
  getMyQuestionSets,
  practiceQuestionSet,
} from '@/services/userApi'
import { useAuthStore } from '@/stores/authStore'
import { useSessionStore } from '@/stores/sessionStore'
import type { QuestionSetItem } from '@/types/user'
import { setTabBarIndex } from '@/utils/tabBar'
import './index.scss'

const FILTERS = ['全部', '语文', '历史', '英语']

function showP1Toast(feature: string) {
  Taro.showToast({ title: `${feature}（P1 敬请期待）`, icon: 'none' })
}

export default function QuestionBankPage() {
  const { isLoggedIn, silentLogin } = useAuthStore()
  const { setSession } = useSessionStore()
  const [activeFilter, setActiveFilter] = useState(0)
  const [sets, setSets] = useState<QuestionSetItem[]>([])
  const [previewTitle, setPreviewTitle] = useState('')
  const [previewQuestions, setPreviewQuestions] = useState<
    { id: string; stem: string; options: string[] }[]
  >([])
  const [showPreview, setShowPreview] = useState(false)

  const loadSets = useCallback(async () => {
    if (!useAuthStore.getState().isLoggedIn) {
      setSets([])
      return
    }
    try {
      const data = await getMyQuestionSets()
      setSets(data.items)
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '加载失败',
        icon: 'none',
      })
    }
  }, [])

  useDidShow(() => {
    setTabBarIndex(1)
    void loadSets()
  })

  const handleFilterClick = (index: number) => {
    setActiveFilter(index)
    if (index > 0) {
      showP1Toast('学科筛选')
    }
  }

  const startPractice = async (questionSetId: string) => {
    try {
      const result = await practiceQuestionSet(questionSetId)
      setSession(result.sessionId)
      Taro.navigateTo({ url: '/pages/quiz/index' })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '启动失败',
        icon: 'none',
      })
    }
  }

  const handlePreview = async (questionSetId: string, title: string) => {
    try {
      const detail = await getMyQuestionSetDetail(questionSetId)
      setPreviewTitle(title)
      setPreviewQuestions(detail.questions)
      setShowPreview(true)
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '加载失败',
        icon: 'none',
      })
    }
  }

  return (
    <View className='tab02-page qb-page'>
      <View className='qb-header'>
        <Text className='tab02-display qb-title'>我的题库</Text>
        <Text className='qb-desc'>AI 根据你的笔记生成的题目集</Text>
      </View>

      <View className='qb-filters'>
        {FILTERS.map((label, index) => (
          <Text
            key={label}
            className={`tab02-filter ${activeFilter === index ? 'tab02-filter--active' : ''}`}
            onClick={() => handleFilterClick(index)}
          >
            {label}
          </Text>
        ))}
      </View>

      <View className='tab02-scroll qb-list'>
        {!isLoggedIn && (
          <View className='tab02-card qb-empty-card'>
            <Mascot variant='mini' />
            <View className='qb-p1-text'>
              <Text className='tab02-display'>登录后同步题库</Text>
              <Text className='qb-p1-desc'>完成闯关后，题目集会出现在这里</Text>
              <Button className='qb-login-btn' onClick={() => void silentLogin().then(loadSets)}>
                微信登录
              </Button>
            </View>
          </View>
        )}

        {isLoggedIn && sets.length === 0 && (
          <View className='tab02-card qb-empty-card'>
            <Mascot variant='mini' />
            <View className='qb-p1-text'>
              <Text className='tab02-display'>还没有题目集</Text>
              <Text className='qb-p1-desc'>完成一次闯关后会自动生成</Text>
            </View>
          </View>
        )}

        {sets.map((item) => (
          <View key={item.id} className='tab02-card qb-card'>
            <View className='qb-card-head'>
              <View className='qb-card-info'>
                <Text className='qb-card-title'>{item.title}</Text>
                <Text className='qb-card-meta'>
                  {item.questionCount} 道题 · {item.typeLabel} · {item.createdAtDisplay}
                </Text>
              </View>
              {item.badge === '未练习' ? (
                <Text className='qb-badge-muted'>{item.badge}</Text>
              ) : item.badge === '已练过' ? (
                <Text className='tab02-badge tab02-badge--ok'>{item.badge}</Text>
              ) : (
                <Text className='tab02-badge tab02-badge--warn'>{item.badge}</Text>
              )}
            </View>

            {item.practiceStatus === 'practiced' ? (
              <View className='qb-card-actions'>
                <Button className='qb-btn-green' onClick={() => void startPractice(item.id)}>
                  再练一次
                </Button>
                <Button className='qb-btn-outline' onClick={() => void handlePreview(item.id, item.title)}>
                  查看题目
                </Button>
              </View>
            ) : (
              <Button className='qb-btn-orange-full' onClick={() => void startPractice(item.id)}>
                开始闯关
              </Button>
            )}
          </View>
        ))}
      </View>

      {showPreview && (
        <View className='qb-preview-mask' onClick={() => setShowPreview(false)}>
          <View className='qb-preview-panel' onClick={(e) => e.stopPropagation()}>
            <Text className='qb-preview-title'>{previewTitle}</Text>
            {previewQuestions.map((q, index) => (
              <View key={q.id} className='qb-preview-item'>
                <Text className='qb-preview-stem'>
                  Q{index + 1} · {q.stem}
                </Text>
                <Text className='qb-preview-options'>{q.options.join(' · ')}</Text>
              </View>
            ))}
            <Button className='qb-preview-close' onClick={() => setShowPreview(false)}>
              关闭
            </Button>
          </View>
        </View>
      )}
    </View>
  )
}
