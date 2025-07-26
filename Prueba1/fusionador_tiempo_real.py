import json
import hashlib
import secrets
import os
import time

# === Archivos de entrada/salida ===
ENTROPIA_1 = "entropia_purpurina.json"
ENTROPIA_2 = "entropia_padre.json"
KEY_LATEST = "clave_final.hex"
KEY_HISTORY = "claves_generadas.txt"

ultima_firma = ""

def cargar_entropia(path):
    if not os.path.exists(path): return b""
    try:
        with open(path, "r") as f:
            contenido = json.load(f)
            return json.dumps(contenido, sort_keys=True).encode("utf-8")
    except:
        return b""

def generar_clave(entropia_combinada):
    h = hashlib.blake2b(digest_size=32)
    h.update(entropia_combinada)
    return h.digest()

def main():
    global ultima_firma
    print("🔁 Fusionador en tiempo real con historial activo...")

    while True:
        datos1 = cargar_entropia(ENTROPIA_1)
        datos2 = cargar_entropia(ENTROPIA_2)
        sistema = secrets.token_bytes(32)

        combinado = datos1 + datos2 + sistema
        firma = hashlib.sha256(combinado).hexdigest()

        if firma != ultima_firma:
            clave = generar_clave(combinado)
            clave_hex = clave.hex()

            # Guardar clave actual
            with open(KEY_LATEST, "w") as f:
                f.write(clave_hex)

            # Añadir clave al historial
            with open(KEY_HISTORY, "a") as f:
                f.write(clave_hex + "\n")

            print(f"[{time.strftime('%H:%M:%S')}] 🔐 Clave nueva: {clave_hex}")
            ultima_firma = firma

        time.sleep(3)  # Esperar 3 segundos

if __name__ == "__main__":
    main()
