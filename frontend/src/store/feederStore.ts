import { create } from 'zustand';
import { DeviceState, Settings, Schedule } from '../api/client';

interface FeederStore {
  deviceId: string;
  deviceState: DeviceState | null;
  isOnline: boolean;
  settings: Settings | null;
  schedule: Schedule[];
  setDeviceState: (state: DeviceState) => void;
  setOnlineStatus: (online: boolean) => void;
  setSettings: (settings: Settings) => void;
  setSchedule: (schedule: Schedule[]) => void;
  updateDeviceId: (deviceId: string) => void;
}

export const useFeederStore = create<FeederStore>((set) => ({
  deviceId: 'feeder_001',
  deviceState: null,
  isOnline: false,
  settings: null,
  schedule: [],
  setDeviceState: (state) => set({ deviceState: state }),
  setOnlineStatus: (online) => set({ isOnline: online }),
  setSettings: (settings) => set({ settings }),
  setSchedule: (schedule) => set({ schedule }),
  updateDeviceId: (deviceId) => set({ deviceId }),
}));
