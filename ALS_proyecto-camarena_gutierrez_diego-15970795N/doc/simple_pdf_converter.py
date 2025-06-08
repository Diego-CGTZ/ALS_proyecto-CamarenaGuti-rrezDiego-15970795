#!/usr/bin/env python3
"""
Script simplificado para convertir documentación markdown a PDF usando reportlab
Autor: Diego Camarena Gutiérrez
DNI: 15970795N
"""

import markdown
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor
import os
import re

def clean_html_tags(text):
    """Elimina tags HTML básicos del texto"""
    # Limpiar tags HTML comunes
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    return text.strip()

def markdown_to_pdf_simple(markdown_file, output_pdf):
    """
    Convierte un archivo markdown a PDF usando reportlab
    """
    print(f"🔄 Convirtiendo {markdown_file} a PDF...")
    
    # Leer el archivo markdown
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para títulos
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        textColor=HexColor('#2c3e50'),
        alignment=0
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        textColor=HexColor('#34495e'),
        alignment=0
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=4,  # Justificado
        textColor=HexColor('#333333')
    )
    
    # Estilo para código
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        spaceAfter=12,
        textColor=HexColor('#e74c3c'),
        fontName='Courier'
    )
    
    # Procesar contenido línea por línea
    story = []
    lines = markdown_content.split('\n')
    
    # Título principal
    story.append(Paragraph("DOCUMENTACIÓN TÉCNICA", title_style))
    story.append(Paragraph("Sistema de Gestión ALS - Aplicación Web Flask", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Información del autor
    story.append(Paragraph("<b>Autor:</b> Diego Camarena Gutiérrez", normal_style))
    story.append(Paragraph("<b>DNI:</b> 15970795N", normal_style))
    story.append(Paragraph("<b>Asignatura:</b> ALS (Análisis, Lógica y Sistemas)", normal_style))
    story.append(Paragraph("<b>Fecha:</b> Junio 2025", normal_style))
    story.append(Spacer(1, 30))
    
    current_paragraph = ""
    in_code_block = False
    
    for line in lines:
        line = line.strip()
        
        # Saltar líneas vacías al inicio
        if not line and not current_paragraph:
            continue
            
        # Detectar bloques de código
        if line.startswith('```'):
            if in_code_block:
                # Fin del bloque de código
                if current_paragraph:
                    story.append(Paragraph(clean_html_tags(current_paragraph), code_style))
                    current_paragraph = ""
                in_code_block = False
            else:
                # Inicio del bloque de código
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, normal_style))
                    current_paragraph = ""
                in_code_block = True
            continue
            
        if in_code_block:
            current_paragraph += line + "<br/>"
            continue
            
        # Detectar títulos
        if line.startswith('# '):
            if current_paragraph:
                story.append(Paragraph(current_paragraph, normal_style))
                current_paragraph = ""
            story.append(PageBreak())
            title_text = line[2:].strip()
            story.append(Paragraph(title_text, title_style))
            continue
            
        elif line.startswith('## '):
            if current_paragraph:
                story.append(Paragraph(current_paragraph, normal_style))
                current_paragraph = ""
            subtitle_text = line[3:].strip()
            story.append(Paragraph(subtitle_text, subtitle_style))
            continue
            
        elif line.startswith('### '):
            if current_paragraph:
                story.append(Paragraph(current_paragraph, normal_style))
                current_paragraph = ""
            subtitle_text = line[4:].strip()
            story.append(Paragraph(f"<b>{subtitle_text}</b>", normal_style))
            continue
            
        # Líneas vacías terminan párrafos
        elif not line:
            if current_paragraph:
                story.append(Paragraph(current_paragraph, normal_style))
                current_paragraph = ""
            continue
            
        # Texto normal
        else:
            if current_paragraph:
                current_paragraph += " "
            current_paragraph += line
    
    # Agregar último párrafo si existe
    if current_paragraph:
        story.append(Paragraph(current_paragraph, normal_style))
    
    # Generar PDF
    doc.build(story)
    print(f"✅ PDF generado: {output_pdf}")

def main():
    """Función principal"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Archivos a convertir
    files_to_convert = [
        'documentacion_tecnica.md',
        'diagrama_clases.md',
        'diagramas_secuencia.md',
        'README_ENTREGA.md'
    ]
    
    print("🔄 Iniciando conversión de documentación a PDF...")
    
    for md_file in files_to_convert:
        input_file = os.path.join(current_dir, md_file)
        output_file = os.path.join(current_dir, md_file.replace('.md', '.pdf'))
        
        if os.path.exists(input_file):
            try:
                markdown_to_pdf_simple(input_file, output_file)
            except Exception as e:
                print(f"❌ Error al convertir {md_file}: {str(e)}")
        else:
            print(f"⚠️  Archivo no encontrado: {md_file}")
    
    print("\n✅ Proceso de conversión completado!")
    print("\n📋 Archivos PDF generados:")
    
    # Listar archivos PDF creados
    for file in os.listdir(current_dir):
        if file.endswith('.pdf'):
            file_path = os.path.join(current_dir, file)
            size = os.path.getsize(file_path) / 1024  # KB
            print(f"   📄 {file} ({size:.1f} KB)")

if __name__ == "__main__":
    main()
