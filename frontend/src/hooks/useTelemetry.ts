import { useState, useEffect } from 'react';
import { devicesApi } from '../api/client';
import { useFeederStore } from '../store/feederStore';

export const useTelemetry = (deviceId: string) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { deviceState, setDeviceState } = useFeederStore();

  useEffect(() => {
    const fetchInitialState = async () => {
      try {
        const response = await devicesApi.getStatus(deviceId);
        setDeviceState(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load device status');
        setLoading(false);
      }
    };

    fetchInitialState();
  }, [deviceId, setDeviceState]);

  return { deviceState, loading, error };
};
