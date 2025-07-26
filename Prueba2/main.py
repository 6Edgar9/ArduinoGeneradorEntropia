import tkinter as tk
from tkinter import ttk
import serial
import threading
import json
import hashlib
import secrets
import time
from datetime import datetime

# =======================
# CONFIGURACIÓN DE PUERTOS
# =======================
PUERTO_ESCLAVO1 = 'COM9'
PUERTO_MAESTRO  = 'COM12'
BAUDRATE = 9600

# =======================
# FUNCIONES AUXILIARES
# =======================

def leer_serial(puerto):
    try:
        ser = serial.Serial(puerto, BAUDRATE, timeout=2)
        time.sleep(2)
        data = ser.readline().decode('utf-8', errors='ignore').strip()
        ser.close()
        if data:
            return json.loads(data)
    except Exception as e:
        print(f"[ERROR] Puerto {puerto}: {e}")
    return {}

def fusionar_entropia(ent1, ent2):
    sys_rand = secrets.token_bytes(32)
    combined = json.dumps(ent1, sort_keys=True).encode() + json.dumps(ent2, sort_keys=True).encode() + sys_rand
    return hashlib.blake2b(combined, digest_size=32).hexdigest()

# =======================
# INTERFAZ TKINTER
# =======================

class BancoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Token Bancario Seguro")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        self.token_var = tk.StringVar()
        self.timer_var = tk.StringVar(value="30")

        ttk.Label(root, text="Token de Seguridad", font=("Helvetica", 16, "bold")).pack(pady=10)
        self.token_label = ttk.Label(root, textvariable=self.token_var, font=("Courier", 18))
        self.token_label.pack(pady=5)

        ttk.Label(root, text="Válido por (segundos):", font=("Helvetica", 10)).pack()
        self.timer_label = ttk.Label(root, textvariable=self.timer_var, font=("Helvetica", 14))
        self.timer_label.pack()

        self.generar_token()
        self.actualizar_timer()

    def generar_token(self):
        print("[INFO] Leyendo datos para generar token...")
        ent1 = leer_serial(PUERTO_ESCLAVO1)
        ent2 = leer_serial(PUERTO_MAESTRO)
        token = fusionar_entropia(ent1, ent2)
        self.token_var.set(token[:16].upper())  # Mostramos solo 16 caracteres
        self.expira_en = 30

    def actualizar_timer(self):
        if self.expira_en <= 0:
            self.generar_token()
        self.timer_var.set(str(self.expira_en))
        self.expira_en -= 1
        self.root.after(1000, self.actualizar_timer)

# =======================
# INICIO DE LA APLICACIÓN
# =======================
if __name__ == "__main__":
    root = tk.Tk()
    app = BancoApp(root)
    root.mainloop()
