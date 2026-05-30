export interface UserProfile {
  id: string
  nickname: string
  avatarUrl?: string | null
  createdAt?: string
  isNewUser?: boolean
}

export interface UserStats {
  totalSessions: number
  averageAccuracy: number
  totalDurationSeconds: number
  totalDurationDisplay: string
}

export interface StudyRecordItem {
  id: string
  title: string
  subjectIcon: string
  finishedAt: string
  finishedAtDisplay: string
  durationSeconds: number
  durationDisplay: string
  accuracy: number
  correctCount: number
  totalQuestions: number
}

export interface PaginatedRecords {
  items: StudyRecordItem[]
  total: number
  page: number
  pageSize: number
}

export interface WrongQuestionItem {
  questionId: string
  stem: string
  selectedAnswer: string
  correctAnswer: string
}

export interface StudyRecordDetail {
  id: string
  title: string
  accuracy: number
  correctCount: number
  totalQuestions: number
  durationSeconds: number
  durationDisplay: string
  finishedAt: string
  finishedAtDisplay: string
  wrongQuestions: WrongQuestionItem[]
  summary: string
  questionSetId: string
}

export interface QuestionSetItem {
  id: string
  title: string
  questionCount: number
  typeLabel: string
  createdAt: string
  createdAtDisplay: string
  practiceStatus: 'unpracticed' | 'practiced'
  lastAccuracy?: number | null
  badge: string
}

export interface PaginatedQuestionSets {
  items: QuestionSetItem[]
  total: number
  page: number
  pageSize: number
}

export interface QuestionPreview {
  id: string
  type: string
  stem: string
  options: string[]
}

export interface QuestionSetDetail {
  id: string
  title: string
  questions: QuestionPreview[]
}

export interface ResumeInfo {
  hasResume: boolean
  type: 'in_progress' | 'last_completed' | 'none'
  sessionId?: string
  title?: string
  answeredCount?: number
  totalQuestions?: number
  accuracy?: number
  updatedAtDisplay?: string
}

export interface LoginResponse {
  token: string
  expiresIn: number
  user: UserProfile
}
