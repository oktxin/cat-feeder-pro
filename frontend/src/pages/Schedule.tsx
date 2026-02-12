import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Save } from 'lucide-react';
import { devicesApi } from '../api/client';
import { useFeederStore } from '../store/feederStore';

export const Schedule: React.FC = () => {
  const { deviceId, setSchedule } = useFeederStore();
  const [localSchedule, setLocalSchedule] = useState<{ time: string; portion: number }[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const response = await devicesApi.getSchedule(deviceId);
        setSchedule(response.data);
        setLocalSchedule(
          response.data.map((s) => ({ time: s.time, portion: s.portion }))
        );
      } catch (error) {
        console.error('Failed to fetch schedule:', error);
      }
    };

    fetchSchedule();
  }, [deviceId, setSchedule]);

  const addScheduleItem = () => {
    setLocalSchedule([...localSchedule, { time: '12:00', portion: 50 }]);
  };

  const removeScheduleItem = (index: number) => {
    setLocalSchedule(localSchedule.filter((_, i) => i !== index));
  };

  const updateScheduleItem = (index: number, field: 'time' | 'portion', value: string | number) => {
    const updated = [...localSchedule];
    updated[index] = { ...updated[index], [field]: value };
    setLocalSchedule(updated);
  };

  const saveSchedule = async () => {
    setIsSaving(true);
    try {
      const times = localSchedule.map((s) => s.time);
      const portions = localSchedule.map((s) => s.portion);
      await devicesApi.updateSchedule(deviceId, times, portions);
      alert('Schedule saved successfully!');
    } catch (error) {
      console.error('Failed to save schedule:', error);
      alert('Failed to save schedule');
    } finally {
      setIsSaving(false);
    }
  };

  const totalDailyFood = localSchedule.reduce((sum, s) => sum + s.portion, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-display font-bold text-dark">Feeding Schedule</h1>
          <p className="text-gray-600 mt-1">Manage automatic feeding times</p>
        </div>
        <button
          onClick={addScheduleItem}
          className="flex items-center space-x-2 bg-orange-warm text-white px-4 py-2 rounded-xl hover:bg-orange-600 transition-colors"
        >
          <Plus size={20} />
          <span>Add Time</span>
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="space-y-4">
          {localSchedule.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No feeding times scheduled. Click "Add Time" to create a schedule.
            </p>
          ) : (
            localSchedule.map((item, index) => (
              <div
                key={index}
                className="flex items-center space-x-4 p-4 bg-cream rounded-xl"
              >
                <div className="flex-1 grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Time
                    </label>
                    <input
                      type="time"
                      value={item.time}
                      onChange={(e) => updateScheduleItem(index, 'time', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-warm focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Portion (g)
                    </label>
                    <input
                      type="number"
                      min="10"
                      max="100"
                      value={item.portion}
                      onChange={(e) =>
                        updateScheduleItem(index, 'portion', Number(e.target.value))
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-warm focus:border-transparent"
                    />
                  </div>
                </div>
                <button
                  onClick={() => removeScheduleItem(index)}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))
          )}
        </div>

        {localSchedule.length > 0 && (
          <>
            <div className="mt-6 p-4 bg-blue-50 rounded-xl">
              <p className="text-sm text-blue-900">
                <strong>Total daily food:</strong> {totalDailyFood}g (
                {(totalDailyFood * 3.5).toFixed(0)} kcal)
              </p>
              <p className="text-xs text-blue-700 mt-1">
                Based on {localSchedule.length} feeding{localSchedule.length !== 1 ? 's' : ''} per
                day
              </p>
            </div>

            <button
              onClick={saveSchedule}
              disabled={isSaving}
              className={`mt-6 w-full flex items-center justify-center space-x-2 py-3 px-6 rounded-xl font-semibold text-white transition-all ${
                isSaving
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-mint hover:bg-teal-500 active:scale-95'
              }`}
            >
              <Save size={20} />
              <span>{isSaving ? 'Saving...' : 'Save Schedule'}</span>
            </button>
          </>
        )}
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-xl font-display font-bold text-dark mb-4">24-Hour Timeline</h3>
        <div className="relative h-16 bg-gradient-to-r from-blue-100 via-yellow-100 to-blue-100 rounded-lg overflow-hidden">
          {localSchedule.map((item, index) => {
            const [hours, minutes] = item.time.split(':').map(Number);
            const position = ((hours * 60 + minutes) / (24 * 60)) * 100;

            return (
              <div
                key={index}
                className="absolute top-0 bottom-0 w-1 bg-orange-warm"
                style={{ left: `${position}%` }}
                title={`${item.time} - ${item.portion}g`}
              >
                <div className="absolute -top-6 -left-4 text-xs font-semibold text-orange-warm whitespace-nowrap">
                  {item.time}
                </div>
              </div>
            );
          })}
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span>00:00</span>
          <span>06:00</span>
          <span>12:00</span>
          <span>18:00</span>
          <span>24:00</span>
        </div>
      </div>
    </div>
  );
};
