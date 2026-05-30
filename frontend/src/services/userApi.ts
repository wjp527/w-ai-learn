import Taro from '@tarojs/taro'

import { useAuthStore } from '@/stores/authStore'
import type {
  LoginResponse,
  PaginatedQuestionSets,
  PaginatedRecords,
  QuestionSetDetail,
  ResumeInfo,
  StudyRecordDetail,
  UserProfile,
  UserStats,
} from '@/types/user'

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

export async function loginWithWechat(code: string) {
  return request<LoginResponse>('/auth/wechat/login', {
    url: '/auth/wechat/login',
    method: 'POST',
    data: { code },
  })
}

export async function getMe() {
  return request<UserProfile>('/auth/me', {
    url: '/auth/me',
    method: 'GET',
  })
}

export async function updateMe(payload: { nickname?: string; avatarUrl?: string }) {
  return request<UserProfile>('/auth/me', {
    url: '/auth/me',
    method: 'PATCH',
    data: payload,
  })
}

export async function getMyStats() {
  return request<UserStats>('/users/me/stats', {
    url: '/users/me/stats',
    method: 'GET',
  })
}

export async function getMyRecords(page = 1, pageSize = 20) {
  return request<PaginatedRecords>(`/users/me/records?page=${page}&pageSize=${pageSize}`, {
    url: `/users/me/records?page=${page}&pageSize=${pageSize}`,
    method: 'GET',
  })
}

export async function getMyRecordDetail(recordId: string) {
  return request<StudyRecordDetail>(`/users/me/records/${recordId}`, {
    url: `/users/me/records/${recordId}`,
    method: 'GET',
  })
}

export async function getMyQuestionSets(page = 1, pageSize = 20) {
  return request<PaginatedQuestionSets>(`/users/me/question-sets?page=${page}&pageSize=${pageSize}`, {
    url: `/users/me/question-sets?page=${page}&pageSize=${pageSize}`,
    method: 'GET',
  })
}

export async function getMyQuestionSetDetail(questionSetId: string) {
  return request<QuestionSetDetail>(`/users/me/question-sets/${questionSetId}`, {
    url: `/users/me/question-sets/${questionSetId}`,
    method: 'GET',
  })
}

export async function practiceQuestionSet(questionSetId: string) {
  return request<{ sessionId: string; status: string }>(
    `/users/me/question-sets/${questionSetId}/practice`,
    {
      url: `/users/me/question-sets/${questionSetId}/practice`,
      method: 'POST',
    },
  )
}

export async function getMyResume() {
  return request<ResumeInfo>('/users/me/resume', {
    url: '/users/me/resume',
    method: 'GET',
  })
}

export { request }
