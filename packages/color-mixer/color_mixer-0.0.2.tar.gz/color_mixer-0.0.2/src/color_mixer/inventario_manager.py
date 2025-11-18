"""
Submódulo de gestión de inventario de automóviles
"""

import json
import os
from typing import List, Dict, Optional
from .estructuras import Color, Auto, ListaEnlazadaColores


class NodoAuto:
    """Nodo para la lista enlazada de automóviles."""
    
    def __init__(self, auto: Auto):
        self.auto = auto
        self.siguiente = None


class ListaEnlazadaAutos:
    """Lista enlazada específica para gestionar automóviles."""
    
    def __init__(self):
        self.cabeza = None
        self._tamaño = 0
    
    def agregar_auto(self, auto: Auto):
        """Agrega un auto al final de la lista."""
        nuevo_nodo = NodoAuto(auto)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self._tamaño += 1
    
    def buscar_por_codigo(self, codigo_color: str) -> Auto:
        """Busca un auto por código de color."""
        actual = self.cabeza
        while actual:
            if actual.auto.codigo_color == codigo_color:
                return actual.auto
            actual = actual.siguiente
        return None
    
    def obtener_todos(self) -> List[Auto]:
        """Devuelve todos los autos como lista."""
        autos = []
        actual = self.cabeza
        while actual:
            autos.append(actual.auto)
            actual = actual.siguiente
        return autos
    
    def tamaño(self) -> int:
        """Devuelve el número de autos en la lista."""
        return self._tamaño
    
    def __iter__(self):
        """Permite iterar sobre la lista."""
        actual = self.cabeza
        while actual:
            yield actual.auto
            actual = actual.siguiente


