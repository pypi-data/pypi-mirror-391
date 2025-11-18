class Color:
    """Clase que representa un color con múltiples formatos."""
    
    def __init__(self, r: int, g: int, b: int, nombre: str = None):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
        self.nombre = nombre or f"RGB({self.r},{self.g},{self.b})"
    
    def to_hex(self) -> str:
        """Convierte el color a formato hexadecimal."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    def to_rgb(self) -> tuple:
        """Devuelve una tupla RGB."""
        return (self.r, self.g, self.b)
    
    def __str__(self):
        return f"{self.nombre} {self.to_hex()}"
    
    def __eq__(self, other):
        if isinstance(other, Color):
            return (self.r, self.g, self.b) == (other.r, other.g, other.b)
        return False

class NodoColor:
    """Nodo para la lista enlazada de colores."""
    
    def __init__(self, color: Color):
        self.color = color
        self.siguiente = None

class ListaEnlazadaColores:
    """Lista enlazada específica para gestionar colores."""
    
    def __init__(self):
        self.cabeza = None
        self._tamaño = 0
    
    def agregar_color(self, color: Color):
        """Agrega un color al final de la lista."""
        nuevo_nodo = NodoColor(color)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self._tamaño += 1
    
    def obtener_colores(self) -> list[Color]:
        """Devuelve todos los colores como lista."""
        colores = []
        actual = self.cabeza
        while actual:
            colores.append(actual.color)
            actual = actual.siguiente
        return colores
    
    def buscar_por_nombre(self, nombre: str) -> Color:
        """Busca un color por nombre."""
        actual = self.cabeza
        while actual:
            if actual.color.nombre.lower() == nombre.lower():
                return actual.color
            actual = actual.siguiente
        return None
    
    def tamaño(self) -> int:
        """Devuelve el número de colores en la lista."""
        return self._tamaño
    
    def __iter__(self):
        """Permite iterar sobre la lista."""
        actual = self.cabeza
        while actual:
            yield actual.color
            actual = actual.siguiente

class Auto:
    """Clase que representa un automóvil con su información de color."""
    
    def __init__(self, modelo: str, codigo_color: str, colores_mezcla: list[Color], porcentajes: list[float]):
        self.modelo = modelo
        self.codigo_color = codigo_color
        self.colores_mezcla = ListaEnlazadaColores()
        for color in colores_mezcla:
            self.colores_mezcla.agregar_color(color)
        self.porcentajes = porcentajes
        self.color_resultante = None
    
    def calcular_color_resultante(self):
        """Calcula el color resultante de la mezcla."""
        if self.color_resultante:
            return self.color_resultante
        
        colores = self.colores_mezcla.obtener_colores()
        if not colores or len(colores) != len(self.porcentajes):
            return None
        
        r_total = sum(color.r * (porcentaje / 100) for color, porcentaje in zip(colores, self.porcentajes))
        g_total = sum(color.g * (porcentaje / 100) for color, porcentaje in zip(colores, self.porcentajes))
        b_total = sum(color.b * (porcentaje / 100) for color, porcentaje in zip(colores, self.porcentajes))
        
        self.color_resultante = Color(int(r_total), int(g_total), int(b_total), f"{self.modelo}_{self.codigo_color}")
        return self.color_resultante
    
    def __str__(self):
        return f"Auto {self.modelo} - Código: {self.codigo_color}"

