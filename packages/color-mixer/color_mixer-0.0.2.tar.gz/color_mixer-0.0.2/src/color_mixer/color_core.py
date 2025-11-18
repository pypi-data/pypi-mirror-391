import json
import os
from typing import List, Tuple, Dict, Optional
from .estructuras import Color, ListaEnlazadaColores


class ColorBlender:
    """Clase dedicada a realizar mezclas de colores."""
    
    def __init__(self):
        pass
    
    def mezclar(self, colores: List[Color], porcentajes: List[float]) -> Color:
        """
        Realiza la mezcla de colores según los porcentajes especificados.
        
        Args:
            colores: Lista de colores a mezclar
            porcentajes: Lista de porcentajes (deben sumar 100)
        
        Returns:
            Color resultante de la mezcla
        
        Raises:
            ValueError: Si los colores o porcentajes son inválidos
        """
        if not colores:
            raise ValueError("No hay colores para mezclar")
        
        if len(colores) != len(porcentajes):
            raise ValueError("Número de colores debe coincidir con número de porcentajes")
        
        if abs(sum(porcentajes) - 100.0) > 0.01:
            raise ValueError("Los porcentajes deben sumar 100%")
        
        r_total = sum(color.r * (porcentaje / 100) for color, porcentaje in zip(colores, porcentajes))
        g_total = sum(color.g * (porcentaje / 100) for color, porcentaje in zip(colores, porcentajes))
        b_total = sum(color.b * (porcentaje / 100) for color, porcentaje in zip(colores, porcentajes))
        
        return Color(int(r_total), int(g_total), int(b_total))


