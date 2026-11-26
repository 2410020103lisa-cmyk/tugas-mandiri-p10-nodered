"""
Tugas Individu Pertemuan 10 - Simulasi perangkat ESP32 dengan Python
NIM  : 2410020103
Nama : Siti Norkhalisa

Fungsi:
1. Mengirim data suhu (simulasi DHT22) setiap 3 detik
2. Menerima perintah relay "ON"/"OFF"  -> mengendalikan GPIO 26
3. Menerima nilai PWM 0-255            -> mengendalikan kecerahan LED di GPIO 2
Semua perintah dibalas dengan status (feedback) agar dashboard menampilkan kondisi aktual.
"""
import time
import random
import threading
import paho.mqtt.client as mqtt

# ================= KONFIGURASI =================
NIM = "2410020103"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_CLIENT_ID = f"PythonDevice-{NIM}"

TOPIC_SUHU = f"iot/{NIM}/sensor/suhu"
TOPIC_RELAY = f"iot/{NIM}/aktuator/relay"
TOPIC_PWM = f"iot/{NIM}/aktuator/pwm"
TOPIC_STATUS_RELAY = f"iot/{NIM}/status/relay"
TOPIC_STATUS_PWM = f"iot/{NIM}/status/pwm"

PIN_RELAY = 26   # GPIO 26 -> relay
PIN_LED_PWM = 2  # GPIO 2  -> LED (PWM)
INTERVAL_PUBLISH = 3  # detik

# ================= STATE GLOBAL =================
relay_state = "OFF"
pwm_value = 0

# ================= AKTUATOR =================
# Di ESP32 : digitalWrite(26, ...) dan ledcWrite(...)
# Di Raspberry Pi : ganti isi fungsi ini dengan RPi.GPIO / gpiozero.
def set_relay(state):
    print(f"[GPIO {PIN_RELAY}] Relay -> {state} ({'HIGH' if state == 'ON' else 'LOW'})")

def set_pwm(value):
    persen = round(value / 255 * 100)
    print(f"[GPIO {PIN_LED_PWM}] PWM LED -> {value}/255 (kecerahan {persen}%)")

# ================= CALLBACK MQTT =================
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[MQTT] Terhubung ke broker")
        client.subscribe([(TOPIC_RELAY, 0), (TOPIC_PWM, 0)])
        print(f"[MQTT] Subscribe ke topik: {TOPIC_RELAY}")
        print(f"[MQTT] Subscribe ke topik: {TOPIC_PWM}")
    else:
        print(f"[MQTT] Gagal terhubung, kode: {rc}")

def on_message(client, userdata, msg):
    global relay_state, pwm_value
    payload = msg.payload.decode("utf-8").strip()
    print(f"[MQTT] Pesan masuk [{msg.topic}]: {payload}")

    if msg.topic == TOPIC_RELAY:
        if payload.upper() in ("ON", "1"):
            relay_state = "ON"
        elif payload.upper() in ("OFF", "0"):
            relay_state = "OFF"
        else:
            print(f"[AKTUATOR] Perintah relay tidak dikenal: {payload}")
            return
        set_relay(relay_state)
        client.publish(TOPIC_STATUS_RELAY, relay_state, qos=0)
        print(f"[MQTT] Publish status: {TOPIC_STATUS_RELAY} -> {relay_state}")

    elif msg.topic == TOPIC_PWM:
        try:
            nilai = int(float(payload))
        except ValueError:
            print(f"[AKTUATOR] Nilai PWM bukan angka: {payload}")
            return
        if not 0 <= nilai <= 255:
            print(f"[AKTUATOR] Nilai PWM di luar rentang 0-255: {nilai}")
            return
        pwm_value = nilai
        set_pwm(pwm_value)
        client.publish(TOPIC_STATUS_PWM, str(pwm_value), qos=0)
        print(f"[MQTT] Publish status: {TOPIC_STATUS_PWM} -> {pwm_value}")

def on_disconnect(client, userdata, *args):
    print("[MQTT] Terputus. Mencoba reconnect...")

# ================= SENSOR =================
def baca_suhu():
    """Simulasi DHT22. Di perangkat asli: baca dari sensor, kembalikan None jika gagal."""
    return round(27.0 + random.uniform(-1.5, 1.5), 2)

def publish_loop(client):
    while True:
        try:
            suhu = baca_suhu()
            if suhu is not None:
                client.publish(TOPIC_SUHU, str(suhu), qos=0)
                print(f"[SENSOR] Publish suhu: {TOPIC_SUHU} -> {suhu} °C")
        except Exception as e:
            print(f"[SENSOR] Error: {e}")
        time.sleep(INTERVAL_PUBLISH)

# ================= MAIN =================
def main():
    try:  # paho-mqtt 2.x
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                             client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
    except AttributeError:  # paho-mqtt 1.x
        client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    print(f"[MQTT] Menghubungkan ke {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()
    time.sleep(1)

    threading.Thread(target=publish_loop, args=(client,), daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MAIN] Menghentikan program...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
