import React, { useState, useEffect } from 'react';
import { Save, User, Utensils, Bell } from 'lucide-react';
import { devicesApi, Settings as SettingsType } from '../api/client';
import { useFeederStore } from '../store/feederStore';

export const Settings: React.FC = () => {
  const { deviceId } = useFeederStore();
  const [settings, setSettings] = useState<SettingsType>({
    petName: 'Whiskers',
    petWeight: undefined,
    foodType: 'dry',
    caloriesPerGram: 3.5,
    lowFoodThreshold: 20,
    lowWaterThreshold: 20,
    theme: 'light',
  });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await devicesApi.getSettings(deviceId);
        setSettings(response.data);
      } catch (error) {
        console.error('Failed to fetch settings:', error);
      }
    };

    fetchSettings();
  }, [deviceId]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await devicesApi.updateSettings(deviceId, settings);
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const calculateDailyFood = () => {
    if (!settings.petWeight) return 'N/A';
    const caloriesPerDay = settings.petWeight * 70;
    const gramsPerDay = caloriesPerDay / settings.caloriesPerGram;
    return `${gramsPerDay.toFixed(0)}g (${caloriesPerDay.toFixed(0)} kcal)`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-display font-bold text-dark">Settings</h1>
          <p className="text-gray-600 mt-1">Configure your cat feeder</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <User className="text-orange-warm" size={24} />
          <h3 className="text-xl font-display font-bold text-dark">Pet Information</h3>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pet Name</label>
            <input
              type="text"
              value={settings.petName}
              onChange={(e) => setSettings({ ...settings, petName: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-warm focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pet Weight (kg)
            </label>
            <input
              type="number"
              step="0.1"
              value={settings.petWeight || ''}
              onChange={(e) =>
                setSettings({ ...settings, petWeight: parseFloat(e.target.value) || undefined })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-warm focus:border-transparent"
              placeholder="e.g., 4.5"
            />
          </div>

          {settings.petWeight && (
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-900">
                <strong>Recommended daily food:</strong> {calculateDailyFood()}
              </p>
              <p className="text-xs text-blue-700 mt-1">
                Based on {settings.petWeight}kg body weight
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Utensils className="text-mint" size={24} />
          <h3 className="text-xl font-display font-bold text-dark">Food Configuration</h3>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Food Type</label>
            <select
              value={settings.foodType}
              onChange={(e) => setSettings({ ...settings, foodType: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-warm focus:border-transparent"
            >
              <option value="dry">Dry Food</option>
              <option value="wet">Wet Food</option>
              <option value="mixed">Mixed</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Calories per Gram
            </label>
            <input
              type="number"
              step="0.1"
              value={settings.caloriesPerGram}
              onChange={(e) =>
                setSettings({ ...settings, caloriesPerGram: parseFloat(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-warm focus:border-transparent"
            />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Bell className="text-yellow-500" size={24} />
          <h3 className="text-xl font-display font-bold text-dark">Alert Thresholds</h3>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Low Food Alert (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={settings.lowFoodThreshold}
              onChange={(e) =>
                setSettings({ ...settings, lowFoodThreshold: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-warm focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Low Water Alert (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={settings.lowWaterThreshold}
              onChange={(e) =>
                setSettings({ ...settings, lowWaterThreshold: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-warm focus:border-transparent"
            />
          </div>
        </div>
      </div>

      <button
        onClick={handleSave}
        disabled={isSaving}
        className={`w-full flex items-center justify-center space-x-2 py-3 px-6 rounded-xl font-semibold text-white transition-all ${
          isSaving
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-orange-warm hover:bg-orange-600 active:scale-95'
        }`}
      >
        <Save size={20} />
        <span>{isSaving ? 'Saving...' : 'Save Settings'}</span>
      </button>
    </div>
  );
};
