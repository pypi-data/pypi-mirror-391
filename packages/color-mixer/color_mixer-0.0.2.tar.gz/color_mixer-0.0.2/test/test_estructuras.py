import unittest
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from color_mixer.estructuras import Color, ListaEnlazadaColores, Auto

class TestColor(unittest.TestCase):
    
    def test_crear_color(self):
        """Test creación de color básico."""
        color = Color(255, 0, 0, "Rojo")
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 0)
        self.assertEqual(color.b, 0)
        self.assertEqual(color.nombre, "Rojo")
    
    def test_color_to_hex(self):
        """Test conversión a hexadecimal."""
        color = Color(255, 0, 0)
        self.assertEqual(color.to_hex(), "#ff0000")
    
    def test_color_to_rgb(self):
        """Test conversión a tupla RGB."""
        color = Color(255, 128, 64)
        self.assertEqual(color.to_rgb(), (255, 128, 64))
    
    def test_color_limites(self):
        """Test que los valores RGB se mantengan en rango 0-255."""
        color = Color(-10, 300, 128)
        self.assertEqual(color.r, 0)
        self.assertEqual(color.g, 255)

class TestListaEnlazadaColores(unittest.TestCase):
    
    def setUp(self):
        """Configurar lista para pruebas."""
        self.lista = ListaEnlazadaColores()
        self.rojo = Color(255, 0, 0, "Rojo")
        self.azul = Color(0, 0, 255, "Azul")
    
    def test_lista_vacia(self):
        """Test lista vacía inicial."""
        self.assertEqual(self.lista.tamaño(), 0)
        self.assertIsNone(self.lista.cabeza)
    
    def test_agregar_color(self):
        """Test agregar colores a la lista."""
        self.lista.agregar_color(self.rojo)
        self.assertEqual(self.lista.tamaño(), 1)
        self.assertIsNotNone(self.lista.cabeza)
        
        self.lista.agregar_color(self.azul)
        self.assertEqual(self.lista.tamaño(), 2)
    
    def test_obtener_colores(self):
        """Test obtener lista de colores."""
        self.lista.agregar_color(self.rojo)
        self.lista.agregar_color(self.azul)
        
        colores = self.lista.obtener_colores()
        self.assertEqual(len(colores), 2)
        self.assertEqual(colores[0].nombre, "Rojo")
        self.assertEqual(colores[1].nombre, "Azul")
    
    def test_buscar_por_nombre(self):
        """Test buscar color por nombre."""
        self.lista.agregar_color(self.rojo)
        self.lista.agregar_color(self.azul)
        
        encontrado = self.lista.buscar_por_nombre("Rojo")
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.nombre, "Rojo")
        
        no_encontrado = self.lista.buscar_por_nombre("Verde")
        self.assertIsNone(no_encontrado)

if __name__ == '__main__':
    unittest.main()