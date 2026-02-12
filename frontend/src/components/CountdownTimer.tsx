import React, { useEffect, useState } from 'react';
import { Clock } from 'lucide-react';

interface CountdownTimerProps {
  targetTime: string | null;
}

export const CountdownTimer: React.FC<CountdownTimerProps> = ({ targetTime }) => {
  const [timeLeft, setTimeLeft] = useState<string>('--:--:--');

  useEffect(() => {
    if (!targetTime) {
      setTimeLeft('No schedule');
      return;
    }

    const calculateTimeLeft = () => {
      const now = new Date();
      const target = new Date(targetTime);
      const diff = target.getTime() - now.getTime();

      if (diff <= 0) {
        return 'Feeding now...';
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      return `${hours.toString().padStart(2, '0')}:${minutes
        .toString()
        .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    };

    const interval = setInterval(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);

    setTimeLeft(calculateTimeLeft());

    return () => clearInterval(interval);
  }, [targetTime]);

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Clock size={24} className="text-orange-warm" />
          <div>
            <h3 className="text-xl font-display font-bold text-dark">Next Feeding</h3>
            <p className="text-sm text-gray-500">Automatic schedule</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold font-display text-orange-warm">{timeLeft}</p>
        </div>
      </div>
    </div>
  );
};
