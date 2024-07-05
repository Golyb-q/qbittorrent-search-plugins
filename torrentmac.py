# VERSION: 1
# AUTHORS: Golyb-q

import sys
import re
import time
from urllib.parse import quote
from novaprinter import prettyPrinter
from helpers import retrieve_url
import threading

class torrentmac(object):
    url = 'https://www.torrentmac.net/'
    name = 'torrentmac.net'
    supported_categories = {'all': ''}

    def get_response(self, link):
        try:
            response = retrieve_url(link)
        except Exception as e:
            response = "error"
            print(f"link|ERROR: ({repr(e)}) {link}|0|0|0||{link}")
        return response
        
    def print_torrent_info(self, link, name, size, desc_link):
        result = {
                'link': link,
                'name': name,
                'size': size,
                'seeds': '0',
                'leech': '0',
                'engine_url': self.url,
                'desc_link': desc_link
            }
        prettyPrinter(result)

    def load_torrent_info(self, link):
        max_attempts = 20
        attempt = 1
        while attempt <= max_attempts:
            response = self.get_response(link)
            if response:
                break
            time.sleep(3)
            attempt += 1

        torrent_pattern = re.compile(r'<a href="([^"]+)" target="_blank" class="btn download-btn">')
        name_pattern = re.compile(r'<th>Name:</th>\s*<td>([^<]+)</td>')
        size_pattern = re.compile(r'<th>Size:</th>\s*<td>([^<]+)</td>')
        torrent_match = torrent_pattern.search(response)
        name_match = name_pattern.search(response)
        size_match = size_pattern.search(response)

        name = name_match.group(1) if name_match else 'error_name'
        size = size_match.group(1) if size_match else -1
        torrent_link = torrent_match.group(1) if torrent_match else 'error_link'

        self.print_torrent_info(torrent_link, name, size, link)

    def load_torrent_url_from_response(self, response):
        pattern = re.compile(r'<h2 class="post-title"><a href="(?P<link>[^"]+)" rel="bookmark"')
        links = pattern.findall(response)
        threads = []
        for link in links:
            thread = threading.Thread(target=self.load_torrent_info, args=(link,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()

    def load_page(self, query, page):
        link = f'{self.url}page/{page}/?s={query}'
        response = self.get_response(link)
        self.load_torrent_url_from_response(response)

    def load_all_page(self, query, max_page):
        threads = []
        for page in range(2, max_page+1):
            thread = threading.Thread(target=self.load_page, args=(query, page))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()

    def get_max_page(self, query):
        link = f'{self.url}page/1/?s={query}'
        response = self.get_response(link)
        max_pages_pattern = re.compile(r'<a class="page-numbers" href="[^"]+/page/(\d+)/\?s=[^"]+">')
        max_pages_matches = max_pages_pattern.findall(response)
        max_pages = max(map(int, max_pages_matches)) if max_pages_matches else 1
        self.load_torrent_url_from_response(response)
        return max_pages

    def search(self, query, cat='all'):
        encoded_query = query.replace(' ', '+')
        max_page = self.get_max_page(encoded_query)
        self.load_all_page(encoded_query, max_page)


if __name__ == "__main__":
    torrentmac().search('GraphicConverter 11.6.3 (5571) Beta')
