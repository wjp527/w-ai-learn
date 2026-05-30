import { View, Text, Button } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'

import { Mascot } from '@/components/Mascot'
import { useAuthStore } from '@/stores/authStore'
import { useSessionStore } from '@/stores/sessionStore'
import './index.scss'

function formatDuration(seconds: number) {
  const minutes = Math.floor(seconds / 60)
  const remain = seconds % 60
  if (minutes <= 0) return `${remain} 秒`
  return `${minutes} 分 ${remain} 秒`
}

function getGradeMeta(accuracy: number) {
  if (accuracy >= 90) {
    return { label: '学霸附体', tone: 'ace' as const, emoji: '🏆' }
  }
  if (accuracy >= 75) {
    return { label: '及格万岁', tone: 'pass' as const, emoji: '🎉' }
  }
  if (accuracy >= 60) {
    return { label: '勉强过关', tone: 'ok' as const, emoji: '😮‍💨' }
  }
  return { label: '又翻车了', tone: 'fail' as const, emoji: '💥' }
}

export default function ReportPage() {
  const { isLoggedIn } = useAuthStore()
  const { report, resetQuizFlow } = useSessionStore()

  useDidShow(() => {
    if (!report) {
      Taro.switchTab({ url: '/pages/input/index' })
    }
  })

  if (!report) {
    return <View className='report-page paper-texture page-flex-col' />
  }

  const grade = getGradeMeta(report.accuracy)
  const wrongCount = report.wrongQuestions.length
  const isPerfect = wrongCount === 0

  const handleRestart = () => {
    resetQuizFlow()
    Taro.switchTab({ url: '/pages/input/index' })
  }

  const handleGoProfile = () => {
    Taro.switchTab({ url: '/pages/profile/index' })
  }

  const handleShare = () => {
    Taro.showToast({ title: '分享战绩（V1 敬请期待）', icon: 'none' })
  }

  return (
    <View className='report-page paper-texture page-flex-col'>
      <View className='report-header'>
        <View className='tape report-tape' />
        <Text className='font-comic report-title'>本轮成绩单</Text>
        {isLoggedIn ? (
          <Text className='report-saved-note'>答完啦，记录已保存</Text>
        ) : (
          <Text className='report-saved-note report-saved-note--guest'>登录后可保存学习记录</Text>
        )}
        <Text className='font-chalk report-subtitle'>帕踢中学教务处（盖章无效）</Text>
      </View>

      <View className='page-scroll report-scroll'>
        {isLoggedIn && (
          <View className='report-save-banner'>
            <Mascot variant='mini' className='report-save-mascot' />
            <Text className='report-save-text font-body'>
              完整错题和薄弱点已存入「我的 → 学习记录」，随时可回看。
            </Text>
          </View>
        )}
        <View className={`report-hero blackboard report-hero--${grade.tone}`}>
          <Text className={`stamp report-grade-stamp report-grade-stamp--${grade.tone}`}>
            {grade.label}
          </Text>

          <View className='report-hero-main'>
            <View className='report-hero-score'>
              <Text className='font-comic report-hero-percent'>{report.accuracy}%</Text>
              <Text className='report-hero-label font-body'>正确率</Text>
            </View>
            <View className='report-hero-divider' />
            <View className='report-hero-score'>
              <Text className='font-comic report-hero-count'>
                {report.correctCount}
                <Text className='report-hero-total'>/{report.totalQuestions}</Text>
              </Text>
              <Text className='report-hero-label font-body'>答对题数</Text>
            </View>
          </View>

          <View className='report-hero-bar'>
            <View className='report-hero-bar-fill' style={{ width: `${report.accuracy}%` }} />
          </View>

          <View className='report-hero-meta'>
            <Text className='report-hero-emoji'>{grade.emoji}</Text>
            <Text className='report-hero-duration font-body'>
              本次学习 {formatDuration(report.durationSeconds)}
            </Text>
          </View>
        </View>

        <View className='comic-panel report-section'>
          <View className='report-section-head'>
            <Text className='report-section-icon report-section-icon--warn'>!</Text>
            <Text className='font-comic report-section-title'>薄弱知识点</Text>
          </View>
          <View className='report-tags'>
            {report.weakPoints.length > 0 ? (
              report.weakPoints.map((point, index) => (
                <View key={`${point}-${index}`} className='report-tag font-body'>
                  <Text className='report-tag-index font-comic'>{index + 1}</Text>
                  <Text className='report-tag-text'>{point}</Text>
                </View>
              ))
            ) : (
              <Text className='report-empty font-body'>这次没翻车，薄弱点空空如也</Text>
            )}
          </View>
        </View>

        <View className='comic-panel report-section'>
          <View className='report-section-head'>
            <Text className='report-section-icon'>✎</Text>
            <Text className='font-comic report-section-title'>
              错题清单
              <Text className='report-section-count'>（{wrongCount} 道）</Text>
            </Text>
          </View>

          {isPerfect ? (
            <View className='report-perfect'>
              <Text className='report-perfect-emoji'>✨</Text>
              <Text className='report-perfect-text font-comic'>全对！这次没翻车</Text>
            </View>
          ) : (
            report.wrongQuestions.map((item, index) => (
              <View key={item.questionId} className='report-wrong-card'>
                <View className='report-wrong-head'>
                  <Text className='wrong-badge font-comic'>第 {index + 1} 题</Text>
                </View>
                <Text className='report-wrong-stem font-body'>{item.stem}</Text>
                <View className='report-wrong-answers'>
                  <View className='report-answer-row report-answer-row--wrong'>
                    <Text className='report-answer-label font-comic'>你选的</Text>
                    <Text className='report-answer-value font-body'>{item.selectedAnswer}</Text>
                  </View>
                  <View className='report-answer-row report-answer-row--right'>
                    <Text className='report-answer-label font-comic'>正确答案</Text>
                    <Text className='report-answer-value font-body'>{item.correctAnswer}</Text>
                  </View>
                </View>
              </View>
            ))
          )}
        </View>

        <View className='report-summary-wrap'>
          <Mascot variant='mini' className='report-mascot' />
          <View className='bubble report-summary font-body'>
            <Text className='font-comic report-summary-title'>AI 总结</Text>
            <Text className='report-summary-text'>{report.summary}</Text>
          </View>
        </View>
      </View>

      <View className='page-footer report-footer'>
        <Button
          className='comic-btn comic-btn--press report-btn report-btn--primary font-comic'
          onClick={handleRestart}
        >
          再来一局
        </Button>
        <Button
          className='comic-btn comic-btn--press report-btn report-btn--secondary font-comic'
          onClick={handleGoProfile}
        >
          去「我的」查看记录
        </Button>
        <Button className='share-ghost report-share font-comic' onClick={handleShare}>
          分享战绩（V1 敬请期待）
        </Button>
      </View>
    </View>
  )
}
