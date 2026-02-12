import React from 'react';
import { Droplet } from 'lucide-react';

interface WaterLevelBarProps {
  level: number;
}

export const WaterLevelBar: React.FC<WaterLevelBarProps> = ({ level }) => {
  const getColor = () => {
    if (level < 20) return 'bg-red-500';
    if (level < 50) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center space-x-4">
        <Droplet size={24} className="text-blue-500" />
        <div className="flex-1">
          <h3 className="text-xl font-display font-bold text-dark mb-2">Water Level</h3>
          <div className="relative w-full h-8 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${getColor()} transition-all duration-500 rounded-full flex items-center justify-end pr-2`}
              style={{ width: `${level}%` }}
            >
              <span className="text-xs font-semibold text-white">{level}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
