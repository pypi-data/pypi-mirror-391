# ColorMixer: Gestión Integral de Colores para Automóviles
---
ColorMixer es una librería Python desarrollada como proyecto académico que demuestra la implementación práctica de patrones de diseño de software y estructuras de datos avanzadas. El proyecto simula un sistema de gestión de colores para inventarios de vehículos, combinando conceptos teóricos de ingeniería de software con una aplicación práctica y funcional.

# Tabla de contenido

* Sobre este Proyecto
* Características Implementadas
* Patrones de Diseño
* Estructuras de Datos
* Instalación
* Uso Básico
* Ejemplos de Código
* API Referencia
* Arquitectura del Proyecto
* Testing
* Contribuciones Académicas

# Sobre este Proyecto

Este proyecto fue desarrollado como parte de un curso de programación orientada a objetos y estructuras de datos. El objetivo principal es demostrar la aplicación práctica de:

Patrones de diseño de software (Factory, Builder, Singleton)
Estructuras de datos personalizadas (listas enlazadas, nodos especializados)
Principios SOLID en el diseño de clases
Persistencia de datos mediante archivos JSON
Modularidad y organización de código Python

* Perfiles de Usuarios Potenciales

- Diseñadores Gráficos y Web: Podrían usar la librería para experimentar con paletas de colores, calcular combinaciones para logotipos o interfaces de usuario, y garantizar la coherencia en sus proyectos. Les serviría para previsualizar rápidamente los resultados de mezclas complejas sin necesidad de software de diseño costoso.

- Artistas y Pintores: Les sería útil para planificar sus obras, especialmente en medios digitales o para mezclar pigmentos en la vida real. La capacidad de guardar mezclas personalizadas les permitiría recrear tonos específicos de manera precisa.

- Desarrolladores de Videojuegos: Utilizarían la librería para generar dinámicamente colores para la interfaz de usuario, efectos especiales o texturas. Podrían crear sistemas que ajusten los colores de los escenarios según la hora del día o el estado de ánimo de un personaje.


* Razones para Usar esta Librería

- Precisión y Consistencia: Permite obtener un control exacto sobre los valores RGB y hexadecimales, asegurando que los colores resultantes sean los mismos cada vez que se mezclan.

- Reusabilidad: La función de guardar mezclas personalizadas evita tener que "adivinar" cómo se logró un color particular. Simplemente se carga la mezcla con su nombre y se reutiliza.

- Automatización: Al ser una librería de código, las mezclas de colores pueden ser parte de un script o un programa más grande, permitiendo la creación de efectos dinámicos o la generación de paletas masivas de forma automática.

- Facilidad de Uso: El uso de presets y la asignación de nombres descriptivos a los colores hace que la interacción sea más intuitiva, incluso para quienes no son expertos en teoría del color.

# Características Implementadas

Gestión de Colores

* Creación de colores desde múltiples formatos (RGB, HEX, presets)
* Sistema de mezcla de colores con porcentajes precisos
* Generación automática de nombres descriptivos para colores
* Historial persistente de mezclas personalizadas

Gestión de Inventario

* Sistema de códigos únicos para vehículos
* Búsqueda y filtrado avanzado
* Estadísticas automáticas del inventario
* Persistencia automática en formato JSON

Exportación Visual

* Generación de paletas SVG
* Reportes HTML con análisis estadístico
* Variables CSS para desarrollo web
* Paletas circulares y lineales

# Patrones de Diseño

* Factory Pattern
Implementado en la clase ColorFactory para la creación flexible de objetos Color:

