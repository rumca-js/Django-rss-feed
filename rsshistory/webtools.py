import logging
import re
import urllib.request, urllib.error, urllib.parse
from urllib.parse import urlparse


class Page(object):
    def __init__(self, url):
        self.url = url
        self.contents = None

    def is_valid(self):
        if not self.contents:
            self.contents = self.get_contents()

        if self.contents:
            return True
        else:
            return False;

    def get_contents(self):
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}

        try:
            req = urllib.request.Request(self.url, headers=hdr)
            handle = urllib.request.urlopen(req)
            thebytes = handle.read()
            return thebytes.decode('UTF-8')
        except Exception as e:
           logging.critical(e, exc_info=True)

    def get_language(self):
        if not self.contents:
            self.contents = self.get_contents()

        if not self.contents:
            return 'en-US'

        whlang = self.contents.find("lang")
        if whlang >= 0:
            lang = self.extract_html(self.contents, '"', '"', whlang)

            if lang.find("en") == -1 and lang.find("pl") == -1:
                return 'en-US'

            return lang

    def extract_html(self, text, tag, closingtag, wh = None):
        if not wh:
            wh = 0

        wh = text.find(tag, wh)

        if wh > 0:
            wh2 = text.find(closingtag, len(tag) + wh + 1)

            if wh2 > 0:
                title = text[wh + len(tag):wh2]
                if title.strip() != "":
                    return title

    def get_domain(self):
        items = urlparse(self.url)
        return items.scheme + "://" + items.netloc

    def get_title(self):
        if not self.contents:
            self.contents = self.get_contents()

        if not self.contents:
            return None

        wh1 = self.contents.find("<title", 0)
        wh2 = self.contents.find("</title", wh1+1)

        title = self.contents[wh1+7: wh2].strip()

        return title

    def is_link_valid(self, address):
        return self.is_link_valid_domain(address)

    def is_link_valid_domain(self, address):
        if not address.startswith(self.get_domain()):
            return False
        return True

    def get_links(self):
        import re
        import requests
        links = set()

        page = self.get_contents()

        wh = 1
        while wh:
            wh = page.find('<a href="', wh + 1)

            if wh > 0:
                #print(wh)
                text = self.extract_html(page, '<a href="', '"', wh)

                if text:
                    text = text.strip()
                    if text.startswith("/"):
                        text = self.url + text

                    if not self.is_link_valid(text):
                        continue

                    if text != "" and len(text) > 1:
                        links.add(text)
            else:
                break

        return links
