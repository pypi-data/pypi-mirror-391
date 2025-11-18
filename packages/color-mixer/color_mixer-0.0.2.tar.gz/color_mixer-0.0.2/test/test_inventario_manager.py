import unittest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from color_mixer.inventario_manager import InventarioManager
from color_mixer.estructuras import Color

class TestInventarioManager(unittest.TestCase):
    
    def setUp(self):
        """Configurar cada test con instancia fresca."""
        # Limpiar singleton para cada test
        InventarioManager._instancia = None
        InventarioManager._inicializado = False
        self.inventario = InventarioManager()
        
        # Colores de prueba
        self.rojo = Color(255, 0, 0, "Rojo Ferrari")
        self.blanco = Color(248, 248, 248, "Blanco Perla")
    
    def tearDown(self):
        """Limpiar después de cada test."""
        # Eliminar archivo de datos si existe
        if os.path.exists(self.inventario.archivo_datos):
            os.remove(self.inventario.archivo_datos)
    
    def test_singleton_pattern(self):
        """Test que InventarioManager es singleton."""
        inventario2 = InventarioManager()
        self.assertIs(self.inventario, inventario2)
    
    def test_registrar_auto_exitoso(self):
        """Test registrar auto correctamente."""
        exito = self.inventario.registrar_auto(
            "Ferrari 488 GTB",
            "FER488R01",
            [self.rojo, self.blanco],
            [70.0, 30.0]
        )
        
        self.assertTrue(exito)
        self.assertEqual(self.inventario.inventario.tamaño(), 1)
    
    def test_registrar_auto_codigo_duplicado(self):
        """Test registrar auto con código duplicado."""
        # Registrar primer auto
        self.inventario.registrar_auto(
            "Ferrari 488 GTB",
            "FER488R01",
            [self.rojo],
            [100.0]
        )
        
        # Intentar registrar con mismo código
        exito = self.inventario.registrar_auto(
            "Ferrari F8 Tributo",
            "FER488R01",  # Código duplicado
            [self.rojo],
            [100.0]
        )
        
        self.assertFalse(exito)
        self.assertEqual(self.inventario.inventario.tamaño(), 1)
    
    def test_porcentajes_invalidos(self):
        """Test registrar auto con porcentajes inválidos."""
        exito = self.inventario.registrar_auto(
            "Ferrari 488 GTB",
            "FER488R01",
            [self.rojo, self.blanco],
            [60.0, 50.0]  # Suman 110%
        )
        
        self.assertFalse(exito)
        self.assertEqual(self.inventario.inventario.tamaño(), 0)
    
    def test_obtener_color_auto(self):
        """Test obtener información de auto registrado."""
        self.inventario.registrar_auto(
            "Ferrari 488 GTB",
            "FER488R01",
            [self.rojo, self.blanco],
            [70.0, 30.0]
        )
        
        info = self.inventario.obtener_color_auto("FER488R01")
        
        self.assertIsNotNone(info)
        self.assertEqual(info['modelo'], "Ferrari 488 GTB")
        self.assertEqual(info['codigo_color'], "FER488R01")
        self.assertEqual(len(info['colores_mezcla']), 2)
        self.assertIsNotNone(info['color_resultante'])
    
    def test_obtener_auto_inexistente(self):
        """Test obtener auto que no existe."""
        info = self.inventario.obtener_color_auto("CODIGO_INEXISTENTE")
        self.assertIsNone(info)
    
    def test_mostrar_colores_existentes(self):
        """Test mostrar lista de colores existentes."""
        self.inventario.registrar_auto(
            "Ferrari 488 GTB",
            "FER488R01",
            [self.rojo],
            [100.0]
        )
        
        colores = self.inventario.mostrar_colores_existentes()
        
        self.assertEqual(len(colores), 1)
        self.assertEqual(colores[0]['codigo'], "FER488R01")
        self.assertEqual(colores[0]['modelo'], "Ferrari 488 GTB")

if __name__ == '__main__':
    unittest.main()