import axios from 'axios';
import { AuthTokens, User, Expense, Mood, CreateExpense, CreateMood } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  async login(email: string, password: string): Promise<AuthTokens> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  async signup(email: string, password: string, fullName?: string): Promise<User> {
    const response = await apiClient.post('/auth/signup', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },
};

// Expenses API
export const expensesAPI = {
  async getExpenses(skip = 0, limit = 100): Promise<Expense[]> {
    const response = await apiClient.get(`/expenses/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async createExpense(expense: CreateExpense): Promise<Expense> {
    const response = await apiClient.post('/expenses/', expense);
    return response.data;
  },

  async updateExpense(id: number, expense: Partial<CreateExpense>): Promise<Expense> {
    const response = await apiClient.put(`/expenses/${id}`, expense);
    return response.data;
  },

  async deleteExpense(id: number): Promise<void> {
    await apiClient.delete(`/expenses/${id}`);
  },
};

// Moods API
export const moodsAPI = {
  async getMoods(skip = 0, limit = 100): Promise<Mood[]> {
    const response = await apiClient.get(`/moods/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async createMood(mood: CreateMood): Promise<Mood> {
    const response = await apiClient.post('/moods/', mood);
    return response.data;
  },

  async updateMood(id: number, mood: Partial<CreateMood>): Promise<Mood> {
    const response = await apiClient.put(`/moods/${id}`, mood);
    return response.data;
  },

  async deleteMood(id: number): Promise<void> {
    await apiClient.delete(`/moods/${id}`);
  },
};
