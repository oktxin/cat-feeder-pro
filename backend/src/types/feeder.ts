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
  type: string;
  timestamp: string;
  data: Record<string, any>;
}

export interface FeedCommand {
  action: 'feed_now';
  portion: number;
}

export interface ScheduleCommand {
  action: 'set_schedule';
  times: string[];
}

export interface PortionCommand {
  action: 'set_portion';
  grams: number;
}

export interface DoorCommand {
  action: 'open_door' | 'close_door';
}

export interface TareCommand {
  action: 'tare_scale';
}

export interface RebootCommand {
  action: 'reboot';
}

export type DeviceCommand =
  | FeedCommand
  | ScheduleCommand
  | PortionCommand
  | DoorCommand
  | TareCommand
  | RebootCommand;

export interface DeviceStatus {
  deviceId?: string;
  online: boolean;
  lastSeen?: string;
}

export interface TelemetryQuery {
  deviceId: string;
  startTime?: Date;
  endTime?: Date;
  limit?: number;
}

export interface EventQuery {
  deviceId: string;
  type?: string;
  startTime?: Date;
  endTime?: Date;
  limit?: number;
}

export interface Statistics {
  totalFeedings: number;
  averageFoodLevel: number;
  totalFoodConsumed: number;
  favoriteTime: string | null;
  dailyFeedings: Array<{
    date: string;
    count: number;
  }>;
}
