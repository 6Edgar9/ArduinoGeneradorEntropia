# Generador de Números Aleatorios Criptográficos con Entropía Física

Este proyecto desarrolla un **generador de números aleatorios de alta seguridad** para aplicaciones criptográficas, inspirado en sistemas profesionales como Cloudflare, pero utilizando componentes accesibles.

El núcleo del sistema es un **recipiente con glicerina y purpurina** que genera **patrones caóticos impredecibles**, capturados y procesados para generar claves criptográficas de 256 bytes.

---

## Componentes y Funcionamiento

### 1. Captura de Entropía

* **Cámara OV7670 (Nodo 1 - Arduino UNO):**
  Captura imágenes cada 5 segundos y extrae **64 píxeles aleatorios** para generar entropía visual.

* **Sensores de movimiento y ambiente (Nodo 2 - Arduino UNO):**

  * **MPU-6050:** Vibraciones 3D del recipiente.
  * **SW-520D (x2):** Inclinación en ejes X/Y.
  * **KY-037:** Ruido ambiental (sonidos imperceptibles).
  * **DS1302 (RTC):** Timestamps con microsegundos.

* **Nodo Maestro (Arduino UNO):**

  * Valida que los otros nodos no hayan sido alterados (checksum de firmware SHA-256).
  * Añade entropía propia:

    * **LM35DZ:** Monitoreo de fluctuaciones térmicas mínimas (0.1°C).
    * **Sensor de nivel:** Detecta ondas en el fluido.
    * **Ruido electrónico:** Lecturas de pines analógicos desconectados.
  * Cifra todos los datos con **AES-128** y los envía al PC.

### 2. Procesamiento en la PC (Python)

1. Combina datos de:

   * Cámara
   * Sensores físicos
   * Entropía del sistema operativo
2. Fusión con **BLAKE2b** y generación de una “sopa entrópica”.
3. Genera **256 bytes de aleatoriedad** equivalentes a una clave AES-256.
4. Aplicaciones:

   * Claves SSH
   * Encriptación de archivos
   * Tokens de seguridad

---

## Lista de Materiales

| Componente                          | Cantidad | Función Clave                |
| ----------------------------------- | -------- | ---------------------------- |
| Arduino UNO                         | 3        | Control de módulos           |
| Cámara OV7670                       | 1        | Captura de patrones visuales |
| MPU-6050                            | 1        | Vibraciones 3D               |
| Sensor SW-520D                      | 2        | Medición de inclinación      |
| KY-037                              | 1        | Ruido ambiental              |
| DS1302 (RTC)                        | 1        | Timestamps en µs             |
| LM35DZ                              | 1        | Monitoreo de temperatura     |
| Sensor de nivel ultrasónico HC-SR04 | 1        | Ondas en fluido              |
| Recipiente de vidrio                | 1        | Contenedor de glicerina      |
| Glicerina + purpurina               | 1 set    | Medio generador de caos      |
| LEDs blancos                        | 2        | Iluminación de cámara        |
| Protoboard                          | 3        | Conexiones                   |
| Resistencias 10kΩ                   | 8        | Pull-ups I2C/OV7670          |
| Resistencias 1kΩ                    | 2        | Divisor de voltaje cámara    |
| Resistencias 220kΩ                  | 3        | Divisor de voltaje cámara    |
| Cables jumper                       | 60+      | Conexiones                   |

---

## Diagrama de Flujo de Operación

```
[Fluido] → Patrones caóticos
├─> [Cámara] → (64 píxeles aleatorios) → [PC vía USB]
├─> [Sensores UNO] → (vibración + inclinación + sonido + tiempo) → [Maestro vía I2C]
└─> [Maestro UNO] → (temperatura + nivel + ruido) + Validación → [PC vía USB]

[PC] → Fusión Python → Clave criptográfica (256 bytes)
```

---

## Asignación de Tareas

### Integración Física

* Montaje de sensores en el recipiente (MPU-6050 y SW-520D).
* Instalación de cámara y LEDs para iluminación uniforme.
* Creación de circuito divisor de voltaje para la OV7670.

### Programación Arduino

* **Nodo Cámara:** Captura de imágenes y extracción de píxeles aleatorios.
* **Nodo Sensores:** Muestreo sincronizado de vibraciones, inclinación, sonido y timestamps.
* **Nodo Maestro:** Validación de firmware, cifrado AES de datos, generación de ruido analógico.

### Software Python

* Receptor serial para nodos cámara y maestro.
* Algoritmo de fusión entrópica (BLAKE2b + `secrets`).
* Pruebas NIST para verificación de aleatoriedad.

### Pruebas de Seguridad

* Termómetro infrarrojo para validar LM35DZ.
* Generación de 10,000 claves para análisis de distribución.

---

## Innovaciones Clave

* **Detección de sabotaje:** Maestro activa LED si checksum no coincide.
* **Entropía térmica:** Fluctuaciones de ±0.1°C.
* **Fusión multimodal:** Combina 8 fuentes de entropía (visual, física, digital).

---

#### Dios, Assembly y la Patria
#### Edrem

---

Desarrollado con fines académicos y de práctica en Python.