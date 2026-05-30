import { useCallback, useState } from 'react'
import { View, Text, Button, Image, Input } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'

import { Mascot } from '@/components/Mascot'
import { getMyRecords, getMyStats } from '@/services/userApi'
import { useAuthStore } from '@/stores/authStore'
import type { StudyRecordItem, UserStats } from '@/types/user'
import { setTabBarIndex } from '@/utils/tabBar'
import './index.scss'

const MENU_ITEMS = [
  { label: '错题本', hint: 'P1 →', p1: true },
  { label: '学习设置', hint: '→', p1: false },
  { label: '关于 / 反馈', hint: '→', p1: false, muted: true },
]

function showP1Toast(feature: string) {
  Taro.showToast({ title: `${feature}（P1 敬请期待）`, icon: 'none' })
}

function getSubjectClass(icon: string) {
  if (icon === '英') return 'english'
  if (icon === '数') return 'math'
  return 'history'
}

export default function ProfilePage() {
  const { isLoggedIn, user, silentLogin, updateProfile } = useAuthStore()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [records, setRecords] = useState<StudyRecordItem[]>([])
  const [nicknameDraft, setNicknameDraft] = useState('')

  const loadData = useCallback(async () => {
    if (!useAuthStore.getState().isLoggedIn) {
      setStats(null)
      setRecords([])
      return
    }
    try {
      const [statsData, recordsData] = await Promise.all([getMyStats(), getMyRecords(1, 20)])
      setStats(statsData)
      setRecords(recordsData.items)
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '加载失败',
        icon: 'none',
      })
    }
  }, [])

  useDidShow(() => {
    setTabBarIndex(2)
    void loadData()
  })

  const handleLogin = async () => {
    await silentLogin()
    if (useAuthStore.getState().isLoggedIn) {
      await loadData()
    } else {
      Taro.showToast({ title: '登录失败，可匿名闯关', icon: 'none' })
    }
  }

  const handleChooseAvatar = async (e: { detail: { avatarUrl: string } }) => {
    try {
      await updateProfile({ avatarUrl: e.detail.avatarUrl })
      Taro.showToast({ title: '头像已更新', icon: 'success' })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '更新失败',
        icon: 'none',
      })
    }
  }

  const handleNicknameBlur = async () => {
    const trimmed = nicknameDraft.trim()
    if (!trimmed || trimmed === user?.nickname) return
    try {
      await updateProfile({ nickname: trimmed })
      Taro.showToast({ title: '昵称已更新', icon: 'success' })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '更新失败',
        icon: 'none',
      })
    }
  }

  const handleRecordClick = (recordId: string) => {
    Taro.navigateTo({ url: `/pages/record-detail/index?id=${recordId}` })
  }

  return (
    <View className='tab02-page profile-page'>
      <View className='profile-hero'>
        <View className='profile-user'>
          {isLoggedIn ? (
            <Button
              className='profile-avatar-btn'
              openType='chooseAvatar'
              onChooseAvatar={handleChooseAvatar}
            >
              <View className='profile-avatar-wrap'>
                {user?.avatarUrl ? (
                  <Image className='profile-avatar-img' src={user.avatarUrl} mode='aspectFill' />
                ) : (
                  <Mascot variant='mini' className='profile-mascot' />
                )}
              </View>
            </Button>
          ) : (
            <View className='profile-avatar-wrap' onClick={handleLogin}>
              <Mascot variant='mini' className='profile-mascot' />
            </View>
          )}
          <View className='profile-user-info'>
            {isLoggedIn ? (
              <>
                <Input
                  className='tab02-display profile-name profile-name-input'
                  type='nickname'
                  value={nicknameDraft || user?.nickname || ''}
                  placeholder='点击设置昵称'
                  onInput={(e) => setNicknameDraft(e.detail.value)}
                  onBlur={handleNicknameBlur}
                />
                <Text className='profile-note'>
                  累计闯关 {stats?.totalSessions ?? 0} 次
                </Text>
              </>
            ) : (
              <>
                <Text className='tab02-display profile-name' onClick={handleLogin}>
                  点击登录
                </Text>
                <Text className='profile-note'>登录后同步学习记录</Text>
              </>
            )}
          </View>
        </View>

        {isLoggedIn && stats && (
          <View className='profile-stats'>
            <View className='profile-stat-pill'>
              <Text className='profile-stat-num'>{stats.totalSessions}</Text>
              <Text className='profile-stat-label'>闯关次数</Text>
            </View>
            <View className='profile-stat-pill'>
              <Text className='profile-stat-num'>{stats.averageAccuracy}%</Text>
              <Text className='profile-stat-label'>平均正确率</Text>
            </View>
            <View className='profile-stat-pill'>
              <Text className='profile-stat-num'>{stats.totalDurationDisplay}</Text>
              <Text className='profile-stat-label'>学习时长</Text>
            </View>
          </View>
        )}
      </View>

      <View className='tab02-scroll profile-scroll'>
        <View className='tab02-card profile-history-card'>
          <View className='profile-history-head'>
            <Text className='profile-history-title'>学习记录</Text>
            {isLoggedIn && records.length > 0 && (
              <Text
                className='profile-history-all'
                onClick={() => Taro.navigateTo({ url: '/pages/record-list/index' })}
              >
                全部
              </Text>
            )}
          </View>

          {!isLoggedIn && (
            <View className='profile-empty'>
              <Text className='profile-empty-text'>登录后可查看学习记录</Text>
            </View>
          )}

          {isLoggedIn && records.length === 0 && (
            <View className='profile-empty'>
              <Text className='profile-empty-text'>还没有记录，去闯一关吧</Text>
            </View>
          )}

          {records.map((item, index) => (
            <View
              key={item.id}
              className={`profile-history-item ${index < records.length - 1 ? 'profile-history-item--border' : ''}`}
              onClick={() => handleRecordClick(item.id)}
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
                <Text
                  className={`profile-score ${item.accuracy < 70 ? 'profile-score--bad' : ''}`}
                >
                  {item.accuracy}%
                </Text>
                <Text className='profile-progress'>
                  {item.correctCount}/{item.totalQuestions}题
                </Text>
              </View>
            </View>
          ))}
        </View>

        <View className='tab02-card profile-menu'>
          {MENU_ITEMS.map((item) => (
            <View
              key={item.label}
              className='profile-menu-item'
              onClick={() => (item.p1 ? showP1Toast(item.label) : Taro.showToast({ title: '敬请期待', icon: 'none' }))}
            >
              <Text className={item.muted ? 'profile-menu-label--muted' : 'profile-menu-label'}>
                {item.label}
              </Text>
              <Text className='profile-menu-hint'>{item.hint}</Text>
            </View>
          ))}
        </View>

        <Button
          className='tab02-btn-primary profile-start-btn'
          onClick={() => Taro.switchTab({ url: '/pages/input/index' })}
        >
          开始新闯关
        </Button>
      </View>
    </View>
  )
}
