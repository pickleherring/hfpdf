"""Get the content of a story from Hentai Foundry and save as PDF.
"""

import tempfile

from reportlab import platypus
from reportlab.lib import styles

import hfget


SECTION_SPACING = 20
PAGENUM_SPACING = 50

STYLE_SHEETS = styles.getSampleStyleSheet()
DEFAULT_STYLE = STYLE_SHEETS['Normal']
TITLE_STYLE = STYLE_SHEETS['Title']
HEADING_STYLE = STYLE_SHEETS['Heading2']
TEXT_STYLE = STYLE_SHEETS['BodyText']


# %% misc functions

def add_page_number(canvas, doc):
    
    page_num = str(canvas.getPageNumber() - 1)
    canvas.drawRightString(PAGENUM_SPACING, PAGENUM_SPACING, page_num)


# %% main functions

def story_to_pdf(story, filename=None):
    """Convert an HF story to PDF.
    
    argument story: dict of story contents as returned by hfget.get_story()
    argument filename: str file to write to
    
    returns: PDF data as bytes
    """
    
    doc = []
    
    title = story['title']
    author = story['author']
    heading = f'{title} by {author}'
    doc.append(platypus.Paragraph(heading, TITLE_STYLE))
    doc.append(platypus.Spacer(0, SECTION_SPACING))
    
    doc.append(platypus.Paragraph(story['description'], DEFAULT_STYLE))
    doc.append(platypus.Spacer(0, SECTION_SPACING))
    
    doc.append(platypus.Paragraph('Contents', HEADING_STYLE))
    
    for ch in story['chapters']:
        title = ch['title']
        number = ch['number']
        link = f'<a href="#{number}">{title}</a>'
        doc.append(platypus.Paragraph(link, DEFAULT_STYLE))
    
    for ch in story['chapters']:
        title = ch['title']
        number = ch['number']
        anchor = f'<a name="{number}"></a>{title}'
        doc.append(platypus.PageBreak())
        doc.append(platypus.Paragraph(anchor, HEADING_STYLE))
        doc.append(platypus.Spacer(0, SECTION_SPACING))
        doc.append(platypus.Paragraph(ch['text'], TEXT_STYLE))
    
    with tempfile.TemporaryFile() as f:
        template = platypus.SimpleDocTemplate(f, title=story['title'])
        template.build(doc, onLaterPages=add_page_number)
        f.seek(0)
        pdf_data = f.read()
    
    if filename:
        with open(filename, 'wb') as f:
            f.write(pdf_data)
    
    return pdf_data


def get_story_as_pdf(story_id, filename=None):
    """Get an HF story and convert to PDF.
    
    argument story_id: str or int story ID number
    argument filename: str file to write to
    
    returns: PDF data as bytes
    """
    
    story = hfget.get_story(story_id)
    pdf_data = story_to_pdf(story, filename=filename)
    
    return pdf_data


if __name__ == '__main__':
    
    import webbrowser
    
    story_id = input('Story ID: ')
    filename = story_id + '.pdf'    
    get_story_as_pdf(story_id, filename=filename)
    webbrowser.open(filename)
