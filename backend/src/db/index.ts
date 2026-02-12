import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  log: ['error', 'warn'],
});

export default prisma;

// Initialize default device if not exists
export async function initializeDatabase() {
  try {
    const existingDevice = await prisma.device.findUnique({
      where: { deviceId: 'feeder_001' }
    });

    if (!existingDevice) {
      await prisma.device.create({
        data: {
          deviceId: 'feeder_001',
          name: 'Cat Feeder #1',
          settings: {
            create: {
              petName: 'Whiskers',
              foodType: 'dry',
              caloriesPerGram: 3.5,
              lowFoodThreshold: 20,
              lowWaterThreshold: 20,
              theme: 'light'
            }
          }
        }
      });
      console.log('✅ Default device initialized');
    }

    console.log('✅ Database ready');
  } catch (error) {
    console.error('❌ Database initialization error:', error);
    throw error;
  }
}

// Cleanup old telemetry data (keep last 30 days)
export async function cleanupOldData() {
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

  try {
    const deletedTelemetry = await prisma.telemetry.deleteMany({
      where: {
        timestamp: {
          lt: thirtyDaysAgo
        }
      }
    });

    if (deletedTelemetry.count > 0) {
      console.log(`🧹 Cleaned up ${deletedTelemetry.count} old telemetry records`);
    }
  } catch (error) {
    console.error('❌ Cleanup error:', error);
  }
}
