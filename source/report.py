# Format a sleep position study analysis and generate a PDF file
# John Lamb 2025
# See: https://nicd.org.uk/knowledge-hub/creating-pdf-reports-with-reportlab-and-pandas

import analyse
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch

report_filename='report.pdf'

padding = dict(
  leftPadding=72, 
  rightPadding=72,
  topPadding=72,
  bottomPadding=18)

portrait_frame = Frame(0, 0, *A4, **padding)
landscape_frame = Frame(0, 0, *landscape(A4), **padding,showBoundary=0)
table_frame=Frame(
    x1=1*inch,
    y1=A4[0]-4.3*inch,
    width=4 * inch,
    height=2 * inch,
    leftPadding=0,
    bottomPadding=0,
    rightPadding=0,
    topPadding=0,
    id=None,
    showBoundary=0
)
pie_frame=Frame(
    x1=6*inch,
    y1=A4[0]-4.5*inch,
    width=4 * inch,
    height=4 * inch,
    leftPadding=0,
    bottomPadding=0,
    rightPadding=0,
    topPadding=0,
    id=None,
    showBoundary=0
)

line_graph_frame =Frame(
    x1=1*inch,
    y1=0.5*inch,
    width=10 * inch,
    height=3 * inch,
    leftPadding=0,
    bottomPadding=0,
    rightPadding=0,
    topPadding=0,
    id=None,
    showBoundary=0
)

from reportlab.platypus import PageTemplate

landscape_template = PageTemplate(
  id='landscape', 
  frames=[landscape_frame,pie_frame,table_frame,line_graph_frame], 
  pagesize=landscape(A4))

from reportlab.platypus import BaseDocTemplate

doc = BaseDocTemplate(report_filename,pageTemplates=[
    landscape_template
  ]
)

import io
from reportlab.platypus import Image
from reportlab.lib.units import inch

# Convert matplotlib figure to an image
def fig2image(f):
    buf = io.BytesIO()
    f.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    x, y = f.get_size_inches()
    return Image(buf, x * inch, y * inch)

from reportlab.platypus import Table, Paragraph
from reportlab.lib import colors

# Convert pandas dataframe to reportLab Table
def df2table(df):
    return Table(
      [[Paragraph(col) for col in df.columns]] + df.values.tolist(), 
      style=[
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('LINEBELOW',(0,0), (-1,0), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.lightgrey, colors.white]),
        ('LEFTPADDING',(0,0),(-1,-1),52),
        ('RIGHTPADDING',(1,0),(1,-1),52),
        ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('ALIGN',(1,0),(1,-1),'RIGHT'),
        
        ]
      )

import pandas as pd
import matplotlib.pyplot as plt

from reportlab.platypus import NextPageTemplate, PageBreak,FrameBreak
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# Composite the page
story = [
    Paragraph('Sleep Position Report', styles['Heading2']),
    Paragraph('Start: '+analyse.start_datetime_str),
    Paragraph('End: '+analyse.end_datetime_str),
    Paragraph(f'Elapsed time: {analyse.elapsed_time_str}'),
    FrameBreak(),
    fig2image(analyse.pie_fig),
    FrameBreak(),
    Paragraph('Position Durations (minutes)', styles['Heading2']),
    df2table(analyse.totals_df),
    FrameBreak(),
    Paragraph('Timeline', styles['Heading2']),
    fig2image(analyse.linechart_fig),
]
# Save the PDF
doc.build(story)