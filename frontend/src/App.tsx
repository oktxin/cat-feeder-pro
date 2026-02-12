import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Calendar, TrendingUp, Settings as SettingsIcon } from 'lucide-react';
import { Dashboard } from './pages/Dashboard';
import { Schedule } from './pages/Schedule';
import { Statistics } from './pages/Statistics';
import { Settings } from './pages/Settings';
import { useFeederStore } from './store/feederStore';
import { useWebSocket } from './hooks/useWebSocket';
import { useTelemetry } from './hooks/useTelemetry';
import { useNotifications } from './hooks/useNotifications';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/schedule', icon: Calendar, label: 'Schedule' },
    { path: '/statistics', icon: TrendingUp, label: 'Statistics' },
    { path: '/settings', icon: SettingsIcon, label: 'Settings' },
  ];

  return (
    <nav className="bg-white shadow-lg rounded-2xl p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="text-4xl">🐱</div>
          <div>
            <h1 className="text-2xl font-display font-bold text-dark">Smart Cat Feeder</h1>
            <p className="text-sm text-gray-500">IoT Device Management</p>
          </div>
        </div>

        <div className="flex space-x-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-colors ${
                  isActive
                    ? 'bg-orange-warm text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon size={20} />
                <span className="font-semibold">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

function App() {
  const { deviceId } = useFeederStore();

  useWebSocket(deviceId);
  useTelemetry(deviceId);
  const { requestPermission } = useNotifications();

  useEffect(() => {
    requestPermission();
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-cream py-8 px-4">
        <div className="max-w-7xl mx-auto">
          <Navigation />

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/schedule" element={<Schedule />} />
            <Route path="/statistics" element={<Statistics />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
