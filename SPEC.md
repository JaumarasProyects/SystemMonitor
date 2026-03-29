# SystemMonitor - Monitor de Sistema para Windows

## 1. Project Overview

**Nombre del proyecto:** SystemMonitor  
**Tipo:** Aplicación de escritorio Windows  
**Core functionality:** Aplicación de monitorización del sistema que muestra información detallada del hardware, software instalado, estado de memoria, procesos en ejecución y uso de recursos con visualizaciones gráficas.  
**Target users:** Usuarios de Windows que quieren conocer el estado de su ordenador.

---

## 2. UI/UX Specification

### Layout Structure

- **Ventana principal:** 1200x800 píxeles, redimensionable (mínimo 900x600)
- **Header:** Barra superior con título y selector de tema
- **Sidebar:** Panel lateral izquierdo (220px) con navegación por secciones
- **Content Area:** Área principal derecha que cambia según la sección seleccionada
- **Footer:** Barra de estado con información de última actualización y botón de Chat IA
- **Chat Widget:** Ventana flotante accesible desde el footer, con contexto de todos los paneles

### Navegación (Sidebar)
1. **Dashboard** - Vista general con gráficos principales
2. **Sistema** - Información del hardware y SO
3. **Memoria** - Estado de RAM y almacenamiento
4. **Procesos** - Lista de procesos en ejecución
5. **Red** - Estado de conexión de red
6. **Puertos** - Estado y gestión de puertos de red
7. **Software** - Programas instalados
8. **Cachés y Cookies** - Gestionar almacenamiento local de navegadores
9. **Análisis IA** - Análisis del sistema con Ollama (LLM local)

### Visual Design

**Paleta de colores (Dark Theme):**
- Background principal: `#1a1a2e`
- Background secundario: `#16213e`
- Background cards: `#0f3460`
- Color primario: `#00d9ff` (cyan brillante)
- Color secundario: `#e94560` (rojo coral)
- Color éxito: `#00ff88` (verde neón)
- Color warning: `#ffaa00` (naranja)
- Texto principal: `#ffffff`
- Texto secundario: `#a0a0a0`
- Bordes: `#2a2a4a`

**Paleta de colores (Light Theme):**
- Background principal: `#f5f5f5`
- Background secundario: `#ffffff`
- Background cards: `#ffffff`
- Color primario: `#0066cc`
- Color secundario: `#cc3366`
- Color éxito: `#00aa55`
- Color warning: `#ff8800`
- Texto principal: `#1a1a1a`
- Texto secundario: `#666666`
- Bordes: `#dddddd`

**Tipografía:**
- Títulos: Segoe UI Semibold, 18px
- Subtítulos: Segoe UI Semibold, 14px
- Cuerpo: Segoe UI, 12px
- Monospace (datos técnicos): Consolas, 11px

**Espaciado:**
- Padding cards: 20px
- Gap entre elementos: 15px
- Border radius: 12px
- Margin sidebar: 10px

**Efectos visuales:**
- Sombras en cards: `0 4px 15px rgba(0,0,0,0.3)`
- Hover en botones: brightness(1.1)
- Transiciones: 0.2s ease
- Gráficos con gradientes sutiles

### Components

**Cards de información:**
- Título con icono
- Valor principal grande
- Detalles secundarios
- Indicador de estado (barra o porcentaje)

**Gráficos:**
- Gráfico circular para uso de memoria
- Gráfico de barras para uso por núcleo CPU
- Gráfico de líneas para historial de uso (últimos 60 segundos)
- Barras de progreso para disco

**Tablas:**
- Encabezado con fondo semi-transparente
- Filas alternadas
- Ordenable por columna
- Highlight en hover

**Botones de navegación:**
- Icono + texto
- Indicador de sección activa
- Efecto hover con borde izquierdo iluminado

---

## 3. Functional Specification

### Módulo 1: Dashboard
- **Gráfico circular:** Uso de RAM (usado/libre)
- **Gráfico circular:** Uso de disco principal
- **Gráfico de líneas:** CPU usage en tiempo real (60s historial)
- **Cards resumen:** CPU%, RAM%, Disco%, Network
- **Sistema de alertas:** Notificaciones cuando recursos > 90%

### Módulo 2: Sistema
- **Información general:**
  - Nombre del equipo
  - Sistema operativo y versión
  - Arquitectura (x64/x86)
  - Usuario actual
  - Dominio/Workgroup
  - Fecha y hora del sistema
  - Tiempo de actividad (uptime)
