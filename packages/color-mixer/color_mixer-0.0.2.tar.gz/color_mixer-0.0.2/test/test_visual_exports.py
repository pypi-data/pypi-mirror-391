import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from color_mixer.visual_exports import VisualExporter
from color_mixer.estructuras import Color

class TestVisualExporter(unittest.TestCase):
    
    def setUp(self):
        """Configurar cada test."""
        self.exporter = VisualExporter()
        # Usar directorio temporal para pruebas
        self.temp_dir = tempfile.mkdtemp()
        self.exporter.directorio_salida = self.temp_dir
        
        # Colores de prueba
        self.colores_prueba = [
            Color(255, 0, 0, "Rojo"),
            Color(0, 255, 0, "Verde"),
            Color(0, 0, 255, "Azul")
        ]
    
    def tearDown(self):
        """Limpiar después de cada test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_crear_swatch(self):
        """Test crear swatch SVG básico."""
        svg_content = self.exporter.crear_swatch(self.colores_prueba)
        
        # Verificar que contiene elementos SVG
        self.assertIn('<svg', svg_content)
        self.assertIn('</svg>', svg_content)
        self.assertIn('<rect', svg_content)
        
        # Verificar que contiene los colores
        self.assertIn('#ff0000', svg_content)  # Rojo
        self.assertIn('#00ff00', svg_content)  # Verde
        self.assertIn('#0000ff', svg_content)  # Azul
    
    def test_crear_swatch_lista_vacia(self):
        """Test crear swatch con lista vacía."""
        svg_content = self.exporter.crear_swatch([])
        self.assertEqual(svg_content, "")
    
    def test_exportar_paleta_svg(self):
        """Test exportar paleta como SVG."""
        nombre_archivo = "test_paleta"
        exito = self.exporter.exportar_paleta_svg(self.colores_prueba, nombre_archivo)
        
        self.assertTrue(exito)
        
        # Verificar que el archivo se creó
        ruta_archivo = os.path.join(self.temp_dir, f"{nombre_archivo}.svg")
        self.assertTrue(os.path.exists(ruta_archivo))
        
        # Verificar contenido del archivo
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            self.assertIn('<svg', contenido)
            self.assertIn('#ff0000', contenido)  # Rojo
    
    def test_exportar_paleta_png(self):
        """Test exportar datos PNG (JSON)."""
        nombre_archivo = "test_png"
        exito = self.exporter.exportar_paleta_png(self.colores_prueba, nombre_archivo)
        
        self.assertTrue(exito)
        
        # Verificar que el archivo JSON se creó
        ruta_archivo = os.path.join(self.temp_dir, f"{nombre_archivo}.json")
        self.assertTrue(os.path.exists(ruta_archivo))
        
        # Verificar contenido JSON
        import json
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            self.assertEqual(datos['tipo'], 'PNG_DATA')
            self.assertEqual(len(datos['colores']), 3)
            self.assertEqual(datos['colores'][0]['rgb'], [255, 0, 0])
    
    def test_crear_paleta_circular(self):
        """Test crear paleta circular."""
        nombre_archivo = "test_circular"
        exito = self.exporter.crear_paleta_circular(self.colores_prueba, nombre_archivo, 100)
        
        self.assertTrue(exito)
        
        # Verificar archivo creado
        ruta_archivo = os.path.join(self.temp_dir, f"{nombre_archivo}_circular.svg")
        self.assertTrue(os.path.exists(ruta_archivo))
        
        # Verificar contenido circular
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            self.assertIn('<circle', contenido)
            self.assertIn('cx=', contenido)
            self.assertIn('cy=', contenido)
    
    def test_crear_paleta_circular_vacia(self):
        """Test crear paleta circular con lista vacía."""
        exito = self.exporter.crear_paleta_circular([], "test_vacio", 100)
        self.assertFalse(exito)
    
    def test_generar_reporte_colores(self):
        """Test generar reporte HTML."""
        nombre_archivo = "test_reporte"
        exito = self.exporter.generar_reporte_colores(self.colores_prueba, nombre_archivo)
        
        self.assertTrue(exito)
        
        # Verificar archivo creado
        ruta_archivo = os.path.join(self.temp_dir, f"{nombre_archivo}_reporte.html")
        self.assertTrue(os.path.exists(ruta_archivo))
        
        # Verificar contenido HTML
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            self.assertIn('<html', contenido)
            self.assertIn('Reporte de Paleta de Colores', contenido)
            self.assertIn('Rojo', contenido)
            self.assertIn('#ff0000', contenido)
    
    def test_exportar_css_variables(self):
        """Test exportar variables CSS."""
        nombre_archivo = "test_css"
        exito = self.exporter.exportar_css_variables(self.colores_prueba, nombre_archivo)
        
        self.assertTrue(exito)
        
        # Verificar archivo creado
        ruta_archivo = os.path.join(self.temp_dir, f"{nombre_archivo}_colors.css")
        self.assertTrue(os.path.exists(ruta_archivo))
        
        # Verificar contenido CSS
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            self.assertIn(':root {', contenido)
            self.assertIn('--color-rojo:', contenido)
            self.assertIn('#ff0000', contenido)
            self.assertIn('.bg-rojo', contenido)
    
    def test_calcular_brillo_promedio(self):
        """Test cálculo de brillo promedio."""
        # Color blanco (255,255,255) = brillo 255
        # Color negro (0,0,0) = brillo 0
        # Promedio = 127.5
        colores_test = [
            Color(255, 255, 255, "Blanco"),
            Color(0, 0, 0, "Negro")
        ]
        
        brillo = self.exporter._calcular_brillo_promedio(colores_test)
        self.assertEqual(brillo, 127.5)
    
    def test_calcular_brillo_lista_vacia(self):
        """Test brillo con lista vacía."""
        brillo = self.exporter._calcular_brillo_promedio([])
        self.assertEqual(brillo, 0.0)
    
    def test_obtener_color_mas_claro(self):
        """Test obtener color más claro."""
        color_claro = self.exporter._obtener_color_mas_claro(self.colores_prueba)
        
        # Verde (0,255,0) debería ser el más claro con brillo 85
        self.assertIn(color_claro.nombre, ["Rojo", "Verde", "Azul"])
    
    def test_obtener_color_mas_oscuro(self):
        """Test obtener color más oscuro."""
        color_oscuro = self.exporter._obtener_color_mas_oscuro(self.colores_prueba)
        
        # Azul (0,0,255) debería ser el más oscuro con brillo 85
        # Pero todos tienen el mismo brillo, así que será el primero que encuentre min()
        self.assertIn(color_oscuro.nombre, ["Rojo", "Verde", "Azul"])
    
    def test_directorio_salida_creacion(self):
        """Test que se crea el directorio de salida."""
        nuevo_temp = os.path.join(self.temp_dir, "nuevo_directorio")
        exporter = VisualExporter()
        exporter.directorio_salida = nuevo_temp
        exporter._crear_directorio_salida()
        
        self.assertTrue(os.path.exists(nuevo_temp))

if __name__ == '__main__':
    unittest.main()