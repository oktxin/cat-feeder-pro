import express from 'express';
import cors from 'cors';
import http from 'http';
import { MQTTBridge } from './mqtt/client';
import { MQTTSocketBridge } from './mqtt/bridge';
import { setupWebSocket } from './websocket';
import { createDevicesRouter } from './routes/devices';
import { initializeDatabase, cleanupOldData } from './db';

const PORT = process.env.PORT || 3001;
const MQTT_HOST = process.env.MQTT_HOST || 'localhost';
const MQTT_PORT = parseInt(process.env.MQTT_PORT || '1883');

async function startServer() {
  console.log('🚀 Starting Cat Feeder Backend...');

  // Initialize database
  await initializeDatabase();

  // Create Express app
  const app = express();
  const httpServer = http.createServer(app);

  // Middleware
  app.use(cors());
  app.use(express.json());

  // Health check
  app.get('/health', (req, res) => {
    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      mqtt: mqttBridge.isConnected()
    });
  });

  // Initialize MQTT
  const mqttBridge = new MQTTBridge(MQTT_HOST, MQTT_PORT);

  try {
    await mqttBridge.connect();
  } catch (error) {
    console.error('❌ Failed to connect to MQTT broker:', error);
    process.exit(1);
  }

  // Setup WebSocket
  const io = setupWebSocket(httpServer);

  // Bridge MQTT and WebSocket
  const bridge = new MQTTSocketBridge(mqttBridge, io);

  // API Routes
  app.use('/api/devices', createDevicesRouter(mqttBridge));

  // Start server
  httpServer.listen(PORT, () => {
    console.log(`✅ Server running on port ${PORT}`);
    console.log(`📡 WebSocket server ready`);
    console.log(`🔌 MQTT bridge active`);
  });

  // Cleanup old data daily
  setInterval(() => {
    cleanupOldData();
  }, 24 * 60 * 60 * 1000); // Every 24 hours

  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('⏹️  SIGTERM received, shutting down gracefully...');
    httpServer.close(() => {
      mqttBridge.disconnect();
      process.exit(0);
    });
  });

  process.on('SIGINT', () => {
    console.log('⏹️  SIGINT received, shutting down gracefully...');
    httpServer.close(() => {
      mqttBridge.disconnect();
      process.exit(0);
    });
  });
}

startServer().catch(error => {
  console.error('❌ Failed to start server:', error);
  process.exit(1);
});
