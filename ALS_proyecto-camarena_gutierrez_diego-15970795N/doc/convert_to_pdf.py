#!/usr/bin/env python3
"""
Script para convertir documentación markdown a PDF
Autor: Diego Camarena Gutiérrez
DNI: 15970795N
"""

import markdown2
from weasyprint import HTML, CSS
import os

def convert_markdown_to_pdf(markdown_file, output_pdf):
    """
    Convierte un archivo markdown a PDF usando weasyprint
    """
    # Leer el archivo markdown
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convertir markdown a HTML
    html_content = markdown2.markdown(
        markdown_content, 
        extras=[
            'fenced-code-blocks',
            'tables', 
            'header-ids',
            'toc',
            'break-on-newline'
        ]
    )
    
    # CSS para el PDF
    css_content = """
    @page {
        size: A4;
        margin: 2cm;
        @top-center {
            content: "Documentación Técnica - Sistema ALS";
            font-size: 10pt;
            color: #666;
        }
        @bottom-center {
            content: "Página " counter(page) " de " counter(pages);
            font-size: 10pt;
            color: #666;
        }
    }
    
    body {
        font-family: 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
        margin: 0;
        padding: 0;
    }
    
    h1 {
        color: #2c3e50;
        font-size: 24pt;
        margin-top: 30pt;
        margin-bottom: 20pt;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10pt;
        page-break-before: always;
    }
    
    h1:first-child {
        page-break-before: auto;
    }
    
    h2 {
        color: #34495e;
        font-size: 18pt;
        margin-top: 25pt;
        margin-bottom: 15pt;
        border-bottom: 2px solid #bdc3c7;
        padding-bottom: 5pt;
    }
    
    h3 {
        color: #2c3e50;
        font-size: 14pt;
        margin-top: 20pt;
        margin-bottom: 10pt;
    }
    
    h4 {
        color: #34495e;
        font-size: 12pt;
        margin-top: 15pt;
        margin-bottom: 8pt;
    }
    
    p {
        margin-bottom: 12pt;
        text-align: justify;
    }
    
    ul, ol {
        margin-bottom: 12pt;
        padding-left: 20pt;
    }
    
    li {
        margin-bottom: 6pt;
    }
    
    code {
        background-color: #f8f9fa;
        color: #e74c3c;
        padding: 2pt 4pt;
        border-radius: 3pt;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
    }
    
    pre {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5pt;
        padding: 15pt;
        margin: 15pt 0;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        line-height: 1.4;
    }
    
    pre code {
        background-color: transparent;
        color: #333;
        padding: 0;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15pt 0;
        font-size: 10pt;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 8pt;
        text-align: left;
    }
    
    th {
        background-color: #f8f9fa;
        font-weight: bold;
        color: #2c3e50;
    }
    
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    blockquote {
        border-left: 4px solid #3498db;
        margin: 15pt 0;
        padding: 10pt 20pt;
        background-color: #f8f9fa;
        font-style: italic;
    }
    
    .page-break {
        page-break-before: always;
    }
    
    .toc {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        padding: 20pt;
        margin: 20pt 0;
        border-radius: 5pt;
    }
    
    .toc h2 {
        margin-top: 0;
        color: #2c3e50;
        border-bottom: none;
    }
    """
    
    # HTML completo con estructura
    full_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Documentación Técnica - Sistema ALS</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Crear CSS object
    css = CSS(string=css_content)
    
    # Convertir a PDF
    html_doc = HTML(string=full_html)
    html_doc.write_pdf(output_pdf, stylesheets=[css])
    
    print(f"✅ PDF generado exitosamente: {output_pdf}")

def main():
    """Función principal"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Archivos a convertir
    files_to_convert = [
        {
            'input': 'documentacion_tecnica.md',
            'output': 'documentacion_tecnica.pdf'
        },
        {
            'input': 'diagrama_clases.md',
            'output': 'diagrama_clases.pdf'
        },
        {
            'input': 'diagramas_secuencia.md',
            'output': 'diagramas_secuencia.pdf'
        },
        {
            'input': 'README_ENTREGA.md',
            'output': 'README_ENTREGA.pdf'
        }
    ]
    
    print("🔄 Iniciando conversión de documentación a PDF...")
    
    for file_info in files_to_convert:
        input_file = os.path.join(current_dir, file_info['input'])
        output_file = os.path.join(current_dir, file_info['output'])
        
        if os.path.exists(input_file):
            try:
                convert_markdown_to_pdf(input_file, output_file)
            except Exception as e:
                print(f"❌ Error al convertir {file_info['input']}: {str(e)}")
        else:
            print(f"⚠️  Archivo no encontrado: {file_info['input']}")
    
    print("\n✅ Proceso de conversión completado!")

if __name__ == "__main__":
    main()
