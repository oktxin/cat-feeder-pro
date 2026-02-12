import React from 'react';
import { Cat } from 'lucide-react';

interface CatPresenceIndicatorProps {
  detected: boolean;
}

export const CatPresenceIndicator: React.FC<CatPresenceIndicatorProps> = ({ detected }) => {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center space-x-4">
        <div
          className={`p-4 rounded-full ${
            detected ? 'bg-mint animate-bounce-slow' : 'bg-gray-200'
          }`}
        >
          <Cat size={32} className={detected ? 'text-white' : 'text-gray-400'} />
        </div>
        <div>
          <h3 className="text-xl font-display font-bold text-dark">Cat at Bowl</h3>
          <p className={`text-sm ${detected ? 'text-mint font-semibold' : 'text-gray-500'}`}>
            {detected ? 'Your cat is eating!' : 'No cat detected'}
          </p>
        </div>
      </div>
    </div>
  );
};
