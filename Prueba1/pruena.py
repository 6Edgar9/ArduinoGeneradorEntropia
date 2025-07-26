#!/usr/bin/env python3
"""
secure_glitter_entropy.py

Captura frames RGB565 desde Arduino vía serial,
detecta partículas brillantes (purpurina),
genera entropía y claves AES‑256, y guarda los resultados en JSON.
"""

import serial
import time
import numpy as np
import cv2
import hashlib
import json
import os

# ========== CONFIGURACIÓN ==========
PORT           = 'COM6'         # Cambia a tu puerto: COMx en Windows o /dev/ttyUSB0 en Linux
BAUDRATE       = 500_000
WIDTH, HEIGHT  = 320, 240
FRAME_SIZE     = WIDTH * HEIGHT * 2
POOL_SIZE      = 5              # N° de muestras por clave
BRIGHT_THRESH  = 200            # Umbral de brillo (canal V de HSV)
MAX_PARTICLES  = 10             # Máximo de puntos de purpurina
OUT_FILE       = 'entropia_purpurina.json'

# ========== FUNCIONES ==========

def open_serial():
    """Inicializa y limpia el puerto serial"""
    ser = serial.Serial(PORT, BAUDRATE, timeout=0.1)
    time.sleep(2)
    ser.reset_input_buffer()
    while ser.in_waiting:
        ser.read(ser.in_waiting)
    return ser

def read_frame(ser):
    """Lee un frame completo de 320x240 RGB565"""
    buf = bytearray()
    while len(buf) < FRAME_SIZE:
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            buf += chunk
    return bytes(buf[:FRAME_SIZE])

def decode_rgb565(frame_buf):
    """Convierte RGB565 a imagen RGB"""
    pix = np.frombuffer(frame_buf, dtype=np.uint8).reshape(-1, 2)
    # Byte alto primero, luego bajo
    pix16 = (pix[:,0].astype(np.uint16) << 8) | pix[:,1].astype(np.uint16)
    r = ((pix16 & 0xF800) >> 11) << 3
    g = ((pix16 & 0x07E0) >> 5)  << 2
    b = ((pix16 & 0x001F)      ) << 3
    return np.dstack((r, g, b)).reshape((HEIGHT, WIDTH, 3)).astype(np.uint8)

def extract_glitter_entropy(img):
    """Extrae características de puntos brillantes como entropía"""
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    V = hsv[...,2]
    _, mask = cv2.threshold(V, BRIGHT_THRESH, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    conts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    entropy = bytearray()
    N = min(len(conts), MAX_PARTICLES)
    entropy.append(N & 0xFF)

    for c in conts[:N]:
        M = cv2.moments(c)
        if M['m00'] == 0:
            entropy += b'\x00\x00\x00'
            continue
        x = int((M['m10']/M['m00']) / WIDTH * 255) & 0xFF
        y = int((M['m01']/M['m00']) / HEIGHT * 255) & 0xFF
        # Intensidad media del contorno
        mask_roi = np.zeros_like(V, dtype=np.uint8)
        cv2.drawContours(mask_roi, [c], -1, 255, -1)
        I = int(cv2.mean(V, mask=mask_roi)[0]) & 0xFF
        entropy += bytes([x, y, I])

    # Timestamp (últimos 4 bytes)
    t = int(time.time() * 1_000_000) & 0xFFFFFFFF
    entropy += t.to_bytes(4, 'little')
    return entropy, t

def fuse_entropy(pool):
    """Genera clave AES‑256 fusionando muestras"""
    h = hashlib.blake2b(digest_size=32)
    for e in pool:
        h.update(e)
    return h.digest()

def save_entropy_record(timestamp, key_bytes):
    """Guarda la clave generada como JSON (una por línea)"""
    record = {
        "timestamp_us": timestamp,
        "source": "purpurina",
        "entropy_hex": key_bytes.hex()
    }
    with open(OUT_FILE, "a") as f:
        json.dump(record, f)
        f.write("\n")
    print("✅ Clave guardada:", record["entropy_hex"])

# ========== PROGRAMA PRINCIPAL ==========

def main():
    print(f"Conectando al puerto {PORT} a {BAUDRATE} bps…")
    ser = open_serial()
    entropy_pool = []

    try:
        while True:
            frame_buf = read_frame(ser)
            img = decode_rgb565(frame_buf)
            entropy, ts = extract_glitter_entropy(img)
            entropy_pool.append(entropy)
            print(f"🧪 Muestra {len(entropy_pool)}/{POOL_SIZE} capturada @ {ts}")

            if len(entropy_pool) >= POOL_SIZE:
                key = fuse_entropy(entropy_pool)
                save_entropy_record(ts, key)
                entropy_pool.clear()

    except KeyboardInterrupt:
        print("\n🛑 Interrumpido por el usuario.")
    finally:
        ser.close()
        print("🔌 Puerto serial cerrado.")

if __name__ == '__main__':
    main()
