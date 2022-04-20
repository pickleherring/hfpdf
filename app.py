"""The hfpdf app.
"""

import regex
import streamlit

import hfpdf


EXAMPLE_URL = 'https://www.hentai-foundry.com/stories/user/pickleherring/46750/Sisterhood-Initiation'
STORY_URL_PATTERN = regex.compile(r'/stories/user/[^/]+/(?P<id>[0-9]+)/(?P<title>[^/.]+)')


# %% wrapper function for caching

@streamlit.cache
def get_story(story_id):
    
    return hfpdf.get_story_as_pdf(story_id)


# %% intro

streamlit.title('HF to PDF')
streamlit.markdown('\
Paste the URL of a story from [Hentai Foundry](https://www.hentai-foundry.com) into the box below. \
The app will fetch the story and convert it to PDF (for long stories this may take a while!) \
When it is ready, a **Download** button will appear. \
Click to download!\
')


# %% user input - URL

url = streamlit.text_input(
    'enter a story URL:',
    placeholder=EXAMPLE_URL
)

match = STORY_URL_PATTERN.search(url)

if match:
    story_id = match.group('id')
    story_title = match.group('title')
else:
    story_id = ''
    story_title = ''


# %% download button

if story_id:
    
    filename = f'{story_title}.pdf'
    button_label = f'Download {filename}'
    
    pdf_data = get_story(story_id)
    
    streamlit.download_button(
        button_label,
        pdf_data,
        file_name=filename,
        mime='application/pdf'
    )

else:
    
    streamlit.markdown('*enter a valid URL*')


# %% app info

streamlit.markdown('made by [pickleherring](https://nushara.com/pickleherring/links)')
