import { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { useFeederStore } from '../store/feederStore';
import { DeviceState } from '../api/client';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:3001';

export const useWebSocket = (deviceId: string) => {
  const socketRef = useRef<Socket | null>(null);
  const { setDeviceState, setOnlineStatus } = useFeederStore();

  useEffect(() => {
    const socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('WebSocket connected');
      socket.emit('subscribe', { deviceId });
    });

    socket.on('telemetry', (data: { deviceId: string; data: DeviceState }) => {
      if (data.deviceId === deviceId) {
        setDeviceState(data.data);
      }
    });

    socket.on('event', (data: { deviceId: string; type: string; data: any }) => {
      if (data.deviceId === deviceId) {
        console.log('Event received:', data.type, data.data);
      }
    });

    socket.on('device_status', (data: { deviceId: string; online: boolean }) => {
      if (data.deviceId === deviceId) {
        setOnlineStatus(data.online);
      }
    });

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    return () => {
      socket.emit('unsubscribe', { deviceId });
      socket.disconnect();
    };
  }, [deviceId, setDeviceState, setOnlineStatus]);

  return socketRef.current;
};