- **CPU:**
  - Nombre del procesador
  - Núcleos físicos/lógicos
  - Frecuencia actual/máxima
  - Porcentaje de uso
  - Uso por núcleo (barras)
  - Caché L1/L2/L3
- **GPU:**
  - Nombre de tarjeta gráfica
  - Memoria dedicada
  - Driver version
  - Resolución actual
  - Porcentaje de uso GPU
  - Estado de la GPU
- **Placa base:**
  - Fabricante
  - Modelo
  - Versión BIOS

### Módulo 3: Memoria
- **RAM:**
  - Total instalada
  - Disponible/usada
  - Porcentaje de uso
  - Gráfico circular
  - Historial de uso (gráfico de líneas)
- **Almacenamiento:**
  - Lista de discos (C:, D:, etc.)
  - Para cada disco:
    - Letra y etiqueta
    - Tipo (SSD/HDD)
    - Sistema de archivos
    - Total/Gancho/Disponible
    - Porcentaje usado
    - Barra de progreso
  - Gráfico de barras comparativo

### Módulo 4: Procesos
- **Tabla de procesos con columnas:**
  - Nombre del proceso
  - PID
  - CPU%
  - Memoria (MB)
  - Estado
  - Usuario
- **Funcionalidades:**
  - Ordenar por columna
  - Filtrar por nombre
  - Buscar en tiempo real
  - Top 10 procesos por CPU/Memoria
  - Botón refrescar

### Módulo 5: Red
- **Adaptadores de red:**
  - Lista de adaptadores
  - Estado (conectado/desconectado)
  - Tipo (Ethernet/WiFi)
  - IP address
  - Máscara de subred
  - Gateway
  - DNS servers
- **Estadísticas:**
  - Bytes enviados/recibidos
  - Paquetes enviados/recibidos
  - Velocidad actual (Mbps)

### Módulo 6: Puertos de Red
- **Conexiones monitorizadas:**
  - Puerto (número)
  - Estado (LISTEN, ESTABLISHED, TIME_WAIT, etc.)
  - Dirección local
  - Dirección remota
  - PID del proceso
  - Nombre del proceso
- **Tarjetas de resumen:**
  - Puertos en estado LISTEN
  - Conexiones ESTABLISHED
  - Conexiones TIME_WAIT
  - Total de conexiones
- **Funcionalidades:**
  - Buscar/filtrar por puerto, proceso o dirección
  - Botón actualizar para refrescar datos
  - Botón "Terminar" para cerrar proceso en un puerto
  - Indicador de última actualización
- **Estados de color:**
  - Verde: LISTEN
  - Azul: ESTABLISHED
  - Amarillo: TIME_WAIT
  - Rojo: CLOSE_WAIT

### Módulo 7: Software Instalado
- **Lista de programas desde registro:**
  - Nombre del programa
  - Versión
  - Fecha de instalación
  - Editor
- **Funcionalidades:**
  - Búsqueda/filtrado
  - Ordenar por nombre/fecha
  - Exportar a CSV

### Módulo 8: Cachés y Cookies
- **Navegadores soportados:**
  - Google Chrome
  - Microsoft Edge
  - Mozilla Firefox
  - Opera
  - Brave
  - Vivaldi
- **Información mostrada:**
  - Tamaño de caché por navegador (MB/GB)
  - Número de cookies almacenadas
  - Tamaño de la base de datos de cookies
- **Funcionalidades:**
  - Botón actualizar para reescanear
  - Botón limpiar caché por navegador
  - Botón limpiar cookies por navegador
  - Botón limpiar toda la caché
  - Indicador de estado con resultado de operaciones

### Módulo 9: Análisis IA (Ollama)
- **Conexión con Ollama:**
  - Detecta automáticamente modelos instalados via API REST (localhost:11434)
  - Muestra solo los modelos realmente disponibles en el sistema
  - Selecciona automáticamente el último modelo instalado por defecto
  - Indica estado de conexión y número de modelos encontrados
- **Tipos de análisis:**
  - **Análisis General:** Estado del sistema, memoria, procesos, software
  - **Análisis de Seguridad:** Revisión completa de vulnerabilidades
