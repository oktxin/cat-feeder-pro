import React from 'react';
import { Wifi, WifiOff } from 'lucide-react';

interface StatusIndicatorProps {
  online: boolean;
  batteryLevel: number;
  wifiSignal: number;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  online,
  batteryLevel,
  wifiSignal,
}) => {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div
            className={`w-4 h-4 rounded-full ${
              online ? 'bg-green-500 animate-pulse-slow' : 'bg-red-500'
            }`}
          />
          <span className={`font-semibold ${online ? 'text-green-600' : 'text-red-600'}`}>
            {online ? 'Online' : 'Offline'}
          </span>
        </div>

        <div className="flex items-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            {online ? <Wifi size={18} /> : <WifiOff size={18} />}
            <span>{wifiSignal} dBm</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>🔋</span>
            <span>{batteryLevel}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};
