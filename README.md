Desarrollaremos un generador de números aleatorios de alta seguridad para aplicaciones criptográficas, inspirado en sistemas profesionales como Cloudflare, pero adaptado a componentes accesibles. El núcleo del sistema es un recipiente con glicerina y purpurina que genera patrones caóticos impredecibles. Estos patrones se monitorean con:



1. Una cámara OV7670 (controlada por un Arduino UNO) que captura imágenes cada 5 segundos y extrae 64 píxeles aleatorios de ellas.
2. Sensores de movimiento y ambiente (conectados a un segundo Arduino UNO):

* MPU-6050: Detecta vibraciones 3D del recipiente.
* SW-520D (x2): Mide inclinación en ejes X/Y.
* KY-037: Captura ruido ambiental (sonidos imperceptibles).
* DS1302: Reloj de alta precisión para timestamps en microsegundos.



Un tercer Arduino UNO (maestro) coordina el sistema:

Valida que los otros dos Arduinos no hayan sido alterados (checksum de firmware).

Añade su propia entropía con:

* LM35DZ: Mide fluctuaciones térmicas mínimas (0.1°C).
* Sensor de nivel: Detecta ondas en la superficie del fluido.
* Ruido electrónico: Lecturas de pines analógicos desconectados.
* Encripta todos los datos (AES-128) y los envía a una computadora.



Finalmente, un script Python en la PC:

1. Combina los píxeles de la cámara + datos de sensores + entropía del sistema operativo.
2. Usa el algoritmo BLAKE2b para fusionar estas fuentes en una "sopa entrópica".
3. Genera 256 bytes de aleatoriedad verdadera (equivalentes a una clave AES-256) para aplicaciones seguras como:

* Claves SSH
* Encriptación de archivos
* Tokens de seguridad







Lista Completa de Materiales

Componente	Cantidad	Función Clave

Arduino UNO	3	Control de módulos

Cámara OV7670	1	Captura de patrones visuales

MPU-6050	1	Detección de vibraciones 3D

Sensor SW-520D	2	Medición de inclinación

KY-037	1	Captura de ruido ambiental

DS1302 (RTC)	1	Timestamps de µs

LM35DZ	1	Monitoreo de temperatura

Sensor de nivel ultrasónico HC-SR04	1	Detección de ondas en fluido

Recipiente de vidrio	1	Contenedor de glicerina

Glicerina + purpurina	1 set	Medio generador de caos

LEDs blancos	2	Iluminación para cámara

Protoboard	3	Conexiones

Resistencias 10kΩ	8	Pull-ups I2C/OV7670

Resistencias 1kΩ	2	Divisor de voltaje para cámara

Resistencias de 220kΩ	3	Divisor de voltaje para cámara

Cables jumper	60+	Conexiones



Diagrama de Flujo de Operación

\[Fluido] → Patrones caóticos

├─> \[Cámara] → (64 píxeles aleatorios) → \[PC vía USB]

├─> \[Sensores UNO] → (vibraciones + inclinación + sonido + tiempo) → \[Maestro vía I2C]

└─> \[Maestro UNO] → (temperatura + nivel + ruido) + Validación → \[PC vía USB]

↓

\[PC] → Fusión Python → Clave criptográfica (256 bytes)



Asignación de Tareas Clave

1. Integración física:

* Montar sensores en el recipiente (MPU-6050 y SW-520D pegados al vidrio).
* Instalar cámara y LEDs para iluminación uniforme.
* Crear circuito divisor de voltaje para la OV7670.

2\. Programación Arduino:

* Nodo Cámara: Captura de imágenes y extracción de píxeles aleatorios.
* Nodo Sensores: Muestreo sincronizado de 4 sensores + timestamp.
* Nodo Maestro:
*  	Validación de firmware (checksum SHA-256).
*  	Cifrado AES de datos.
*  	Generación de ruido analógico.



3\. Software Python:

* Receptor serial para dos puertos USB (cámara + maestro).
* Algoritmo de fusión entrópica (BLAKE2b + librería secrets).
* Pruebas NIST para verificar aleatoriedad.



4\. Pruebas de seguridad:

* Termómetro infrarrojo para verificar que LM35DZ reporta valores reales.
* Generar 10,000 claves y analizar su distribución.



Innovaciones Clave

* Detección de sabotaje: Si el checksum de firmware no coincide, el maestro activa un LED de alarma.
* Entropía térmica: El LM35DZ detecta cambios de ±0.1°C (imposible de predecir).
* Fusión multimodal: Combina 8 fuentes de entropía (física/visual/digital).
