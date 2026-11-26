# Dashboard Node-RED untuk Kontrol Relay dan Monitoring Suhu

- Nama : Siti Norkhalisa
- NIM  : 2410020103
- Kelas: SI 5A Reg Bjm Pagi

Penugasan Individu (Proyek Mini) Pertemuan 10. Perangkat ESP32 disimulasikan dengan skrip Python,
broker memakai Mosquitto lokal, dan antarmuka memakai Node-RED Dashboard.

## Topik MQTT

| Fungsi | Topik | Arah |
|---|---|---|
| Suhu | `iot/2410020103/sensor/suhu` | Python -> Node-RED |
| Relay (ON/OFF, GPIO 26) | `iot/2410020103/aktuator/relay` | Node-RED -> Python |
| PWM (0-255, GPIO 2) | `iot/2410020103/aktuator/pwm` | Node-RED -> Python |
| Status relay (feedback) | `iot/2410020103/status/relay` | Python -> Node-RED |
| Status PWM (feedback) | `iot/2410020103/status/pwm` | Python -> Node-RED |

## Isi repositori

- `iot_device_nim.py` : kode perangkat (suhu tiap 3 detik, relay GPIO 26, PWM GPIO 2)
- `flow-tugas-mandiri-p10.json` : flow Node-RED (mqtt in, ui_gauge, ui_switch, ui_slider)
- `screenshot-dashboard.png` : tampilan dashboard yang berjalan
- `video-demo.mp4` : video demo kontrol dari dashboard ke perangkat (maks. 60 detik)

## Cara menjalankan

1. Pastikan Mosquitto berjalan di `localhost:1883`.
2. `pip install paho-mqtt` lalu `python iot_device_nim.py`.
3. Jalankan `node-red`, pasang palet `node-red-dashboard`, lalu Menu > Import > pilih file JSON > Deploy.
4. Buka `http://localhost:1880/ui`, tab **Tugas Mandiri P10**.
