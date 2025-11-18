import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from color_mixer.color_core import ColorMixerCore, ColorFactory, ColorHistory, ColorBlender
from color_mixer.estructuras import Color


class TestColorBlender(unittest.TestCase):
    """Tests para la clase ColorBlender."""
    
    def setUp(self):
        self.blender = ColorBlender()
    
    def test_mezcla_basica(self):
        """Test mezcla básica de dos colores."""
        rojo = Color(255, 0, 0, "Rojo")
        azul = Color(0, 0, 255, "Azul")
        
        resultado = self.blender.mezclar([rojo, azul], [50.0, 50.0])
        
        self.assertIsInstance(resultado, Color)
        self.assertGreater(resultado.r, 0)
        self.assertGreater(resultado.b, 0)
    
    def test_mezcla_sin_colores(self):
        """Test mezclar sin colores debe lanzar error."""
        with self.assertRaises(ValueError):
            self.blender.mezclar([], [])
    
    def test_porcentajes_no_suman_100(self):
        """Test que porcentajes deben sumar 100."""
        rojo = Color(255, 0, 0, "Rojo")
        azul = Color(0, 0, 255, "Azul")
        
        with self.assertRaises(ValueError):
            self.blender.mezclar([rojo, azul], [60.0, 60.0])
    
    def test_colores_y_porcentajes_diferentes(self):
        """Test que número de colores y porcentajes coincidan."""
        rojo = Color(255, 0, 0, "Rojo")
        azul = Color(0, 0, 255, "Azul")
        
        with self.assertRaises(ValueError):
            self.blender.mezclar([rojo, azul], [100.0])


class TestColorFactory(unittest.TestCase):
    
    def setUp(self):
        self.factory = ColorFactory()
    
    def test_crear_color_rgb(self):
        """Test crear color desde RGB."""
        color = self.factory.crear_color_rgb(255, 128, 64, "Naranja")
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 128)
        self.assertEqual(color.b, 64)
        self.assertEqual(color.nombre, "Naranja")
    
    def test_crear_color_hex_valido(self):
        """Test crear color desde hex válido."""
        color = self.factory.crear_color_hex("#FF8040", "Naranja")
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 128)
        self.assertEqual(color.b, 64)
    
    def test_crear_color_hex_invalido(self):
        """Test crear color desde hex inválido."""
        with self.assertRaises(ValueError):
            self.factory.crear_color_hex("#GG0000")
        
        with self.assertRaises(ValueError):
            self.factory.crear_color_hex("#FF00")
    
    def test_crear_color_preset(self):
        """Test crear color desde preset."""
        color = self.factory.crear_color_preset("rojo_ferrari")
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 0)
        self.assertEqual(color.b, 0)
    
    def test_preset_inexistente(self):
        """Test preset que no existe."""
        with self.assertRaises(ValueError):
            self.factory.crear_color_preset("color_inexistente")


class TestColorMixerCore(unittest.TestCase):
    
    def setUp(self):
        self.mixer = ColorMixerCore()
    
    def test_agregar_colores_builder(self):
        """Test patrón builder para agregar colores."""
        resultado = self.mixer.agregar_color_rgb(255, 0, 0, "Rojo", 50.0)\
                              .agregar_color_rgb(0, 0, 255, "Azul", 50.0)
        
        # Debe retornar self para encadenamiento
        self.assertIs(resultado, self.mixer)
        self.assertEqual(self.mixer.colores_actuales.tamaño(), 2)
    
    def test_mezcla_basica(self):
        """Test mezcla básica de dos colores."""
        self.mixer.agregar_color_rgb(255, 0, 0, "Rojo", 50.0)\
                  .agregar_color_rgb(0, 0, 255, "Azul", 50.0)
        
        resultado = self.mixer.mezclar_colores()
        
        # El resultado debe ser un color válido
        self.assertIsInstance(resultado, Color)
        # Debe tener componentes de ambos colores
        self.assertGreater(resultado.r, 0)
        self.assertGreater(resultado.b, 0)
    
    def test_porcentajes_invalidos(self):
        """Test validación de porcentajes."""
        self.mixer.agregar_color_rgb(255, 0, 0, "Rojo", 60.0)\
                  .agregar_color_rgb(0, 0, 255, "Azul", 60.0)
        
        with self.assertRaises(ValueError):
            self.mixer.establecer_porcentajes([60.0, 60.0])  # Suman 120%
    
    def test_limpiar_mezcla(self):
        """Test limpiar mezcla actual."""
        self.mixer.agregar_color_rgb(255, 0, 0, "Rojo", 100.0)
        self.assertEqual(self.mixer.colores_actuales.tamaño(), 1)
        
        resultado = self.mixer.limpiar_mezcla()
        self.assertIs(resultado, self.mixer)  # Builder pattern
        self.assertEqual(self.mixer.colores_actuales.tamaño(), 0)
        self.assertEqual(len(self.mixer.porcentajes_actuales), 0)


if __name__ == '__main__':
    unittest.main()