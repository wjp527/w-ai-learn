export type SessionStatus = 'processing' | 'ready' | 'failed'
export type QuestionType = 'single_choice' | 'true_false'

export interface KnowledgePoint {
  id: string
  title: string
  description: string
  sourceEvidence: string
}

export interface Question {
  id: string
  type: QuestionType
  stem: string
  options: string[]
  correctAnswer: string
  explanation: string
  sourceEvidence: string
}

export interface SessionDetail {
  sessionId: string
  status: SessionStatus
  knowledgePoints: KnowledgePoint[]
  questions: Question[]
  errorMessage?: string | null
}

export interface SubmitAnswerResult {
  isCorrect: boolean
  correctAnswer: string
  explanation: string
  sourceEvidence: string
}

export interface StudyReport {
  accuracy: number
  totalQuestions: number
  correctCount: number
  wrongQuestions: Array<{
    questionId: string
    stem: string
    selectedAnswer: string
    correctAnswer: string
  }>
  weakPoints: string[]
  summary: string
  durationSeconds: number
}