```bash
factory = ColorFactory()

# Diferentes formas de crear colores
color_rgb = factory.crear_color_rgb(255, 0, 0, "Rojo")
color_hex = factory.crear_color_hex("#FF0000", "Rojo") 
color_preset = factory.crear_color_preset("rojo_ferrari")
```
* Builder Pattern
Implementado en ColorMixerCore para construir mezclas complejas paso a paso:
```bash
mixer = ColorMixerCore()
resultado = mixer.agregar_color_preset("rojo_ferrari", 60.0)\
                 .agregar_color_hex("#FFFFFF", "Blanco", 40.0)\
                 .mezclar_colores()
```
* Singleton Pattern
Implementado en InventarioManager y ColorHistory para garantizar una única instancia:
```bash
# Siempre devuelve la misma instancia
inventario1 = InventarioManager()
inventario2 = InventarioManager()
assert inventario1 is inventario2  # True
```
# Estructuras de Datos

* Listas Enlazadas Personalizadas
El proyecto implementa listas enlazadas especializadas para diferentes tipos de datos:

ListaEnlazadaColores
```bash
class ListaEnlazadaColores:
    def __init__(self):
        self.cabeza = None
        self._tamaño = 0
    
    def agregar_color(self, color: Color):
        # Implementación de inserción
    
    def buscar_por_nombre(self, nombre: str) -> Color:
        # Búsqueda lineal optimizada
```
ListaEnlazadaAutos
```bash
class ListaEnlazadaAutos:
    def buscar_por_codigo(self, codigo: str) -> Auto:
        # Búsqueda específica para inventario
    
    def obtener_todos(self) -> List[Auto]:
        # Conversión eficiente a lista estándar
```
* Nodos Especializados

```bash
class NodoColor:
    def __init__(self, color: Color):
        self.color = color
        self.siguiente = None

class NodoAuto:
    def __init__(self, auto: Auto):
        self.auto = auto
        self.siguiente = None
```
# Instalación

* Requisitos del Sistema
 - Python 3.8 o superior
 - Sistema operativo: Windows, macOS, Linux

* Instalación desde PyPI (Recomendado)

```bash
pip install color-mixer
``` 

* Instalación desde código fuente

```bash
# Clonar el repositorio
git clone https://github.com/armando-777/PG2_PRACTICA_7_ColorMixer.git
cd src/colormixer

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias (ninguna requerida para funcionamiento básico)
pip install -r requirements.txt  # Solo para desarrollo/testing
```
# Uso Básico

