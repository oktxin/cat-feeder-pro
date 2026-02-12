import { Server as SocketIOServer } from 'socket.io';
import { MQTTBridge } from './client';
import prisma from '../db';
import { DeviceState, DeviceEvent, DeviceStatus } from '../types/feeder';

export class MQTTSocketBridge {
  private mqttBridge: MQTTBridge;
  private io: SocketIOServer;
  private deviceStatuses: Map<string, DeviceStatus> = new Map();

  constructor(mqttBridge: MQTTBridge, io: SocketIOServer) {
    this.mqttBridge = mqttBridge;
    this.io = io;
    this.setupListeners();
  }

  private setupListeners() {
    // MQTT -> Database & WebSocket
    this.mqttBridge.on('telemetry', async (data: DeviceState) => {
      await this.handleTelemetry(data);
    });

    this.mqttBridge.on('event', async (event: DeviceEvent) => {
      await this.handleEvent(event);
    });

    this.mqttBridge.on('status', (status: DeviceStatus) => {
      this.handleStatus(status);
    });
  }

  private async handleTelemetry(state: DeviceState) {
    try {
      // Store in database
      await prisma.telemetry.create({
        data: {
          deviceId: state.device_id,
          foodLevel: state.food_level,
          waterLevel: state.water_level,
          motorStatus: state.motor_status,
          catDetected: state.cat_detected,
          weightBowl: state.weight_bowl,
          doorOpen: state.door_open,
          temperature: state.temperature,
          wifiSignal: state.wifi_signal,
          batteryLevel: state.battery_level,
          totalFeedingsToday: state.total_feedings_today,
          firmwareVersion: state.firmware_version,
          timestamp: new Date(state.timestamp),
        }
      });

      // Broadcast to WebSocket clients
      this.io.emit('telemetry', {
        deviceId: state.device_id,
        data: state
      });

    } catch (error) {
      console.error('❌ Error handling telemetry:', error);
    }
  }

  private async handleEvent(event: DeviceEvent) {
    try {
      // Determine device ID from event context or use default
      const deviceId = 'feeder_001';

      // Store in database
      await prisma.event.create({
        data: {
          deviceId,
          type: event.type,
          data: JSON.stringify(event.data),
          timestamp: new Date(event.timestamp),
        }
      });

      // Broadcast to WebSocket clients
      this.io.emit('event', {
        deviceId,
        type: event.type,
        data: event
      });

      console.log(`📋 Event recorded: ${event.type}`);

    } catch (error) {
      console.error('❌ Error handling event:', error);
    }
  }

  private handleStatus(status: DeviceStatus) {
    const deviceId = status.deviceId || 'feeder_001';

    this.deviceStatuses.set(deviceId, {
      online: status.online,
      lastSeen: new Date().toISOString()
    });

    // Broadcast to WebSocket clients
    this.io.emit('device_status', {
      deviceId,
      online: status.online
    });

    console.log(`📡 Device ${deviceId} is ${status.online ? 'online' : 'offline'}`);
  }

  getDeviceStatus(deviceId: string): DeviceStatus | undefined {
    return this.deviceStatuses.get(deviceId);
  }

  getAllDeviceStatuses(): Map<string, DeviceStatus> {
    return this.deviceStatuses;
  }
}
