export type Period = "day" | "week" | "month";

export interface Summary {
  total_messages: number;
  total_messages_change: number;
  active_users: number;
  active_users_change: number;
  avg_dialog_length: number;
  avg_dialog_length_change: number;
  messages_per_day: number;
  messages_per_day_change: number;
}

export interface TimelinePoint {
  date: string;
  user_messages: number;
  bot_messages: number;
  total: number;
}

export interface UserActivity {
  user_id: number;
  username: string | null;
  first_name: string | null;
  message_count: number;
  last_activity: string;
}

export interface DialogPreview {
  user_id: number;
  username: string | null;
  first_name: string | null;
  last_message: string;
  message_count: number;
  last_activity: string;
}

export interface StatsResponse {
  summary: Summary;
  activity_timeline: TimelinePoint[];
  top_users: UserActivity[];
  recent_dialogs: DialogPreview[];
}
