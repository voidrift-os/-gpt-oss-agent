export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Expense {
  id: number;
  title: string;
  amount: number;
  category: string;
  description?: string;
  date: string;
  owner_id: number;
  created_at: string;
  updated_at?: string;
}

export interface Mood {
  id: number;
  mood_level: number; // 1-10 scale
  mood_type?: string;
  notes?: string;
  date: string;
  owner_id: number;
  created_at: string;
  updated_at?: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface CreateExpense {
  title: string;
  amount: number;
  category: string;
  description?: string;
  date: string;
}

export interface CreateMood {
  mood_level: number;
  mood_type?: string;
  notes?: string;
  date: string;
}
