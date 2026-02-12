import React from 'react';
import { useFeederStore } from '../store/feederStore';
import { FoodLevelGauge } from '../components/FoodLevelGauge';
import { WaterLevelBar } from '../components/WaterLevelBar';
import { FeedNowButton } from '../components/FeedNowButton';
import { CatPresenceIndicator } from '../components/CatPresenceIndicator';
import { EventLog } from '../components/EventLog';
import { CountdownTimer } from '../components/CountdownTimer';
import { StatusIndicator } from '../components/StatusIndicator';

export const Dashboard: React.FC = () => {
  const { deviceState, isOnline, deviceId } = useFeederStore();

  if (!deviceState) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-warm mx-auto mb-4"></div>
          <p className="text-gray-600">Loading device data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-display font-bold text-dark">Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor your cat's feeding device</p>
        </div>
      </div>

      <StatusIndicator
        online={isOnline}
        batteryLevel={deviceState.battery_level}
        wifiSignal={deviceState.wifi_signal}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 flex justify-center items-center">
          <FoodLevelGauge level={deviceState.food_level} />
        </div>

        <div className="space-y-6">
          <WaterLevelBar level={deviceState.water_level} />
          <FeedNowButton deviceId={deviceId} disabled={!isOnline} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CatPresenceIndicator detected={deviceState.cat_detected} />
        <CountdownTimer targetTime={deviceState.next_feeding_time} />
      </div>

      <EventLog deviceId={deviceId} />

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-xl font-display font-bold text-dark mb-4">Device Info</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Temperature</p>
            <p className="font-semibold text-lg">{deviceState.temperature}°C</p>
          </div>
          <div>
            <p className="text-gray-500">Bowl Weight</p>
            <p className="font-semibold text-lg">{deviceState.weight_bowl}g</p>
          </div>
          <div>
            <p className="text-gray-500">Feedings Today</p>
            <p className="font-semibold text-lg">{deviceState.total_feedings_today}</p>
          </div>
          <div>
            <p className="text-gray-500">Motor Status</p>
            <p className="font-semibold text-lg capitalize">{deviceState.motor_status}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
