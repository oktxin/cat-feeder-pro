import { Router, Request, Response } from 'express';
import prisma from '../db';
import { MQTTBridge } from '../mqtt/client';
import { DeviceCommand } from '../types/feeder';

export function createDevicesRouter(mqttBridge: MQTTBridge) {
  const router = Router();

  // Get all devices
  router.get('/', async (req: Request, res: Response) => {
    try {
      const devices = await prisma.device.findMany({
        include: {
          settings: true
        }
      });
      res.json(devices);
    } catch (error) {
      console.error('Error fetching devices:', error);
      res.status(500).json({ error: 'Failed to fetch devices' });
    }
  });

  // Get device current status
  router.get('/:id/status', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;

      const latestTelemetry = await prisma.telemetry.findFirst({
        where: { deviceId: id },
        orderBy: { timestamp: 'desc' }
      });

      if (!latestTelemetry) {
        return res.status(404).json({ error: 'No telemetry data found' });
      }

      res.json(latestTelemetry);
    } catch (error) {
      console.error('Error fetching device status:', error);
      res.status(500).json({ error: 'Failed to fetch device status' });
    }
  });

  // Get telemetry history
  router.get('/:id/telemetry', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { period = '24h', limit = 100 } = req.query;

      const now = new Date();
      let startTime = new Date();

      switch (period) {
        case '24h':
          startTime.setHours(now.getHours() - 24);
          break;
        case '7d':
          startTime.setDate(now.getDate() - 7);
          break;
        case '30d':
          startTime.setDate(now.getDate() - 30);
          break;
        default:
          startTime.setHours(now.getHours() - 24);
      }

      const telemetry = await prisma.telemetry.findMany({
        where: {
          deviceId: id,
          timestamp: {
            gte: startTime
          }
        },
        orderBy: { timestamp: 'desc' },
        take: Number(limit)
      });

      res.json(telemetry);
    } catch (error) {
      console.error('Error fetching telemetry:', error);
      res.status(500).json({ error: 'Failed to fetch telemetry' });
    }
  });

  // Get events
  router.get('/:id/events', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { type, limit = 50 } = req.query;

      const where: any = { deviceId: id };
      if (type) {
        where.type = type;
      }

      const events = await prisma.event.findMany({
        where,
        orderBy: { timestamp: 'desc' },
        take: Number(limit)
      });

      const parsedEvents = events.map(event => ({
        ...event,
        data: JSON.parse(event.data)
      }));

      res.json(parsedEvents);
    } catch (error) {
      console.error('Error fetching events:', error);
      res.status(500).json({ error: 'Failed to fetch events' });
    }
  });

  // Get feeding schedule
  router.get('/:id/schedule', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;

      const schedules = await prisma.schedule.findMany({
        where: { deviceId: id },
        orderBy: { time: 'asc' }
      });

      res.json(schedules);
    } catch (error) {
      console.error('Error fetching schedule:', error);
      res.status(500).json({ error: 'Failed to fetch schedule' });
    }
  });

  // Update feeding schedule
  router.post('/:id/schedule', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { times, portions } = req.body;

      if (!Array.isArray(times)) {
        return res.status(400).json({ error: 'times must be an array' });
      }

      // Delete existing schedules
      await prisma.schedule.deleteMany({
        where: { deviceId: id }
      });

      // Create new schedules
      const schedulePromises = times.map((time: string, index: number) => {
        return prisma.schedule.create({
          data: {
            deviceId: id,
            time,
            portion: portions?.[index] || 50,
            enabled: true
          }
        });
      });

      const newSchedules = await Promise.all(schedulePromises);

      // Send command to device
      const command: DeviceCommand = {
        action: 'set_schedule',
        times
      };
      mqttBridge.sendCommand(id, command);

      res.json(newSchedules);
    } catch (error) {
      console.error('Error updating schedule:', error);
      res.status(500).json({ error: 'Failed to update schedule' });
    }
  });

  // Trigger immediate feeding
  router.post('/:id/feed', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { portion = 50 } = req.body;

      const command: DeviceCommand = {
        action: 'feed_now',
        portion: Number(portion)
      };

      const success = mqttBridge.sendCommand(id, command);

      if (success) {
        res.json({ success: true, message: 'Feeding command sent' });
      } else {
        res.status(500).json({ error: 'Failed to send feeding command' });
      }
    } catch (error) {
      console.error('Error triggering feed:', error);
      res.status(500).json({ error: 'Failed to trigger feeding' });
    }
  });

  // Update device settings
  router.post('/:id/settings', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const settings = req.body;

      const updatedSettings = await prisma.settings.upsert({
        where: { deviceId: id },
        update: settings,
        create: {
          deviceId: id,
          ...settings
        }
      });

      res.json(updatedSettings);
    } catch (error) {
      console.error('Error updating settings:', error);
      res.status(500).json({ error: 'Failed to update settings' });
    }
  });

  // Get device settings
  router.get('/:id/settings', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;

      const settings = await prisma.settings.findUnique({
        where: { deviceId: id }
      });

      if (!settings) {
        return res.status(404).json({ error: 'Settings not found' });
      }

      res.json(settings);
    } catch (error) {
      console.error('Error fetching settings:', error);
      res.status(500).json({ error: 'Failed to fetch settings' });
    }
  });

  // Get statistics
  router.get('/:id/stats', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const { period = 'week' } = req.query;

      const now = new Date();
      let startTime = new Date();

      switch (period) {
        case 'day':
          startTime.setHours(0, 0, 0, 0);
          break;
        case 'week':
          startTime.setDate(now.getDate() - 7);
          break;
        case 'month':
          startTime.setDate(now.getDate() - 30);
          break;
      }

      // Get feeding events
      const feedingEvents = await prisma.event.findMany({
        where: {
          deviceId: id,
          type: 'feeding_complete',
          timestamp: { gte: startTime }
        },
        orderBy: { timestamp: 'asc' }
      });

      // Get average food level
      const telemetryData = await prisma.telemetry.findMany({
        where: {
          deviceId: id,
          timestamp: { gte: startTime }
        },
        select: { foodLevel: true, timestamp: true }
      });

      const avgFoodLevel = telemetryData.length > 0
        ? telemetryData.reduce((sum, t) => sum + t.foodLevel, 0) / telemetryData.length
        : 0;

      // Calculate daily feedings
      const dailyFeedings: { [key: string]: number } = {};
      feedingEvents.forEach(event => {
        const date = event.timestamp.toISOString().split('T')[0];
        dailyFeedings[date] = (dailyFeedings[date] || 0) + 1;
      });

      const dailyFeedingsArray = Object.entries(dailyFeedings).map(([date, count]) => ({
        date,
        count
      }));

      // Calculate total food consumed
      const totalFoodConsumed = feedingEvents.reduce((sum, event) => {
        const data = JSON.parse(event.data);
        return sum + (data.portion_grams || 0);
      }, 0);

      // Find favorite feeding time
      const hourCounts: { [hour: number]: number } = {};
      feedingEvents.forEach(event => {
        const hour = event.timestamp.getHours();
        hourCounts[hour] = (hourCounts[hour] || 0) + 1;
      });

      let favoriteHour: number | null = null;
      let maxCount = 0;
      Object.entries(hourCounts).forEach(([hour, count]) => {
        if (count > maxCount) {
          maxCount = count;
          favoriteHour = Number(hour);
        }
      });

      const favoriteTime = favoriteHour !== null
        ? `${String(favoriteHour).padStart(2, '0')}:00`
        : null;

      res.json({
        totalFeedings: feedingEvents.length,
        averageFoodLevel: Math.round(avgFoodLevel),
        totalFoodConsumed,
        favoriteTime,
        dailyFeedings: dailyFeedingsArray
      });

    } catch (error) {
      console.error('Error fetching statistics:', error);
      res.status(500).json({ error: 'Failed to fetch statistics' });
    }
  });

  return router;
}
