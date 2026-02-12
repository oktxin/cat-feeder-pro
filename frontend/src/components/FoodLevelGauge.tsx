import React from 'react';

interface FoodLevelGaugeProps {
  level: number;
}

export const FoodLevelGauge: React.FC<FoodLevelGaugeProps> = ({ level }) => {
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (level / 100) * circumference;

  const getColor = () => {
    if (level < 20) return '#EF4444';
    if (level < 50) return '#F59E0B';
    return '#10B981';
  };

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="200" height="200" className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth="20"
        />
        {/* Progress circle */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth="20"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-4xl font-bold font-display" style={{ color: getColor() }}>
          {level}%
        </span>
        <span className="text-sm text-gray-500">Food Level</span>
      </div>
    </div>
  );
};
