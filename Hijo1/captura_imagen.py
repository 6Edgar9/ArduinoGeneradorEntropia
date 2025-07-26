#!/usr/bin/env python3
"""
capture_ov7670_try_formats.py

Intenta decodificar cada frame en:
  – RGB565 (alto<<8|bajo)
  – YUV422 (Y0U Y1V)
y guarda ambos para que compares.
"""

import serial, os, time
import numpy as np
from PIL import Image

# — CONFIGURACIÓN —
PORT       = 'COM6'
BAUDRATE   = 500000
W, H       = 320, 240
FRAME_SIZE = W * H * 2     # bytes (RGB565) o W*H*2 = W*H pixels en YUYV
OUT_DIR    = 'frames_test'

# Asegura carpeta
os.makedirs(OUT_DIR, exist_ok=True)

def save_rgb565(buf, count):
    pix = np.frombuffer(buf, np.uint8).reshape(-1,2)
    # prueba con both orders:
    for name, (hi, lo) in [('high-low',(0,1)), ('low-high',(1,0))]:
        pix16 = (pix[:,hi].astype(np.uint16)<<8) | pix[:,lo].astype(np.uint16)
        r = ((pix16 & 0xF800) >>11) <<3
        g = ((pix16 & 0x07E0) >>5 ) <<2
        b = ((pix16 & 0x001F)     ) <<3
        img = np.dstack((r,g,b)).reshape((H,W,3)).astype(np.uint8)
        path = os.path.join(OUT_DIR, f'frame{count:04d}_rgb565_{name}.png')
        Image.fromarray(img).save(path)
        print("▶ Guardado", path)

def save_yuv422(buf, count):
    arr = np.frombuffer(buf, np.uint8)
    rgb = np.zeros((H,W,3), np.uint8)
    i = 0
    for y in range(H):
        for x in range(0,W,2):
            Y0, U, Y1, V = arr[i], arr[i+1], arr[i+2], arr[i+3]
            i += 4
            # Conversión básica
            for xi, Y in [(x, Y0), (x+1, Y1)]:
                C = Y - 16
                D = U - 128
                E = V - 128
                R = 1.164*C + 1.596*E
                G = 1.164*C - 0.392*D - 0.813*E
                B = 1.164*C + 2.017*D
                rgb[y,xi,0] = np.clip(R,0,255)
                rgb[y,xi,1] = np.clip(G,0,255)
                rgb[y,xi,2] = np.clip(B,0,255)
    path = os.path.join(OUT_DIR, f'frame{count:04d}_yuv422.png')
    Image.fromarray(rgb).save(path)
    print("▶ Guardado", path)

def main():
    ser = serial.Serial(PORT, BAUDRATE, timeout=0.1)
    time.sleep(2)
    ser.reset_input_buffer()
    # limpia resto
    while ser.in_waiting:
        ser.read(ser.in_waiting)

    buf = bytearray()
    count = 0
    print("Arrancando captura… Ctrl‑C para parar.")
    try:
        while True:
            chunk = ser.read(ser.in_waiting or 1)
            if chunk:
                buf += chunk
            if len(buf) >= FRAME_SIZE:
                frame = bytes(buf[:FRAME_SIZE])
                print(f"\n==> Frame {count}")
                save_rgb565(frame, count)
                save_yuv422(frame, count)
                count += 1
                buf = buf[FRAME_SIZE:]
    except KeyboardInterrupt:
        print("\nInterrumpido.")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
