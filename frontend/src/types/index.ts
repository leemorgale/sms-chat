export interface User {
  id: number;
  name: string;
  phone_number: string;
  created_at: string;
  groups?: Group[];
}

export interface Group {
  id: number;
  name: string;
  created_at: string;
  user_count: number;
  members?: User[];
}

export interface Message {
  id: number;
  group_id: number;
  sender_id: number;
  content: string;
  created_at: string;
  sender?: User;
}

export interface ApiError {
  detail: string;
}