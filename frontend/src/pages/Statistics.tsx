import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, Calendar, Award } from 'lucide-react';
import { devicesApi, Statistics as StatsType } from '../api/client';
import { useFeederStore } from '../store/feederStore';

export const Statistics: React.FC = () => {
  const { deviceId } = useFeederStore();
  const [stats, setStats] = useState<StatsType | null>(null);
  const [telemetryData, setTelemetryData] = useState<any[]>([]);
  const [period, setPeriod] = useState<'day' | 'week' | 'month'>('week');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, telemetryRes] = await Promise.all([
          devicesApi.getStats(deviceId, period),
          devicesApi.getTelemetry(deviceId, period === 'day' ? '24h' : '7d'),
        ]);

        setStats(statsRes.data);

        const formattedTelemetry = telemetryRes.data.reverse().map((t: any) => ({
          time: new Date(t.timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          }),
          foodLevel: t.foodLevel,
        }));

        setTelemetryData(formattedTelemetry);
      } catch (error) {
        console.error('Failed to fetch statistics:', error);
      }
    };

    fetchData();
  }, [deviceId, period]);

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-warm mx-auto mb-4"></div>
          <p className="text-gray-600">Loading statistics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-display font-bold text-dark">Statistics</h1>
          <p className="text-gray-600 mt-1">Feeding insights and analytics</p>
        </div>

        <div className="flex space-x-2">
          {(['day', 'week', 'month'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                period === p
                  ? 'bg-orange-warm text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-2">
            <TrendingUp className="text-orange-warm" size={24} />
            <h3 className="text-lg font-display font-bold text-dark">Total Feedings</h3>
          </div>
          <p className="text-4xl font-bold text-orange-warm">{stats.totalFeedings}</p>
          <p className="text-sm text-gray-500 mt-1">This {period}</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-2">
            <Calendar className="text-mint" size={24} />
            <h3 className="text-lg font-display font-bold text-dark">Food Consumed</h3>
          </div>
          <p className="text-4xl font-bold text-mint">{stats.totalFoodConsumed}g</p>
          <p className="text-sm text-gray-500 mt-1">
            {(stats.totalFoodConsumed * 3.5).toFixed(0)} kcal
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-2">
            <Award className="text-yellow-500" size={24} />
            <h3 className="text-lg font-display font-bold text-dark">Favorite Time</h3>
          </div>
          <p className="text-4xl font-bold text-yellow-600">
            {stats.favoriteTime || 'N/A'}
          </p>
          <p className="text-sm text-gray-500 mt-1">Most frequent feeding</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-xl font-display font-bold text-dark mb-4">Food Level History</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={telemetryData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="time" stroke="#6B7280" />
            <YAxis stroke="#6B7280" domain={[0, 100]} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#FFF',
                border: '1px solid #E5E7EB',
                borderRadius: '0.5rem',
              }}
            />
            <Line
              type="monotone"
              dataKey="foodLevel"
              stroke="#FF6B35"
              strokeWidth={3}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-xl font-display font-bold text-dark mb-4">Daily Feedings</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stats.dailyFeedings}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="date" stroke="#6B7280" />
            <YAxis stroke="#6B7280" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#FFF',
                border: '1px solid #E5E7EB',
                borderRadius: '0.5rem',
              }}
            />
            <Bar dataKey="count" fill="#4ECDC4" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