* Mezcla Simple de Colores
```bash
from color_mixer.color_core import ColorMixerCore

# Crear mezclador
mixer = ColorMixerCore()

# Agregar colores (patrón Builder)
mixer.agregar_color_preset("rojo_ferrari", 70.0)\
     .agregar_color_preset("blanco_perla", 30.0)

# Realizar mezcla
color_resultado = mixer.mezclar_colores()

print(f"Color creado: {color_resultado.nombre}")
print(f"Código HEX: {color_resultado.to_hex()}")
print(f"RGB: {color_resultado.to_rgb()}")
```
* Gestión de Inventario
```bash
from color_mixer.inventario_manager import InventarioManager
from color_mixer.color_core import ColorFactory

# Obtener gestor (Singleton)
inventario = InventarioManager()

# Crear colores
factory = ColorFactory()
rojo = factory.crear_color_preset("rojo_ferrari")
negro = factory.crear_color_preset("negro_carbón")

# Registrar vehículo
inventario.registrar_auto(
    modelo="Ferrari 488 GTB",
    codigo_color="FER001",
    colores_mezcla=[rojo, negro],
    porcentajes=[85.0, 15.0]
)

# Consultar información
info = inventario.obtener_color_auto("FER001")
print(f"Modelo: {info['modelo']}")
print(f"Color: {info['color_resultante']['hex']}")
```
* Exportación Visual
```bash
from color_mixer.visual_exports import VisualExporter

# Crear exportador
exporter = VisualExporter()

# Exportar paleta SVG
colores = [rojo, negro]
exporter.exportar_paleta_svg(colores, "mi_paleta")

# Generar reporte HTML
exporter.generar_reporte_colores(colores, "analisis_colores")
```
# Ejemplos de Código
```bash
def ejemplo_concesionario():
    """Simula un sistema básico de concesionario de autos."""
    
    # Configurar colores de marca
    mixer = ColorMixerCore()
    
    # Crear color signature de la marca
    color_signature = mixer.agregar_color_hex("#8B0000", "Rojo Borgoña", 70.0)\
                           .agregar_color_hex("#FFD700", "Dorado", 30.0)\
                           .mezclar_colores()
    
    mixer.guardar_mezcla_personal("Signature_Marca")
    
    # Registrar vehículos en inventario
    inventario = InventarioManager()
    
    # Ferrari deportivo
    ferrari_mixer = ColorMixerCore()
    ferrari_color = ferrari_mixer.agregar_color_preset("rojo_ferrari", 100.0)\
                                 .mezclar_colores()
    
    inventario.registrar_auto(
        "Ferrari 488 GTB",
        "FER488001",
        [ferrari_color],
        [100.0]
    )
    
    # Lamborghini personalizado
    lambo_mixer = ColorMixerCore()
    lambo_color = lambo_mixer.agregar_color_hex("#FF4500", "Naranja Deportivo", 90.0)\
                             .agregar_color_preset("negro_carbón", 10.0)\
                             .mezclar_colores()
    
    inventario.registrar_auto(
        "Lamborghini Huracán",
        "LAM001",
        lambo_mixer.colores_actuales.obtener_colores(),
        lambo_mixer.porcentajes_actuales
    )
    
    # Generar catálogo visual
    exporter = VisualExporter()
    
    # Crear paleta con todos los colores
    todos_colores = []
    for auto in inventario.inventario:
        color = auto.calcular_color_resultante()
        if color:
            todos_colores.append(color)
    
    # Exportar catálogo
    exporter.crear_paleta_circular(todos_colores, "catalogo_premium", 180)
    exporter.generar_reporte_colores(todos_colores, "inventario_detallado")
    
    # Mostrar estadísticas
    stats = inventario.obtener_estadisticas()
    print(f"Inventario configurado:")
    print(f"- Total vehículos: {stats['total_autos']}")
    print(f"- Modelos únicos: {stats['modelos_unicos']}")
    print(f"- Colores más usados: {stats['colores_mas_usados']}")
    
    return inventario

# Ejecutar ejemplo
if __name__ == "__main__":
    inventario = ejemplo_concesionario()
```
#  API Referencia
* Clase Color
```bash
class Color:
    def __init__(self, r: int, g: int, b: int, nombre: str = None)
    def to_hex(self) -> str
    def to_rgb(self) -> tuple
    def __str__(self) -> str
    def __eq__(self, other) -> bool
```
* Clase ColorFactory
```bash
class ColorFactory:
    @staticmethod
    def crear_color_rgb(r: int, g: int, b: int, nombre: str = None) -> Color
    
    @staticmethod
    def crear_color_hex(hex_code: str, nombre: str = None) -> Color
    
    @staticmethod
    def crear_color_preset(nombre_preset: str) -> Color
```
* Clase ColorMixerCore
```bash
class ColorMixerCore:
    def agregar_color_rgb(self, r: int, g: int, b: int, nombre: str = None, porcentaje: float = 0.0)
    def agregar_color_hex(self, hex_code: str, nombre: str = None, porcentaje: float = 0.0)
    def agregar_color_preset(self, nombre_preset: str, porcentaje: float = 0.0)
    def establecer_porcentajes(self, porcentajes: List[float])
    def mezclar_colores(self) -> Color
    def guardar_mezcla_personal(self, nombre: str) -> bool
    def cargar_mezcla_personal(self, nombre: str) -> Optional[Color]
    def listar_mezclas_personales(self) -> List[str]
    def obtener_nombre_color(self, color: Color) -> str
    def limpiar_mezcla(self)
```
* Clase InventarioManager
```bash
class InventarioManager:
    def registrar_auto(self, modelo: str, codigo_color: str, colores_mezcla: List[Color], porcentajes: List[float]) -> bool
    def obtener_color_auto(self, codigo_color: str) -> Optional[Dict]
    def mostrar_colores_existentes(self) -> List[Dict]
    def buscar_por_modelo(self, modelo: str) -> List[Auto]
    def buscar_por_color_similar(self, color_referencia: Color, tolerancia: int = 50) -> List[Auto]
    def obtener_estadisticas(self) -> Dict
    def eliminar_auto(self, codigo_color: str) -> bool
```
* Clase VisualExporter
```bash
class VisualExporter:
    def crear_swatch(self, colores: List[Color], ancho_muestra: int = 100, alto_muestra: int = 100) -> str
    def exportar_paleta_png(self, colores: List[Color], nombre_archivo: str) -> bool
    def exportar_paleta_svg(self, colores: List[Color], nombre_archivo: str, ancho_muestra: int = 120, alto_muestra: int = 120) -> bool
    def crear_paleta_circular(self, colores: List[Color], nombre_archivo: str, radio: int = 150) -> bool
    def generar_reporte_colores(self, colores: List[Color], nombre_archivo: str) -> bool
    def exportar_css_variables(self, colores: List[Color], nombre_archivo: str) -> bool
```
# Arquitectura del Proyecto

