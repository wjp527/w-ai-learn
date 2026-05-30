import Taro from '@tarojs/taro'

import { useAuthStore } from '@/stores/authStore'
import type { SessionDetail, StudyReport, SubmitAnswerResult } from '@/types/session'

const API_BASE = 'http://127.0.0.1:8002'

async function request<T>(path: string, options: Taro.request.Option = { url: '' }): Promise<T> {
  const token = useAuthStore.getState().token
  const response = await Taro.request({
    ...options,
    url: `${API_BASE}${path}`,
    header: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.header || {}),
    },
  })

  if (response.statusCode === 401) {
    useAuthStore.getState().logout()
  }

  if (response.statusCode >= 400) {
    const detail = (response.data as { detail?: string })?.detail || '请求失败'
    throw new Error(detail)
  }

  return response.data as T
}

export async function createSession(sourceText: string, questionCount: number) {
  return request<{ sessionId: string; status: string }>('/sessions', {
    url: '/sessions',
    method: 'POST',
    data: { sourceText, questionCount },
  })
}

export async function getSession(sessionId: string) {
  return request<SessionDetail>(`/sessions/${sessionId}`, {
    url: `/sessions/${sessionId}`,
    method: 'GET',
  })
}

export async function submitAnswer(sessionId: string, questionId: string, selectedAnswer: string) {
  return request<SubmitAnswerResult>(`/sessions/${sessionId}/answers`, {
    url: `/sessions/${sessionId}/answers`,
    method: 'POST',
    data: { questionId, selectedAnswer },
  })
}

export async function getReport(sessionId: string) {
  return request<StudyReport>(`/sessions/${sessionId}/report`, {
    url: `/sessions/${sessionId}/report`,
    method: 'GET',
  })
}
