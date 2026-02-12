import { Server as HTTPServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';

export function setupWebSocket(httpServer: HTTPServer): SocketIOServer {
  const io = new SocketIOServer(httpServer, {
    cors: {
      origin: '*',
      methods: ['GET', 'POST']
    }
  });

  io.on('connection', (socket) => {
    console.log(`🔌 Client connected: ${socket.id}`);

    socket.on('subscribe', (data: { deviceId: string }) => {
      const room = `device_${data.deviceId}`;
      socket.join(room);
      console.log(`📬 Client ${socket.id} subscribed to ${data.deviceId}`);
    });

    socket.on('unsubscribe', (data: { deviceId: string }) => {
      const room = `device_${data.deviceId}`;
      socket.leave(room);
      console.log(`📭 Client ${socket.id} unsubscribed from ${data.deviceId}`);
    });

    socket.on('disconnect', () => {
      console.log(`🔌 Client disconnected: ${socket.id}`);
    });
  });

  return io;
}
