import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { devicesApi } from '../api/client';

interface FeedNowButtonProps {
  deviceId: string;
  disabled?: boolean;
}

export const FeedNowButton: React.FC<FeedNowButtonProps> = ({ deviceId, disabled = false }) => {
  const [portion, setPortion] = useState(50);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isFeeding, setIsFeeding] = useState(false);

  const handleFeed = async () => {
    setIsFeeding(true);
    try {
      await devicesApi.feedNow(deviceId, portion);
      setTimeout(() => {
        setIsFeeding(false);
        setIsExpanded(false);
      }, 3000);
    } catch (error) {
      console.error('Failed to trigger feeding:', error);
      setIsFeeding(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full"
      >
        <h3 className="text-xl font-display font-bold text-dark">Feed Now</h3>
        <ChevronDown
          className={`transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          size={20}
        />
      </button>

      {isExpanded && (
        <div className="mt-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Portion Size: {portion}g
            </label>
            <input
              type="range"
              min="10"
              max="100"
              value={portion}
              onChange={(e) => setPortion(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-orange-warm"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>10g</span>
              <span>100g</span>
            </div>
          </div>

          <button
            onClick={handleFeed}
            disabled={disabled || isFeeding}
            className={`w-full py-3 px-6 rounded-xl font-semibold text-white transition-all ${
              isFeeding
                ? 'bg-mint animate-pulse-slow'
                : disabled
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-orange-warm hover:bg-orange-600 active:scale-95'
            }`}
          >
            {isFeeding ? 'Feeding...' : 'Feed Now'}
          </button>
        </div>
      )}
    </div>
  );
};
