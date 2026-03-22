"""
Web interface for Device Emulator
Allows real-time control and monitoring
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
import os

logger = logging.getLogger(__name__)

# Get the directory where this file is located
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,
            static_folder=os.path.join(basedir, 'static'),
            template_folder=os.path.join(basedir, 'templates'))
CORS(app)

# Global reference to the emulator (will be set from main.py)
emulator = None


def set_emulator(emu):
    """Set the global emulator reference"""
    global emulator
    emulator = emu


@app.route('/')
def index():
    """Main dashboard page — Art Deco simulator"""
    return render_template('simulator.html')


@app.route('/schematic')
def schematic():
    """Emulator schematic page — interactive circuit diagram"""
    return render_template('schematic.html')


@app.route('/analytics')
def analytics():
    """Analytics page with charts and statistics"""
    return render_template('analytics.html')


@app.route('/history')
def history():
    """Feeding history page"""
    return render_template('history.html')


@app.route('/settings')
def settings():
    """Device settings page"""
    return render_template('settings.html')


@app.route('/api/status')
def get_status():
    """Get current device state"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    state = emulator.feeder.get_state()
    return jsonify(state)


@app.route('/api/feed', methods=['POST'])
def feed_now():
    """Trigger immediate feeding"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    data = request.json or {}
    portion = data.get('portion', 50)

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(emulator.feeder.feed_now(portion))
    loop.close()

    return jsonify({'success': success, 'portion': portion})


@app.route('/api/sensors/food', methods=['POST'])
def set_food_level():
    """Manually set food level"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    data = request.json
    level = data.get('level', 50)
    emulator.feeder.sensors.food_level = max(0, min(100, level))

    return jsonify({'success': True, 'level': emulator.feeder.sensors.food_level})


@app.route('/api/sensors/water', methods=['POST'])
def set_water_level():
    """Manually set water level"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    data = request.json
    level = data.get('level', 50)
    emulator.feeder.sensors.water_level = max(0, min(100, level))

    return jsonify({'success': True, 'level': emulator.feeder.sensors.water_level})


@app.route('/api/sensors/temperature', methods=['POST'])
def set_temperature():
    """Manually set temperature"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    data = request.json
    temp = data.get('temperature', 22)
    emulator.feeder.sensors.temperature = max(15, min(35, temp))

    return jsonify({'success': True, 'temperature': emulator.feeder.sensors.temperature})


@app.route('/api/cat/toggle', methods=['POST'])
def toggle_cat_presence():
    """Toggle cat detection"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    current = emulator.feeder.ir_sensor.is_detected()
    emulator.feeder.ir_sensor.force_state(not current)

    return jsonify({'success': True, 'cat_detected': not current})


@app.route('/api/door/toggle', methods=['POST'])
def toggle_door():
    """Toggle door state"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    if emulator.feeder.door_open:
        emulator.feeder.close_door()
    else:
        emulator.feeder.open_door()

    return jsonify({'success': True, 'door_open': emulator.feeder.door_open})


@app.route('/api/schedule', methods=['POST'])
def update_schedule():
    """Update feeding schedule"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    data = request.json
    times = data.get('times', [])

    if times:
        emulator.feeder.set_schedule(times)

    return jsonify({
        'success': True,
        'schedule': emulator.feeder.feeding_schedule,
        'next_feeding': emulator.feeder.next_feeding_time.isoformat() if emulator.feeder.next_feeding_time else None
    })


@app.route('/api/motor/error', methods=['POST'])
def simulate_motor_error():
    """Simulate motor error"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    emulator.feeder.motor_status = 'error'
    return jsonify({'success': True, 'motor_status': 'error'})


@app.route('/api/motor/reset', methods=['POST'])
def reset_motor():
    """Reset motor to idle"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    emulator.feeder.motor_status = 'idle'
    return jsonify({'success': True, 'motor_status': 'idle'})


@app.route('/api/scale/tare', methods=['POST'])
def tare_scale():
    """Tare the bowl scale"""
    if emulator is None:
        return jsonify({'error': 'Emulator not initialized'}), 500

    emulator.feeder.tare_scale()
    return jsonify({'success': True})


def run_web_interface(port=5000):
    """Run the Flask web interface"""
    logger.info(f"Starting web interface on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
