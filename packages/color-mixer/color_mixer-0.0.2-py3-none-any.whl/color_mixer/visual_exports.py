import os
import json
from typing import List, Tuple, Optional
from .estructuras import Color


class VisualExporter:
    """Clase para exportar paletas de colores a diferentes formatos visuales."""
    
    def __init__(self, directorio_salida: str = None):
        self.directorio_salida = directorio_salida or "colormixer_exports"
        self._crear_directorio_salida()
    
    def configurar_directorio_salida(self, directorio: str):
        """Configura el directorio de salida para los exports."""
        self.directorio_salida = directorio
        self._crear_directorio_salida()
    
    def crear_swatch(self, colores: List[Color], ancho_muestra: int = 100, alto_muestra: int = 100) -> str:
        """
        Genera una representación de muestra de colores en formato SVG.
        
        Args:
            colores: Lista de colores para mostrar
            ancho_muestra: Ancho de cada muestra de color
            alto_muestra: Alto de cada muestra de color
        
        Returns:
            String con el contenido SVG
        """
        if not colores:
            return ""
        
        ancho_total = len(colores) * ancho_muestra
        alto_total = alto_muestra + 60  # Espacio adicional para texto
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{ancho_total}" height="{alto_total}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="white"/>
'''
        
        for i, color in enumerate(colores):
            x = i * ancho_muestra
            
            # Rectángulo de color
            svg_content += f'''    <rect x="{x}" y="0" width="{ancho_muestra}" height="{alto_muestra}" 
                  fill="{color.to_hex()}" stroke="black" stroke-width="1"/>
'''
            
            # Texto con nombre del color
            texto_x = x + ancho_muestra // 2
            svg_content += f'''    <text x="{texto_x}" y="{alto_muestra + 20}" 
                  text-anchor="middle" font-family="Arial" font-size="10" fill="black">
        {color.nombre[:12]}...
    </text>
'''
            
            # Texto con código hex
            svg_content += f'''    <text x="{texto_x}" y="{alto_muestra + 40}" 
                  text-anchor="middle" font-family="Arial" font-size="8" fill="gray">
        {color.to_hex()}
    </text>
