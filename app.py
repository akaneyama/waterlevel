import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
import eventlet

# Monkey patch untuk mengizinkan konkurensi antara Flask dan MQTT
eventlet.monkey_patch()

# --- PENGATURAN ---
MQTT_BROKER = "127.0.0.1"  # Gunakan IP langsung untuk menghindari masalah DNS
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/waterlevel"

# Inisialisasi Aplikasi Flask dan SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci-rahasia-yang-aman!'
socketio = SocketIO(app, async_mode='eventlet')

# Variabel global untuk menyimpan data terakhir
app_data = {
    "ketinggian_air": 0.0
}

# --- Logika MQTT (Akan berjalan di thread terpisah) ---
def mqtt_thread_worker():
    """Fungsi ini berisi semua logika untuk klien MQTT."""
    
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("MQTT Terhubung!")
            client.subscribe(MQTT_TOPIC)
        else:
            print(f"Koneksi MQTT Gagal, kode: {rc}")

    def on_message(client, userdata, msg):
        try:
            # Mengambil data, menyimpannya, dan mengirimkannya ke browser via WebSocket
            level = float(msg.payload.decode('utf-8'))
            app_data['ketinggian_air'] = level
            print(f"---------------------------------")
            print(f"Data diterima: {level} cm. Mengirim ke dashboard...")
            # Mengirim event 'update_data' ke semua klien yang terhubung
            socketio.emit('update_data', {'level': level})
        except Exception as e:
            print(f"Error memproses pesan: {e}")

    # Menggunakan versi API callback yang lebih baru
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    # Terus mencoba terhubung jika gagal
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_forever()
        except Exception as e:
            print(f"Tidak dapat terhubung ke MQTT Broker. Mencoba lagi dalam 5 detik... Error: {e}")
            time.sleep(5)

# --- Rute Flask & Event SocketIO ---
@app.route('/')
def index():
    # Mengirim nilai awal ke template untuk mencegah error saat render pertama kali.
    # Nilai ini akan segera diperbarui oleh WebSocket.
    return render_template('index.html', water_level=app_data['ketinggian_air'])

@socketio.on('connect')
def handle_connect():
    # Saat klien baru terhubung, kirim data terakhir agar halaman tidak kosong
    print('Klien terhubung ke dashboard')
    socketio.emit('update_data', {'level': app_data['ketinggian_air']})

# --- Fungsi Utama ---
if __name__ == '__main__':
    # 1. Buat dan mulai thread MQTT di latar belakang
    print("Memulai thread MQTT di background...")
    mqtt_thread = threading.Thread(target=mqtt_thread_worker)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # 2. Jalankan server dengan SocketIO, bukan app.run() standar
    print("Menjalankan server web Flask dengan SocketIO di http://0.0.0.0:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
