import { create } from 'zustand'

import type { Question, SessionDetail, StudyReport } from '@/types/session'

interface SessionState {
  sessionId: string
  sourceText: string
  questionCount: number
  sessionDetail: SessionDetail | null
  currentIndex: number
  selectedAnswer: string
  feedback: {
    isCorrect: boolean
    correctAnswer: string
    explanation: string
    sourceEvidence: string
  } | null
  report: StudyReport | null
  quizStartedAt: number | null
  setInput: (sourceText: string, questionCount: number) => void
  setSession: (sessionId: string, detail?: SessionDetail | null) => void
  setSessionDetail: (detail: SessionDetail) => void
  setCurrentIndex: (index: number) => void
  setSelectedAnswer: (answer: string) => void
  setFeedback: (feedback: SessionState['feedback']) => void
  setReport: (report: StudyReport) => void
  markQuizStarted: () => void
  resetQuizFlow: () => void
  resetAll: () => void
}

const initialState = {
  sessionId: '',
  sourceText: '',
  questionCount: 8,
  sessionDetail: null,
  currentIndex: 0,
  selectedAnswer: '',
  feedback: null,
  report: null,
  quizStartedAt: null,
}

export const useSessionStore = create<SessionState>((set) => ({
  ...initialState,
  setInput: (sourceText, questionCount) => set({ sourceText, questionCount }),
  setSession: (sessionId, detail = null) => set({ sessionId, sessionDetail: detail }),
  setSessionDetail: (detail) => set({ sessionDetail: detail }),
  setCurrentIndex: (index) => set({ currentIndex: index, selectedAnswer: '', feedback: null }),
  setSelectedAnswer: (answer) => set({ selectedAnswer: answer }),
  setFeedback: (feedback) => set({ feedback }),
  setReport: (report) => set({ report }),
  markQuizStarted: () => set({ quizStartedAt: Date.now() }),
  resetQuizFlow: () =>
    set({
      currentIndex: 0,
      selectedAnswer: '',
      feedback: null,
      report: null,
      quizStartedAt: null,
    }),
  resetAll: () => set(initialState),
}))

export function getCurrentQuestion(state: SessionState): Question | null {
  const questions = state.sessionDetail?.questions || []
  return questions[state.currentIndex] || null
}
