import { View, Text, Button } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'

import { Mascot } from '@/components/Mascot'
import { getReport, submitAnswer } from '@/services/api'
import { getCurrentQuestion, useSessionStore } from '@/stores/sessionStore'
import './index.scss'

const OPTION_LETTERS = ['A', 'B', 'C', 'D']

export default function QuizPage() {
  const {
    sessionId,
    sessionDetail,
    currentIndex,
    selectedAnswer,
    feedback,
    setSelectedAnswer,
    setFeedback,
    setCurrentIndex,
    setReport,
    markQuizStarted,
  } = useSessionStore()

  const questions = sessionDetail?.questions || []
  const question = getCurrentQuestion(useSessionStore.getState())
  const total = questions.length
  const progress = total ? ((currentIndex + 1) / total) * 100 : 0

  useDidShow(() => {
    if (!sessionId || !sessionDetail?.questions?.length) {
      Taro.switchTab({ url: '/pages/input/index' })
    }
  })

  const handleSubmit = async () => {
    if (!question || !selectedAnswer || !sessionId) return
    markQuizStarted()
    try {
      const result = await submitAnswer(sessionId, question.id, selectedAnswer)
      setFeedback(result)
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '提交失败',
        icon: 'none',
      })
    }
  }

  const handleNext = async () => {
    if (!sessionId) return
    if (currentIndex < total - 1) {
      setCurrentIndex(currentIndex + 1)
      return
    }
    try {
      const report = await getReport(sessionId)
      setReport(report)
      Taro.redirectTo({ url: '/pages/report/index' })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '报告生成失败',
        icon: 'none',
      })
    }
  }

  if (!question) {
    return <View className='quiz-page paper-texture' />
  }

  const isTrueFalse = question.type === 'true_false'
  const isCorrect = feedback?.isCorrect
  const showFeedback = Boolean(feedback)

  return (
    <View
      className={`quiz-page paper-texture page-flex-col ${showFeedback && !isCorrect ? 'quiz-page--wrong' : ''}`}
    >
      {showFeedback && isCorrect && (
        <View className='quiz-confetti'>
          <View className='confetti-piece confetti-piece--1' />
          <View className='confetti-piece confetti-piece--2' />
          <View className='confetti-piece confetti-piece--3' />
          <View className='confetti-piece confetti-piece--4' />
        </View>
      )}

      {showFeedback && !isCorrect && <View className='quiz-speed-lines' />}

      <View className='quiz-head'>
        <View className='quiz-head-row'>
          <Text className='font-comic quiz-index'>第 {currentIndex + 1} 题</Text>
          {showFeedback && isCorrect && (
            <Text className='font-comic quiz-badge-ok pop-in'>✓ 牛啊！</Text>
          )}
          {showFeedback && !isCorrect && <Text className='stamp quiz-stamp'>又翻车了</Text>}
          {!showFeedback && (
            <Text
              className={`quiz-type-badge font-body ${isTrueFalse ? 'quiz-type-badge--tf' : 'quiz-type-badge--sc'}`}
            >
              {isTrueFalse ? '判断' : '单选'}
            </Text>
          )}
        </View>
        <View className='chalk-bar'>
          <View className='chalk-fill' style={{ width: `${progress}%` }} />
        </View>
        {!showFeedback && (
          <Text className='quiz-progress-text font-body'>
            {currentIndex + 1} / {total}
          </Text>
        )}
      </View>

      <View className='page-scroll quiz-body'>
        <View className='comic-panel quiz-stem-panel'>
          {!isTrueFalse && !showFeedback && (
            <Text className='quiz-quest-label font-comic'>QUEST</Text>
          )}
          <Text className='quiz-stem font-body'>{question.stem}</Text>
        </View>

        {!showFeedback && isTrueFalse && (
          <View className='quiz-tf-col'>
            <View className='quiz-tf-grid'>
              <Button
                className={`comic-btn comic-btn--press quiz-tf-btn quiz-tf-btn--yes font-comic ${
                  selectedAnswer === '对' ? 'quiz-tf-btn--selected' : ''
                }`}
                onClick={() => setSelectedAnswer('对')}
              >
                <Text className='quiz-tf-icon'>✓</Text>
                <Text className='quiz-tf-label font-body'>对</Text>
              </Button>
              <Button
                className={`comic-btn comic-btn--press quiz-tf-btn quiz-tf-btn--no font-comic ${
                  selectedAnswer === '错' ? 'quiz-tf-btn--selected' : ''
                }`}
                onClick={() => setSelectedAnswer('错')}
              >
                <Text className='quiz-tf-icon quiz-tf-icon--wrong'>✗</Text>
                <Text className='quiz-tf-label font-body'>错</Text>
              </Button>
            </View>
            <Text className='quiz-tf-hint font-body'>点一下，别犹豫（犹豫会 0 分）</Text>
          </View>
        )}

        {!showFeedback && !isTrueFalse && (
          <View className='quiz-options'>
            {question.options.map((option, index) => (
              <View
                key={option}
                className={`comic-panel quiz-option font-body ${
                  selectedAnswer === option ? 'option-selected' : ''
                }`}
                onClick={() => setSelectedAnswer(option)}
              >
                <Text className={`opt-letter ${selectedAnswer === option ? 'opt-letter--hoody' : ''}`}>
                  {OPTION_LETTERS[index]}
                </Text>
                <Text>{option}</Text>
              </View>
            ))}
          </View>
        )}

        {showFeedback && (
          <View className='quiz-feedback'>
            {!isTrueFalse && (
              <View
                className={`comic-panel quiz-answer-card ${
                  isCorrect ? 'quiz-answer-card--correct' : ''
                }`}
              >
                <Text className={`opt-letter ${isCorrect ? 'opt-letter--board' : 'opt-letter--wrong'}`}>
                  {OPTION_LETTERS[question.options.indexOf(feedback!.correctAnswer)] || 'A'}
                </Text>
                <Text className='font-body'>
                  {feedback!.correctAnswer} {isCorrect ? '✓' : ''}
                </Text>
              </View>
            )}

            {showFeedback && !isCorrect && !isTrueFalse && selectedAnswer && (
              <View className='comic-panel quiz-answer-card quiz-answer-card--wrong-pick wiggle'>
                <Text className='opt-letter opt-letter--wrong'>
                  {OPTION_LETTERS[question.options.indexOf(selectedAnswer)] || '?'}
                </Text>
                <Text className='font-body'>
                  {selectedAnswer} ✗ <Text className='quiz-you-pick'>你选的</Text>
                </Text>
              </View>
            )}

            {showFeedback && !isCorrect && isTrueFalse && selectedAnswer && (
              <View className='comic-panel quiz-answer-card quiz-answer-card--wrong-pick wiggle'>
                <Text className='font-body'>
                  {selectedAnswer} ✗ <Text className='quiz-you-pick'>你选的</Text>
                </Text>
              </View>
            )}

            {showFeedback && !isCorrect && (
              <View className='comic-panel quiz-answer-card quiz-answer-card--correct-reveal'>
                <Text className='opt-letter opt-letter--board'>✓</Text>
                <Text className='font-body'>
                  {feedback!.correctAnswer}{' '}
                  <Text className='quiz-correct-tag'>正确答案</Text>
                </Text>
              </View>
            )}

            {isCorrect && (
              <Text className='quiz-celebrate font-comic pop-in'>🎉 答对了！+1 衰力值</Text>
            )}

            <View className='quiz-explain-row'>
              {isCorrect ? (
                <Mascot variant='mini' />
              ) : (
                <View className='quiz-emoji-face'>😅</View>
              )}
              <View className='bubble quiz-explain font-body'>
                <Text className={`quiz-explain-title font-comic ${isCorrect ? 'quiz-explain-title--ok' : 'quiz-explain-title--bad'}`}>
                  AI 讲解
                </Text>
                <Text className='quiz-explain-text'>{feedback!.explanation}</Text>
              </View>
            </View>

            {feedback!.sourceEvidence ? (
              <View className='comic-panel quiz-source-panel'>
                <Text className='quiz-source-title font-comic'>原文依据</Text>
                <Text className='quiz-source-text font-body'>{feedback!.sourceEvidence}</Text>
              </View>
            ) : null}
          </View>
        )}
      </View>

      <View className='page-footer quiz-footer'>
        {!showFeedback ? (
          <Button
            className='comic-btn comic-btn--press quiz-submit font-comic'
            disabled={!selectedAnswer}
            onClick={handleSubmit}
          >
            提交答案
          </Button>
        ) : (
          <Button
            className={`comic-btn comic-btn--press quiz-next font-comic ${
              isCorrect ? 'quiz-next--ok' : 'quiz-next--bad'
            }`}
            onClick={handleNext}
          >
            {currentIndex >= total - 1
              ? '查看报告 →'
              : isCorrect
                ? '下一关 →'
                : '下一关 → 别怂'}
          </Button>
        )}
      </View>
    </View>
  )
}
