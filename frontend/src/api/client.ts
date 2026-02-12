import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

const apiClient = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface DeviceState {
  device_id: string;
  food_level: number;
  water_level: number;
  last_feeding_time: string | null;
  next_feeding_time: string | null;
  motor_status: 'idle' | 'running' | 'error';
  cat_detected: boolean;
  weight_bowl: number;
  door_open: boolean;
  temperature: number;
  wifi_signal: number;
  battery_level: number;
  total_feedings_today: number;
  firmware_version: string;
  timestamp: string;
}

export interface DeviceEvent {
  id: string;
  type: string;
  data: any;
  timestamp: string;
}

export interface Schedule {
  id: string;
  time: string;
  portion: number;
  enabled: boolean;
  weekdays: string;
}

export interface Settings {
  petName: string;
  petWeight?: number;
  foodType: string;
  caloriesPerGram: number;
  lowFoodThreshold: number;
  lowWaterThreshold: number;
  theme: string;
}

export interface Statistics {
  totalFeedings: number;
  averageFoodLevel: number;
  totalFoodConsumed: number;
  favoriteTime: string | null;
  dailyFeedings: Array<{ date: string; count: number }>;
}

export const devicesApi = {
  getAll: () => apiClient.get('/devices'),
  getStatus: (deviceId: string) => apiClient.get<DeviceState>(`/devices/${deviceId}/status`),
  getTelemetry: (deviceId: string, period: string = '24h') =>
    apiClient.get<DeviceState[]>(`/devices/${deviceId}/telemetry?period=${period}`),
  getEvents: (deviceId: string, type?: string) =>
    apiClient.get<DeviceEvent[]>(`/devices/${deviceId}/events${type ? `?type=${type}` : ''}`),
  getSchedule: (deviceId: string) =>
    apiClient.get<Schedule[]>(`/devices/${deviceId}/schedule`),
  updateSchedule: (deviceId: string, times: string[], portions?: number[]) =>
    apiClient.post(`/devices/${deviceId}/schedule`, { times, portions }),
  feedNow: (deviceId: string, portion: number) =>
    apiClient.post(`/devices/${deviceId}/feed`, { portion }),
  getSettings: (deviceId: string) =>
    apiClient.get<Settings>(`/devices/${deviceId}/settings`),
  updateSettings: (deviceId: string, settings: Partial<Settings>) =>
    apiClient.post(`/devices/${deviceId}/settings`, settings),
  getStats: (deviceId: string, period: string = 'week') =>
    apiClient.get<Statistics>(`/devices/${deviceId}/stats?period=${period}`),
};

export default apiClient;