class InventarioManager:
    """Gestor de inventario de automóviles - Singleton pattern."""
    
    _instancia = None
    _inicializado = False
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia
    
    def __init__(self, ruta_guardado: str = None):
        if not InventarioManager._inicializado:
            self.inventario = ListaEnlazadaAutos()
            self.archivo_datos = ruta_guardado or 'inventario_autos.json'
            self._cargar_inventario()
            InventarioManager._inicializado = True
    
    def configurar_ruta_guardado(self, ruta: str):
        """Configura la ruta de guardado del inventario."""
        self.archivo_datos = ruta
        self._cargar_inventario()
    
    def registrar_auto(self, modelo: str, codigo_color: str, colores_mezcla: List[Color], porcentajes: List[float]) -> bool:
        """Registra un nuevo auto en el inventario."""
        try:
            # Verificar que no existe el código
            if self.inventario.buscar_por_codigo(codigo_color):
                print(f"Error: Ya existe un auto con código {codigo_color}")
                return False
            
            # Validar porcentajes
            if abs(sum(porcentajes) - 100.0) > 0.01:
                print("Error: Los porcentajes deben sumar 100%")
                return False
            
            if len(colores_mezcla) != len(porcentajes):
                print("Error: Número de colores debe coincidir con número de porcentajes")
                return False
            
            # Crear y agregar auto
            auto = Auto(modelo, codigo_color, colores_mezcla, porcentajes)
            auto.calcular_color_resultante()
            self.inventario.agregar_auto(auto)
            
            # Guardar cambios
            self._guardar_inventario()
            print(f"Auto {modelo} registrado exitosamente con código {codigo_color}")
            return True
            
        except Exception as e:
            print(f"Error registrando auto: {e}")
            return False
    
    def obtener_color_auto(self, codigo_color: str) -> Optional[Dict]:
        """Obtiene información completa de un auto por código de color."""
        auto = self.inventario.buscar_por_codigo(codigo_color)
        if not auto:
            return None
        
        colores_info = []
        for color in auto.colores_mezcla:
            colores_info.append({
                'nombre': color.nombre,
                'rgb': color.to_rgb(),
                'hex': color.to_hex()
            })
        
        color_resultante = auto.calcular_color_resultante()
        
        return {
            'modelo': auto.modelo,
            'codigo_color': auto.codigo_color,
            'colores_mezcla': colores_info,
            'porcentajes': auto.porcentajes,
            'color_resultante': {
                'nombre': color_resultante.nombre,
                'rgb': color_resultante.to_rgb(),
                'hex': color_resultante.to_hex()
            } if color_resultante else None
        }
    
    def mostrar_colores_existentes(self) -> List[Dict]:
        """Muestra todos los códigos de color registrados."""
        colores_existentes = []
        for auto in self.inventario:
            color_resultante = auto.calcular_color_resultante()
            colores_existentes.append({
                'codigo': auto.codigo_color,
                'modelo': auto.modelo,
                'color_principal': color_resultante.to_hex() if color_resultante else '#000000',
                'nombre_color': color_resultante.nombre if color_resultante else 'Sin nombre'
            })
        
        return colores_existentes
    
    def buscar_por_modelo(self, modelo: str) -> List[Auto]:
        """Busca autos por modelo."""
        autos_encontrados = []
        for auto in self.inventario:
            if modelo.lower() in auto.modelo.lower():
                autos_encontrados.append(auto)
        return autos_encontrados
    
    def buscar_por_color_similar(self, color_referencia: Color, tolerancia: int = 50) -> List[Auto]:
        """Busca autos con colores similares al color de referencia."""
        autos_similares = []
        for auto in self.inventario:
            color_auto = auto.calcular_color_resultante()
            if color_auto:
                distancia = self._calcular_distancia_color(color_referencia, color_auto)
                if distancia <= tolerancia:
                    autos_similares.append(auto)
        return autos_similares
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del inventario."""
        total_autos = self.inventario.tamaño()
        modelos_unicos = set()
        colores_mas_usados = {}
        
        for auto in self.inventario:
            modelos_unicos.add(auto.modelo)
            for color in auto.colores_mezcla:
                nombre_color = color.nombre
                colores_mas_usados[nombre_color] = colores_mas_usados.get(nombre_color, 0) + 1
        
        return {
            'total_autos': total_autos,
            'modelos_unicos': len(modelos_unicos),
            'lista_modelos': list(modelos_unicos),
            'colores_mas_usados': sorted(colores_mas_usados.items(), key=lambda x: x[1], reverse=True)
        }
    
    def eliminar_auto(self, codigo_color: str) -> bool:
        """Elimina un auto del inventario."""
        if not self.inventario.cabeza:
            return False
        
        # Si es el primer nodo
        if self.inventario.cabeza.auto.codigo_color == codigo_color:
            self.inventario.cabeza = self.inventario.cabeza.siguiente
            self.inventario._tamaño -= 1
            self._guardar_inventario()
            return True
        
        # Buscar en el resto de la lista
        actual = self.inventario.cabeza
        while actual.siguiente:
            if actual.siguiente.auto.codigo_color == codigo_color:
                actual.siguiente = actual.siguiente.siguiente
                self.inventario._tamaño -= 1
                self._guardar_inventario()
                return True
            actual = actual.siguiente
        
        return False
    
    def _calcular_distancia_color(self, color1: Color, color2: Color) -> float:
        """Calcula la distancia euclidiana entre dos colores."""
        return ((color1.r - color2.r) ** 2 + (color1.g - color2.g) ** 2 + (color1.b - color2.b) ** 2) ** 0.5
    
    def _cargar_inventario(self):
        """Carga el inventario desde archivo JSON."""
        try:
            if os.path.exists(self.archivo_datos):
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    for auto_data in datos:
                        colores = []
                        for color_data in auto_data['colores_mezcla']:
                            color = Color(color_data['r'], color_data['g'], color_data['b'], color_data['nombre'])
                            colores.append(color)
                        
                        auto = Auto(auto_data['modelo'], auto_data['codigo_color'], colores, auto_data['porcentajes'])
                        self.inventario.agregar_auto(auto)
        except Exception as e:
            print(f"Error cargando inventario: {e}")
    
    def _guardar_inventario(self):
        """Guarda el inventario en archivo JSON."""
        try:
            datos = []
            for auto in self.inventario:
                colores_data = []
                for color in auto.colores_mezcla:
                    colores_data.append({
                        'r': color.r,
                        'g': color.g,
                        'b': color.b,
                        'nombre': color.nombre
                    })
                
                datos.append({
                    'modelo': auto.modelo,
                    'codigo_color': auto.codigo_color,
                    'colores_mezcla': colores_data,
                    'porcentajes': auto.porcentajes
                })
            
            with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando inventario: {e}")