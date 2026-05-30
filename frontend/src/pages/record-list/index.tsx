import { useCallback, useEffect, useState } from 'react'
import { View, Text } from '@tarojs/components'
import Taro, { useDidShow, useReachBottom } from '@tarojs/taro'

import { getMyRecords } from '@/services/userApi'
import type { StudyRecordItem } from '@/types/user'
import '../profile/index.scss'
import './index.scss'

function getSubjectClass(icon: string) {
  if (icon === '英') return 'english'
  if (icon === '数') return 'math'
  return 'history'
}

export default function RecordListPage() {
  const [records, setRecords] = useState<StudyRecordItem[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)

  useDidShow(() => {
    Taro.hideTabBar({ animation: false }).catch(() => undefined)
  })

  useEffect(() => {
    return () => {
      Taro.showTabBar({ animation: false }).catch(() => undefined)
    }
  }, [])

  const loadPage = useCallback(async (pageNum: number, append: boolean) => {
    setLoading(true)
    try {
      const data = await getMyRecords(pageNum, 20)
      setTotal(data.total)
      setPage(pageNum)
      setRecords((prev) => (append ? [...prev, ...data.items] : data.items))
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '加载失败',
        icon: 'none',
      })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadPage(1, false)
  }, [loadPage])

  useReachBottom(() => {
    if (loading || records.length >= total) return
    void loadPage(page + 1, true)
  })

  return (
    <View className='record-list-page'>
      <View className='tab02-scroll record-list-scroll'>
        <View className='tab02-card profile-history-card'>
          {records.map((item, index) => (
            <View
              key={item.id}
              className={`record-list-item profile-history-item ${index < records.length - 1 ? 'record-list-item--border' : ''}`}
              onClick={() => Taro.navigateTo({ url: `/pages/record-detail/index?id=${item.id}` })}
            >
              <View className={`profile-subject profile-subject--${getSubjectClass(item.subjectIcon)}`}>
                <Text>{item.subjectIcon}</Text>
              </View>
              <View className='profile-history-main'>
                <Text className='profile-history-name'>{item.title}</Text>
                <Text className='profile-history-time'>
                  {item.finishedAtDisplay} · 用时 {item.durationDisplay}
                </Text>
              </View>
              <View className='profile-history-score'>
                <Text className={`profile-score ${item.accuracy < 70 ? 'profile-score--bad' : ''}`}>
                  {item.accuracy}%
                </Text>
                <Text className='profile-progress'>
                  {item.correctCount}/{item.totalQuestions}题
                </Text>
              </View>
            </View>
          ))}
          {records.length === 0 && !loading && (
            <View className='profile-empty'>
              <Text className='profile-empty-text'>暂无记录</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  )
}
