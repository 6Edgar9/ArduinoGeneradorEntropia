import serial
import json
import time
from datetime import datetime

# === CONFIGURACIÓN ===
PORT = 'COM5'           # Cambia al puerto correcto
BAUDRATE = 9600
OUTPUT_FILE = 'entropia_padre.json'

# === INICIALIZAR SERIAL ===
ser = serial.Serial(PORT, BAUDRATE, timeout=2)
time.sleep(2)  # Esperar conexión

print(f"[{datetime.now()}] Escuchando puerto {PORT}...")

try:
    with open(OUTPUT_FILE, 'a') as f:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                timestamp = datetime.now().isoformat()
                data['captured_at'] = timestamp
                f.write(json.dumps(data) + '\n')
                f.flush()  # <-- Fuerza la escritura inmediata en disco
                print(f"[{timestamp}] Datos recibidos: {data}")
            except json.JSONDecodeError as e:
                print(f"[ERROR] Línea no válida: {line}")
except KeyboardInterrupt:
    print("\n[FIN] Captura detenida por el usuario.")
finally:
    ser.close()