- **Datos recopilados para análisis general:**
  - Información del sistema (SO, arquitectura, uptime)
  - CPU (modelo, núcleos, frecuencia, uso)
  - GPU (modelo, memoria, driver, resolución, uso)
  - Memoria RAM (total, usado, libre, porcentaje)
  - Almacenamiento (cada disco con uso)
  - Red (adaptadores, IPs, bytes transferidos)
  - Procesos (top 30 por CPU)
  - Software instalado (primeros 20 + contador)
- **Datos recopilados para análisis de seguridad:**
  - Estado del Firewall de Windows
  - Estado del Antivirus (Windows Defender)
  - Procesos sospechosos (cracks, keygens, miners, RATs)
  - Puertos abiertos listening
  - Programas de inicio automático
  - Recursos compartidos de red
  - Usuarios recientes en el sistema
- **Respuesta del LLM incluye (Análisis General):**
  - Valoración general del sistema
  - Análisis de uso de memoria
  - Procesos críticos identificados
  - Evaluación del software instalado
  - Recomendaciones de optimización
- **Respuesta del LLM incluye (Análisis de Seguridad):**
  - Puntuación de seguridad (0-100)
  - Aspectos positivos de seguridad
  - Vulnerabilidades detectadas
  - Amenazas potenciales con nivel de riesgo
  - Recomendaciones de seguridad priorizadas
  - Acciones inmediatas recomendadas
- **Chat con IA (Widget Compartido):**
  - Accesible desde el botón "💬 Chat IA" en el footer
  - Ventana flotante que puede abrirse/cerrarse en cualquier momento
  - Selector de modelo de Ollama
  - Acceso a contexto de TODOS los paneles del sistema:
    - Dashboard: CPU, RAM, disco, red
    - Sistema: CPU, GPU, información general
    - Memoria: RAM y almacenamiento detallado
    - Procesos: Top procesos por CPU y memoria
    - Red: Adaptadores y estadísticas
    - Puertos: Conexiones de red
    - Software: Programas instalados
    - Cachés: Navegadores y cookies
    - Análisis IA: Resultados de análisis previos
  - Botón de voz (🔊) para reproducir respuestas con Edge TTS
  - Mensajes del usuario (derecha) y del asistente (izquierda)
  - Indicador "Pensando..." mientras espera respuesta
  - Manejo de errores con mensajes claros
- **Síntesis de voz (Edge TTS):**
  - Usa voces neuronales de Microsoft Edge
  - Voz predeterminada: es-ES-AlvaroNeural (voz masculina española)
  - Botón toggle para activar/desactivar voz
  - Las respuestas del LLM se leen en voz alta automáticamente si la voz está activada

---

## 4. Technical Stack

- **Python 3.10+**
- **psutil:** Información del sistema
- **customtkinter:** Interfaz gráfica moderna
- **matplotlib:** Gráficos embebidos
- **pillow:** Manejo de iconos
- **winreg:** Leer registro de Windows
- **requests:** Conexión con API de Ollama
- **edge-tts:** Síntesis de voz con voces neuronales de Microsoft

---

## 5. Acceptance Criteria

1. ✅ Aplicación inicia sin errores
2. ✅ Sidebar permite navegar entre 9 secciones
3. ✅ Dashboard muestra 4 gráficos principales actualizados
4. ✅ Sección Sistema muestra toda la información de CPU, GPU y placa base
5. ✅ Sección Memoria muestra RAM y todos los discos con barras de progreso
6. ✅ Sección Procesos muestra tabla ordenable y filtrable
7. ✅ Sección Red muestra adaptadores y estadísticas
8. ✅ Sección Puertos muestra conexiones de red y permite terminar procesos
9. ✅ Sección Software lista programas instalados
 10. ✅ Sección Cachés y Cookies muestra y permite limpiar datos de navegadores
 11. ✅ Sección Análisis IA incluye análisis general, análisis de seguridad con Ollama y chat interactivo
 12. ✅ Tema claro/oscuro funciona correctamente
 13. ✅ Los datos se actualizan automáticamente cada 2 segundos
 14. ✅ La interfaz es responsive y redimensionable
 15. ✅ Gráficos se actualizan en tiempo real sin parpadeos
 16. ✅ Chat IA accesible desde todos los paneles mediante botón en footer
 17. ✅ Chat tiene acceso al contexto de datos de todos los paneles
 18. ✅ Botón de voz para reproducir respuestas del LLM con Edge TTS
