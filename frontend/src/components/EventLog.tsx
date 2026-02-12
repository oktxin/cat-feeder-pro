import React, { useEffect, useState } from 'react';
import { devicesApi, DeviceEvent } from '../api/client';
import { Activity } from 'lucide-react';

interface EventLogProps {
  deviceId: string;
}

export const EventLog: React.FC<EventLogProps> = ({ deviceId }) => {
  const [events, setEvents] = useState<DeviceEvent[]>([]);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await devicesApi.getEvents(deviceId);
        setEvents(response.data.slice(0, 5));
      } catch (error) {
        console.error('Failed to fetch events:', error);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 10000);
    return () => clearInterval(interval);
  }, [deviceId]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'cat_detected':
        return '🐱';
      case 'feeding_complete':
        return '✅';
      case 'low_food_warning':
      case 'low_water_warning':
        return '⚠️';
      case 'error':
        return '🔴';
      default:
        return '📋';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Activity size={24} className="text-orange-warm" />
        <h3 className="text-xl font-display font-bold text-dark">Recent Events</h3>
      </div>

      <div className="space-y-3">
        {events.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-4">No recent events</p>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="flex items-start space-x-3 p-3 bg-cream rounded-lg hover:bg-orange-50 transition-colors"
            >
              <span className="text-2xl">{getEventIcon(event.type)}</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-dark">
                  {event.data.message || event.type}
                </p>
                <p className="text-xs text-gray-500">{formatTime(event.timestamp)}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