class ColorHistory:
    """Singleton para mantener el historial de mezclas."""
    
    _instancia = None
    _inicializado = False
    
    def __new__(cls, ruta_guardado: str = None):  # ← CAMBIO: Agregar parámetro
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia
    
    def __init__(self, ruta_guardado: str = None):
        if not ColorHistory._inicializado:
            self.historial = []
            self.mezclas_personales = {}
            self.ruta_guardado = ruta_guardado or 'colormixer_history.json'
            self._cargar_datos()
            ColorHistory._inicializado = True
    
    def configurar_ruta(self, ruta: str):
        """Configura la ruta de guardado del historial."""
        self.ruta_guardado = ruta
        self._cargar_datos()
    
    def agregar_mezcla(self, nombre: str, colores: List[Color], porcentajes: List[float], color_resultado: Color):
        """Agrega una mezcla al historial."""
        mezcla = {
            'nombre': nombre,
            'colores': [{'r': c.r, 'g': c.g, 'b': c.b, 'nombre': c.nombre} for c in colores],
            'porcentajes': porcentajes,
            'resultado': {'r': color_resultado.r, 'g': color_resultado.g, 'b': color_resultado.b, 'nombre': color_resultado.nombre}
        }
        self.historial.append(mezcla)
        self.mezclas_personales[nombre] = mezcla
        self._guardar_datos()
    
    def obtener_mezcla(self, nombre: str) -> Optional[Dict]:
        """Obtiene una mezcla por nombre."""
        return self.mezclas_personales.get(nombre)
    
    def listar_mezclas(self) -> List[str]:
        """Lista todos los nombres de mezclas guardadas."""
        return list(self.mezclas_personales.keys())
    
    def _cargar_datos(self):
        """Carga datos desde archivo JSON."""
        try:
            if os.path.exists(self.ruta_guardado):
                with open(self.ruta_guardado, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    self.historial = datos.get('historial', [])
                    self.mezclas_personales = datos.get('mezclas_personales', {})
        except Exception as e:
            print(f"Error cargando historial: {e}")
    
    def _guardar_datos(self):
        """Guarda datos en archivo JSON."""
        try:
            datos = {
                'historial': self.historial,
                'mezclas_personales': self.mezclas_personales
            }
            with open(self.ruta_guardado, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando historial: {e}")


class ColorFactory:
    """Factory para crear diferentes tipos de colores."""
    
    @staticmethod
    def crear_color_rgb(r: int, g: int, b: int, nombre: str = None) -> Color:
        """Crea un color desde valores RGB."""
        return Color(r, g, b, nombre)
    
    @staticmethod
    def crear_color_hex(hex_code: str, nombre: str = None) -> Color:
        """Crea un color desde código hexadecimal."""
        hex_code = hex_code.lstrip('#')
        if len(hex_code) != 6:
            raise ValueError("Código hexadecimal debe tener 6 caracteres")
        
        try:
            r = int(hex_code[0:2], 16)
            g = int(hex_code[2:4], 16)
            b = int(hex_code[4:6], 16)
            return Color(r, g, b, nombre)
        except ValueError:
            raise ValueError("Código hexadecimal inválido")
    
    @staticmethod
    def crear_color_preset(nombre_preset: str) -> Color:
        """Crea un color desde presets predefinidos."""
        presets = {
            'rojo_ferrari': Color(255, 0, 0, 'Rojo Ferrari'),
            'azul_marino': Color(0, 0, 128, 'Azul Marino'),
            'verde_esmeralda': Color(0, 128, 0, 'Verde Esmeralda'),
            'blanco_perla': Color(248, 248, 248, 'Blanco Perla'),
            'negro_carbón': Color(36, 36, 36, 'Negro Carbón'),
            'plata_metalico': Color(192, 192, 192, 'Plata Metálico'),
            'dorado': Color(255, 215, 0, 'Dorado'),
            'bronce': Color(205, 127, 50, 'Bronce')
        }
        
        if nombre_preset.lower() in presets:
            return presets[nombre_preset.lower()]
        else:
            raise ValueError(f"Preset '{nombre_preset}' no existe")


class ColorMixerCore:
    """Clase principal para mezclar colores - Implementa Builder pattern."""
    
    def __init__(self, ruta_guardado: str = None):
        self.colores_actuales = ListaEnlazadaColores()
        self.porcentajes_actuales = []
        self.history = ColorHistory(ruta_guardado)
        self.factory = ColorFactory()
        self.blender = ColorBlender()
        self._nombres_colores = self._inicializar_nombres_colores()
    
    def configurar_ruta_guardado(self, ruta: str):
        """Configura la ruta de guardado del historial."""
        self.history.configurar_ruta(ruta)
        return self
    
    def agregar_color_rgb(self, r: int, g: int, b: int, nombre: str = None, porcentaje: float = 0.0):
        """Agrega un color RGB a la mezcla actual."""
        color = self.factory.crear_color_rgb(r, g, b, nombre)
        self.colores_actuales.agregar_color(color)
        self.porcentajes_actuales.append(porcentaje)
        return self
    
    def agregar_color_hex(self, hex_code: str, nombre: str = None, porcentaje: float = 0.0):
        """Agrega un color hexadecimal a la mezcla actual."""
        color = self.factory.crear_color_hex(hex_code, nombre)
        self.colores_actuales.agregar_color(color)
        self.porcentajes_actuales.append(porcentaje)
        return self
    
    def agregar_color_preset(self, nombre_preset: str, porcentaje: float = 0.0):
        """Agrega un color preset a la mezcla actual."""
        color = self.factory.crear_color_preset(nombre_preset)
        self.colores_actuales.agregar_color(color)
        self.porcentajes_actuales.append(porcentaje)
        return self
    
    def establecer_porcentajes(self, porcentajes: List[float]):
        """Establece los porcentajes para todos los colores."""
        if sum(porcentajes) != 100.0:
            raise ValueError("Los porcentajes deben sumar 100%")
        
        if len(porcentajes) != self.colores_actuales.tamaño():
            raise ValueError("Número de porcentajes debe coincidir con número de colores")
        
        self.porcentajes_actuales = porcentajes
        return self
    
    def mezclar_colores(self) -> Color:
        """Realiza la mezcla de colores actual."""
        if self.colores_actuales.tamaño() == 0:
            raise ValueError("No hay colores para mezclar")
        
        if not self.porcentajes_actuales:
            # Distribución equitativa si no se especifican porcentajes
            porcentaje_igual = 100.0 / self.colores_actuales.tamaño()
            self.porcentajes_actuales = [porcentaje_igual] * self.colores_actuales.tamaño()
        
        colores = self.colores_actuales.obtener_colores()
        
        # Usar el ColorBlender para realizar la mezcla
        color_resultado = self.blender.mezclar(colores, self.porcentajes_actuales)
        color_resultado.nombre = self.obtener_nombre_color(color_resultado)
        
        return color_resultado
    
    def guardar_mezcla_personal(self, nombre: str) -> bool:
        """Guarda la mezcla actual como personal."""
        try:
            color_resultado = self.mezclar_colores()
            colores = self.colores_actuales.obtener_colores()
            self.history.agregar_mezcla(nombre, colores, self.porcentajes_actuales, color_resultado)
            return True
        except Exception as e:
            print(f"Error guardando mezcla: {e}")
            return False
    
    def cargar_mezcla_personal(self, nombre: str) -> Optional[Color]:
        """Carga una mezcla personal previamente guardada."""
        mezcla = self.history.obtener_mezcla(nombre)
        if not mezcla:
            return None
        
        # Reconstruir la mezcla
        self.limpiar_mezcla()
        
        for color_data, porcentaje in zip(mezcla['colores'], mezcla['porcentajes']):
            color = Color(color_data['r'], color_data['g'], color_data['b'], color_data['nombre'])
            self.colores_actuales.agregar_color(color)
            self.porcentajes_actuales.append(porcentaje)
        
        resultado = mezcla['resultado']
        return Color(resultado['r'], resultado['g'], resultado['b'], resultado['nombre'])
    
    def listar_mezclas_personales(self) -> List[str]:
        """Lista todas las mezclas personales guardadas."""
        return self.history.listar_mezclas()
    
    def obtener_nombre_color(self, color: Color) -> str:
        """Obtiene un nombre descriptivo para un color."""
        # Buscar el nombre más cercano
        min_distancia = float('inf')
        nombre_cercano = f"RGB({color.r},{color.g},{color.b})"
        
        for nombre, rgb in self._nombres_colores.items():
            distancia = self._calcular_distancia_color(color, Color(*rgb))
            if distancia < min_distancia:
                min_distancia = distancia
                nombre_cercano = nombre
        
        # Si la distancia es muy grande, usar descripción genérica
        if min_distancia > 100:
            return self._generar_descripcion_color(color)
        
        return nombre_cercano
    
    def obtener_porcentajes(self, colores_mezcla: List[Color]) -> List[float]:
        """Calcula porcentajes sugeridos para una lista de colores."""
        if not colores_mezcla:
            return []
        
        # Por ahora, distribución equitativa
        porcentaje_igual = 100.0 / len(colores_mezcla)
        return [porcentaje_igual] * len(colores_mezcla)
    
    def limpiar_mezcla(self):
        """Limpia la mezcla actual."""
        self.colores_actuales = ListaEnlazadaColores()
        self.porcentajes_actuales = []
        return self
    
    def _calcular_distancia_color(self, color1: Color, color2: Color) -> float:
        """Calcula la distancia euclidiana entre dos colores."""
        return ((color1.r - color2.r) ** 2 + (color1.g - color2.g) ** 2 + (color1.b - color2.b) ** 2) ** 0.5
    
    def _generar_descripcion_color(self, color: Color) -> str:
        """Genera una descripción genérica del color."""
        r, g, b = color.r, color.g, color.b
        
        # Determinar el componente dominante
        if r > g and r > b:
            if r > 200:
                return "Rojo Brillante"
            elif r > 100:
                return "Rojo Medio"
            else:
                return "Rojo Oscuro"
        elif g > r and g > b:
            if g > 200:
                return "Verde Brillante"
            elif g > 100:
                return "Verde Medio"
            else:
                return "Verde Oscuro"
        elif b > r and b > g:
            if b > 200:
                return "Azul Brillante"
            elif b > 100:
                return "Azul Medio"
            else:
                return "Azul Oscuro"
        else:
            # Colores neutros
            promedio = (r + g + b) // 3
            if promedio > 200:
                return "Blanco Perlado"
            elif promedio > 100:
                return "Gris Plata"
            else:
                return "Gris Carbón"
    
    def _inicializar_nombres_colores(self) -> Dict[str, Tuple[int, int, int]]:
        """Inicializa el diccionario de nombres de colores."""
        return {
            'Rojo Ferrari': (255, 0, 0),
            'Azul Marino': (0, 0, 128),
            'Verde Esmeralda': (0, 128, 0),
            'Blanco Perla': (248, 248, 248),
            'Negro Carbón': (36, 36, 36),
            'Plata Metálico': (192, 192, 192),
            'Dorado': (255, 215, 0),
            'Bronce': (205, 127, 50),
            'Azul Cielo': (135, 206, 235),
            'Rosa Sakura': (255, 182, 193),
            'Violeta Imperial': (102, 51, 153),
            'Naranja Atardecer': (255, 165, 0),
            'Amarillo Limón': (255, 255, 0),
            'Turquesa': (64, 224, 208),
            'Coral': (255, 127, 80),
            'Lavanda': (230, 230, 250)
        }