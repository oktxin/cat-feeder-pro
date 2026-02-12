import { useEffect } from 'react';
import { useFeederStore } from '../store/feederStore';

export const useNotifications = () => {
  const { deviceState } = useFeederStore();

  useEffect(() => {
    if (!deviceState) return;

    if (deviceState.cat_detected) {
      showNotification('🐱 Your cat is at the bowl!');
    }

    if (deviceState.food_level < 20) {
      showNotification(`⚠️ Food running low — ${deviceState.food_level}% remaining`);
    }

    if (deviceState.motor_status === 'error') {
      showNotification('🔴 Device error: motor jam detected');
    }
  }, [deviceState]);

  const showNotification = (message: string) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Smart Cat Feeder', { body: message });
    } else {
      console.log('Notification:', message);
    }
  };

  const requestPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  };

  return { requestPermission };
};