* Organización de Módulos
```bash
src/color_mixer/
├── estructuras.py          # Clases base y estructuras de datos
├── color_core.py          # Lógica principal de mezcla
├── inventario_manager.py  # Gestión de inventario (Singleton)
└── visual_exports.py      # Exportación y visualización
```
* Flujo de Datos

1. ColorFactory crea objetos Color
2. ColorMixerCore agrega colores usando Builder pattern
3. Color resultante se calcula mediante algoritmo de mezcla
4. InventarioManager almacena Auto con colores asociados
5. VisualExporter genera representaciones visuales
6. Datos se persisten automáticamente en JSON

#  Testing

El proyecto incluye pruebas unitarias para validar la funcionalidad:
* Estructura de Pruebas
```bash
tests/
├── test_estructuras.py       # Pruebas de clases base
├── test_color_core.py        # Pruebas de mezcla y Factory
├── test_inventario_manager.py # Pruebas de Singleton
└── test_visual_exports.py    # Pruebas de exportación
```
* Ejecutar Pruebas
```bash
# Instalar pytest (si no está instalado)
pip install pytest

# Ejecutar todas las pruebas
python -m pytest test/ -v

# Ejecutar pruebas específicas

python -m pytest test/test_color_core.py -v
python -m pytest test/test_inventario_manager.py -v
python -m pytest test/test_visual_exports.py -v
python -m pytest test/test_estructuras.py -v

```
* Ejemplo de Prueba
```bash
def test_patron_builder():
    """Verifica que el patrón Builder funciona correctamente."""
    mixer = ColorMixerCore()
    
    # El patrón Builder debe permitir encadenamiento
    resultado = mixer.agregar_color_rgb(255, 0, 0, "Rojo", 50.0)\
                     .agregar_color_rgb(0, 0, 255, "Azul", 50.0)
    
    assert resultado is mixer  # Verifica encadenamiento
    assert mixer.colores_actuales.tamaño() == 2
    
    color_final = mixer.mezclar_colores()
    assert color_final.r > 0 and color_final.b > 0  # Mezcla correcta
```
# Contribuciones Académicas

Conceptos Demostrados

* Patrones de Diseño:

Implementación práctica de Factory, Builder y Singleton
Ventajas y casos de uso de cada patrón
Comparación con implementaciones alternativas

* Estructuras de Datos:

Listas enlazadas simples con operaciones especializadas
Encapsulación de lógica de dominio en estructuras
Iteradores personalizados y operaciones de búsqueda

* Herramientas Utilizadas

Desarrollo: Python 3.8+, Visual Studio Code
Testing: pytest, pytest-cov
Documentación: Markdown, docstrings de Python
Control de versiones: Git
Formato de código: Black, flake8

