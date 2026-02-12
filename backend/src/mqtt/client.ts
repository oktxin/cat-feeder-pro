import mqtt from 'mqtt';
import { EventEmitter } from 'events';
import { DeviceState, DeviceEvent, DeviceCommand, DeviceStatus } from '../types/feeder';

export class MQTTBridge extends EventEmitter {
  private client: mqtt.MqttClient | null = null;
  private connected = false;
  private readonly host: string;
  private readonly port: number;

  constructor(host: string = 'localhost', port: number = 1883) {
    super();
    this.host = host;
    this.port = port;
  }

  async connect(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      const brokerUrl = `mqtt://${this.host}:${this.port}`;
      console.log(`🔌 Connecting to MQTT broker at ${brokerUrl}...`);

      this.client = mqtt.connect(brokerUrl, {
        clientId: `backend_${Math.random().toString(16).slice(2, 10)}`,
        clean: true,
        reconnectPeriod: 5000,
        connectTimeout: 30000,
      });

      this.client.on('connect', () => {
        console.log('✅ Connected to MQTT broker');
        this.connected = true;
        this.subscribeToTopics();
        resolve(true);
      });

      this.client.on('error', (error) => {
        console.error('❌ MQTT connection error:', error);
        this.connected = false;
        reject(error);
      });

      this.client.on('message', (topic, payload) => {
        this.handleMessage(topic, payload);
      });

      this.client.on('offline', () => {
        console.log('📡 MQTT client offline');
        this.connected = false;
      });

      this.client.on('reconnect', () => {
        console.log('🔄 Reconnecting to MQTT broker...');
      });
    });
  }

  private subscribeToTopics() {
    if (!this.client) return;

    const topics = [
      'feeder/+/telemetry',
      'feeder/+/events',
      'feeder/+/status',
    ];

    topics.forEach(topic => {
      this.client!.subscribe(topic, (err) => {
        if (err) {
          console.error(`❌ Failed to subscribe to ${topic}:`, err);
        } else {
          console.log(`📬 Subscribed to ${topic}`);
        }
      });
    });
  }

  private handleMessage(topic: string, payload: Buffer) {
    try {
      const data = JSON.parse(payload.toString());
      const parts = topic.split('/');
      const deviceNum = parts[1];
      const messageType = parts[2];

      switch (messageType) {
        case 'telemetry':
          this.emit('telemetry', data as DeviceState);
          break;

        case 'events':
          this.emit('event', data as DeviceEvent);
          break;

        case 'status':
          this.emit('status', {
            deviceId: `feeder_${deviceNum}`,
            ...data
          } as DeviceStatus);
          break;

        default:
          console.warn(`Unknown message type: ${messageType}`);
      }
    } catch (error) {
      console.error('❌ Error parsing MQTT message:', error);
    }
  }

  sendCommand(deviceId: string, command: DeviceCommand): boolean {
    if (!this.client || !this.connected) {
      console.error('❌ Cannot send command - MQTT not connected');
      return false;
    }

    const deviceNum = deviceId.split('_')[1];
    const topic = `feeder/${deviceNum}/commands`;
    const payload = JSON.stringify(command);

    this.client.publish(topic, payload, { qos: 1 }, (err) => {
      if (err) {
        console.error(`❌ Failed to send command to ${deviceId}:`, err);
      } else {
        console.log(`📤 Command sent to ${deviceId}: ${command.action}`);
      }
    });

    return true;
  }

  disconnect() {
    if (this.client) {
      this.client.end();
      this.connected = false;
      console.log('🔌 Disconnected from MQTT broker');
    }
  }

  isConnected(): boolean {
    return this.connected;
  }
}
