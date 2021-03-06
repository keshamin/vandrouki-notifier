from collections import OrderedDict

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin


class Post(object):
    def __init__(self, post_id, link, title, content):
        self.post_id = post_id
        self.link = link
        self.title = title
        self.content = content

    @classmethod
    def from_link(cls, link):
        response = requests.get(link)
        if response.status_code != 200:
            raise Exception('Failed to get a page.')

        soup = BeautifulSoup(response.text, 'html.parser')
        post_id = soup.find('div', 'type-post')['id']
        post_title = str(soup.find('h1', 'entry-title').string)
        post_content = str(soup.find('div', 'entry-content'))
        return Post(post_id, link, post_title, post_content)

    def contains_keywords(self, keywords_list):
        found = False

        for keyword in keywords_list:
            if found:
                break
            keyword = keyword.lower()
            if keyword in self.content.lower() or keyword in self.title.lower():
                found = True
        return found


class VandroukiParser(object):

    def __init__(self, vandrouki_url):
        self.vandrouki_url = vandrouki_url
        self._post_id_and_link_generator = self._post_id_and_link_gen()
        self.keywords_list = []

    def _post_id_and_link_gen(self):
        page_num = 1
        while True:
            url = urljoin(self.vandrouki_url, '/page/{num}'.format(num=page_num))
            for post_id, link in self._collect_posts_links_from_page(url).items():
                yield post_id, link
            page_num += 1

    def _get_next_post_id_and_link(self):
        return next(self._post_id_and_link_generator)

    def collect_posts_links(self, num=1000, until_id=None):
        result = OrderedDict()
        i = 0
        while i != num:
            post_id, link = self._get_next_post_id_and_link()
            if until_id == post_id:
                break
            i += 1
            result[post_id] = link
        return result

    @staticmethod
    def _collect_posts_links_from_page(page_url):
        post_id_to_link = {}

        response = requests.get(page_url)
        if response.status_code != 200:
            raise Exception('Failed to get a page.')

        soup = BeautifulSoup(response.text, 'html.parser')

        posts_area = soup.find(id='primary')
        for post in posts_area.find_all('div', 'post'):
            post_id_to_link[post['id']] = post.find('a')['href']

        return post_id_to_link

    def post_contains_keywords(self, post_url, keywords_list=None):
        if keywords_list is None:
            keywords_list = self.keywords_list

        found_keywords = []

        response = requests.get(post_url)
        if response.status_code != 200:
            raise Exception('Failed to get a page.')

        soup = BeautifulSoup(response.text, 'html.parser')
        post_title = str(soup.find('h1', 'entry-title')).lower()
        post_content = str(soup.find('div', 'entry-content')).lower()
        for keyword in keywords_list:
            keyword = keyword.lower()
            if keyword in post_content or keyword in post_title:
                found_keywords.append(keyword)

        return found_keywords