'''
        
        svg_content += "</svg>"
        return svg_content
    
    def exportar_paleta_png(self, colores: List[Color], nombre_archivo: str) -> bool:
        """
        Exporta la paleta de colores como imagen PNG.
        Nota: Esta implementación crea un archivo de datos JSON con información de la paleta
        ya que la generación real de PNG requeriría librerías adicionales como PIL.
        """
        try:
            ruta_archivo = os.path.join(self.directorio_salida, f"{nombre_archivo}.json")
            
            datos_paleta = {
                'tipo': 'PNG_DATA',
                'nombre': nombre_archivo,
                'colores': [],
                'metadata': {
                    'ancho_sugerido': len(colores) * 100,
                    'alto_sugerido': 160,
                    'formato': 'RGB'
                }
            }
            
            for color in colores:
                datos_paleta['colores'].append({
                    'nombre': color.nombre,
                    'rgb': color.to_rgb(),
                    'hex': color.to_hex()
                })
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos_paleta, f, indent=2, ensure_ascii=False)
            
            print(f"Datos PNG guardados en: {ruta_archivo}")
            print("Nota: Para generar PNG real, usar: python -c \"from PIL import Image; # código adicional\"")
            return True
            
        except Exception as e:
            print(f"Error exportando a PNG: {e}")
            return False
    
    def exportar_paleta_svg(self, colores: List[Color], nombre_archivo: str, 
                           ancho_muestra: int = 120, alto_muestra: int = 120) -> bool:
        """
        Exporta la paleta de colores como archivo SVG.
        
        Args:
            colores: Lista de colores para exportar
            nombre_archivo: Nombre del archivo (sin extensión)
            ancho_muestra: Ancho de cada muestra
            alto_muestra: Alto de cada muestra
        
        Returns:
            True si se exportó exitosamente
        """
        try:
            svg_content = self.crear_swatch(colores, ancho_muestra, alto_muestra)
            ruta_archivo = os.path.join(self.directorio_salida, f"{nombre_archivo}.svg")
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            print(f"Paleta SVG guardada en: {ruta_archivo}")
            return True
            
        except Exception as e:
            print(f"Error exportando a SVG: {e}")
            return False
    
    def crear_paleta_circular(self, colores: List[Color], nombre_archivo: str, radio: int = 150) -> bool:
        """
        Crea una paleta de colores en disposición circular.
        
        Args:
            colores: Lista de colores
            nombre_archivo: Nombre del archivo
            radio: Radio del círculo
        
        Returns:
            True si se creó exitosamente
        """
        try:
            if not colores:
                return False
            
            import math
            
            tamaño_canvas = radio * 2 + 100
            centro = tamaño_canvas // 2
            
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{tamaño_canvas}" height="{tamaño_canvas}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="white"/>
    <circle cx="{centro}" cy="{centro}" r="{radio + 10}" fill="none" stroke="lightgray" stroke-width="2"/>
'''
            
            angulo_por_color = 2 * math.pi / len(colores)
            radio_muestra = 30
            
            for i, color in enumerate(colores):
                angulo = i * angulo_por_color - math.pi / 2  # Empezar desde arriba
                
                x = centro + radio * math.cos(angulo)
                y = centro + radio * math.sin(angulo)
                
                # Círculo de color
                svg_content += f'''    <circle cx="{x:.1f}" cy="{y:.1f}" r="{radio_muestra}" 
                      fill="{color.to_hex()}" stroke="black" stroke-width="2"/>
'''
                
                # Texto con nombre (posicionado hacia afuera)
                texto_x = centro + (radio + 50) * math.cos(angulo)
                texto_y = centro + (radio + 50) * math.sin(angulo) + 5
                
                svg_content += f'''    <text x="{texto_x:.1f}" y="{texto_y:.1f}" 
                      text-anchor="middle" font-family="Arial" font-size="10" fill="black">
        {color.nombre[:10]}
    </text>
'''
            
            svg_content += "</svg>"
            
            ruta_archivo = os.path.join(self.directorio_salida, f"{nombre_archivo}_circular.svg")
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            print(f"Paleta circular guardada en: {ruta_archivo}")
            return True
            
        except Exception as e:
            print(f"Error creando paleta circular: {e}")
            return False
    
    def generar_reporte_colores(self, colores: List[Color], nombre_archivo: str) -> bool:
        """
        Genera un reporte detallado de los colores en formato HTML.
        
        Args:
            colores: Lista de colores para el reporte
            nombre_archivo: Nombre del archivo
        
        Returns:
            True si se generó exitosamente
        """
        try:
            html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Colores - {nombre_archivo}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .color-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .color-card {{ border: 1px solid #ddd; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .color-preview {{ height: 100px; width: 100%; }}
        .color-info {{ padding: 15px; }}
        .color-name {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
        .color-values {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .value-item {{ background: #f8f8f8; padding: 8px; border-radius: 4px; }}
        .summary {{ margin-top: 30px; padding: 20px; background: #f0f8ff; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reporte de Paleta de Colores</h1>
            <p>Archivo: {nombre_archivo}</p>
            <p>Fecha de generación: {self._obtener_fecha_actual()}</p>
            <p>Total de colores: {len(colores)}</p>
        </div>
        
        <div class="color-grid">
'''
            
            for color in colores:
                rgb_str = f"rgb({color.r}, {color.g}, {color.b})"
                html_content += f'''
            <div class="color-card">
                <div class="color-preview" style="background-color: {color.to_hex()};"></div>
                <div class="color-info">
                    <div class="color-name">{color.nombre}</div>
                    <div class="color-values">
                        <div class="value-item">
                            <strong>HEX:</strong><br>
                            {color.to_hex()}
                        </div>
                        <div class="value-item">
                            <strong>RGB:</strong><br>
                            {rgb_str}
                        </div>
                    </div>
                </div>
            </div>
'''
            
            # Resumen estadístico
            html_content += f'''
        </div>
        
        <div class="summary">
            <h2>Resumen Estadístico</h2>
            <p><strong>Brillo promedio:</strong> {self._calcular_brillo_promedio(colores):.1f}/255</p>
            <p><strong>Color más claro:</strong> {self._obtener_color_mas_claro(colores).nombre}</p>
            <p><strong>Color más oscuro:</strong> {self._obtener_color_mas_oscuro(colores).nombre}</p>
        </div>
    </div>
</body>
</html>
'''
            
            ruta_archivo = os.path.join(self.directorio_salida, f"{nombre_archivo}_reporte.html")
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Reporte HTML generado en: {ruta_archivo}")
            return True
            
        except Exception as e:
            print(f"Error generando reporte HTML: {e}")
            return False
    
    def exportar_css_variables(self, colores: List[Color], nombre_archivo: str) -> bool:
        """
        Exporta los colores como variables CSS.
        
        Args:
            colores: Lista de colores
            nombre_archivo: Nombre del archivo
        
        Returns:
            True si se exportó exitosamente
        """
        try:
            css_content = f"""/* Variables CSS para paleta de colores - {nombre_archivo} */
/* Generado automáticamente por ColorMixer */

:root {{
"""
            
            for i, color in enumerate(colores):
                nombre_var = color.nombre.lower().replace(' ', '-').replace('_', '-')
                css_content += f"    --color-{nombre_var}: {color.to_hex()};\n"
                css_content += f"    --color-{i + 1}: {color.to_hex()};\n"
            
            css_content += "}\n\n"
            
            # Agregar clases utilitarias
            css_content += "/* Clases utilitarias */\n"
            for i, color in enumerate(colores):
                nombre_var = color.nombre.lower().replace(' ', '-').replace('_', '-')
                css_content += f".bg-{nombre_var} {{ background-color: var(--color-{nombre_var}); }}\n"
                css_content += f".text-{nombre_var} {{ color: var(--color-{nombre_var}); }}\n"
            
            ruta_archivo = os.path.join(self.directorio_salida, f"{nombre_archivo}_colors.css")
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            print(f"Variables CSS guardadas en: {ruta_archivo}")
            return True
            
        except Exception as e:
            print(f"Error exportando CSS: {e}")
            return False
    
    def _crear_directorio_salida(self):
        """Crea el directorio de salida si no existe."""
        try:
            if not os.path.exists(self.directorio_salida):
                os.makedirs(self.directorio_salida)
        except Exception as e:
            print(f"Error creando directorio de salida: {e}")
    
    def _obtener_fecha_actual(self) -> str:
        """Obtiene la fecha actual en formato legible."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _calcular_brillo_promedio(self, colores: List[Color]) -> float:
        """Calcula el brillo promedio de una lista de colores."""
        if not colores:
            return 0.0
        
        total_brillo = sum((color.r + color.g + color.b) / 3 for color in colores)
        return total_brillo / len(colores)
    
    def _obtener_color_mas_claro(self, colores: List[Color]) -> Color:
        """Obtiene el color más claro de la lista."""
        if not colores:
            return Color(255, 255, 255, "Blanco por defecto")
        
        return max(colores, key=lambda c: (c.r + c.g + c.b) / 3)
    
    def _obtener_color_mas_oscuro(self, colores: List[Color]) -> Color:
        """Obtiene el color más oscuro de la lista."""
        if not colores:
            return Color(0, 0, 0, "Negro por defecto")
        
        return min(colores, key=lambda c: (c.r + c.g + c.b) / 3)