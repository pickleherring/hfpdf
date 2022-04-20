"""Get the content of a story from Hentai Foundry.
"""

import bs4
import regex
import requests


BASE_URL = 'https://www.hentai-foundry.com/stories/user/_/'
REQUEST_PARAMS = {'enterAgree': 1}
PARSER = 'lxml'
CHAPTER_URL_PATTERN = regex.compile(r'/stories/user/[^/]+/[^/]+/[^/]+/(?P<id>[0-9]+)/Chapter-(?P<number>[0-9]+)/')


# %% misc functions

def clean_html(html_tag, div=True, rel=True, style=True):
    """Remove unwanted elements from HTML.
    
    argument html_tag: bs4.Tag
    
    returns: str cleaned HTML
    """
    
    # remove inner divs
    if div:
        for div in html_tag.find_all('div'):
            div.decompose()
    
    # remove invalid rel tag from links
    if rel:
        for a in html_tag.find_all('a', attrs={'rel': 'nofollow'}):
            del a['rel']
            
    # remove unsupported styling
    if style:
        for span in html_tag.find_all('span'):
            if span.has_attr('style'):
                del span['style']
    
    return html_tag.decode_contents()


# %% page retrieval functions

def get_page(url):
    """Get the contents of an HF page.
    
    argument url: str URL
    
    returns: bs4.BeautifulSoup of page contents
    """
    
    r = requests.get(url, params=REQUEST_PARAMS)
    
    print(r.status_code, r.reason, url)
    
    return bs4.BeautifulSoup(r.text, features=PARSER)
    

def get_story_page(story_id):
    """Get the frontpage of a story.
    
    argument story_id: str or int story ID number
    
    returns bs4.BeautifulSoup of page contents
    """
    
    url = f'{BASE_URL}{story_id}/_'
    
    return get_page(url)


def get_chapter_page(story_id, chapter_id, chapter_num):
    """Get a chapter page.
    
    argument story_id: str or int story ID number
    argument chapter_id: str or int chapter ID number
    
    returns bs4.BeautifulSoup of page contents
    """
    
    url = f'{BASE_URL}{story_id}/_/{chapter_id}/Chapter-{chapter_num}/_'
    
    return get_page(url)


# %% info search functions

def get_title(page):
    """Get the title of a story or chapter.
    
    argument page: bs4.BeautifulSoup of page
    
    returns: str title
    """
    
    return page.find('h1', attrs={'class': 'titleSemantic'}).get_text()


def get_author(story_page):
    """Get the author of a story.
    
    argument story_page: bs4.BeautifulSoup of story frontpage
    
    returns: str author
    """
    
    story_info = story_page.find('td', attrs={'class': 'storyInfo'})
    
    return story_info.find('a').get_text()


def get_description(story_page):
    """Get the description of a story.
    
    argument story_page: bs4.BeautifulSoup of story frontpage
    
    returns: str HTML-formatted description
    """
    
    description = story_page.find('td', attrs={'class': 'storyDescript'})
    
    return clean_html(description)


def get_chapter_ids(story_page):
    """Get the chapter ID numbers for a story.
    
    argument story_page: bs4.BeautifulSoup of story frontpage
    
    returns: list of dict {'number': int, 'id': int}
    """
    
    chapters = []
    chapters_section = story_page.find('section', attrs={'id': 'yw0'})
    
    for a in chapters_section.find_all('a'):
        info = {}
        m = CHAPTER_URL_PATTERN.search(a['href'])
        for item in ('number', 'id'):
            info[item] = m.group(item)
        chapters.append(info)
    
    return chapters
    

def get_chapter_text(chapter_page):
    """Get the text of a chapter.
    
    argument chapter_page: bs4.BeautifulSoup of chapter page
    
    returns: str HTML-formatted text
    """
    
    chapter_section = chapter_page.find('section', attrs={'id': 'viewChapter'})
    text_box = chapter_section.find('div', attrs={'class': 'boxbody'})
    
    return clean_html(text_box)


# %% main function

def get_story(story_id):
    """Get the full content of a story from HF.
    
    argument story_id: str or int story ID number
    
    returns dict {'title': str, 'author': str, 'id': int, 'description': str, \
    'chapters': list of dict {'number': int, 'title': str, 'id': int, 'text': str}}
    """
    
    story = {'id': story_id}
    
    story_page = get_story_page(story_id)
    
    story['title'] = get_title(story_page)
    story['author'] = get_author(story_page)
    story['description'] = get_description(story_page)
    story['chapters'] = get_chapter_ids(story_page)
    
    for chapter in story['chapters']:
        chapter_page = get_chapter_page(story_id, chapter['id'], chapter['number'])
        chapter['title'] = get_title(chapter_page)
        chapter['text'] = get_chapter_text(chapter_page)
    
    return story
