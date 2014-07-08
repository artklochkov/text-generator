# -*- coding: utf-8 -*-
from Queue import Queue
import os
import requests
from BeautifulSoup import BeautifulSoup, Tag
import logging

class crawler:

    __DEFAULT_BLOOMBERG_HOST = 'http://www.bloomberg.com/'
    __DEFAULT_PAGES_NUMBER_TO_LOG_THRESHOLD = 100
    __DEFAULT_BLOOMBERG_FILE = "E:/BLOOMBERG/texts.txt"
    __DEFAULT_INDEX_FILE = "E:/BLOOMBERG/index"
    __DEFAULT_INDEX_SEPARATOR = '|'
    __ARTICLE_LENGTH_THRESHOLD = 100

    logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG)

    def __init__(self):
        self.__index_counter = 0
        self.__index_counter_2 = 0
        self.__links_queue = Queue()
        self.__links_set = set()

    # save page content on disk and make note in links dictionary file
    def __index_page(self, text, link):
        paragraphs = self.__parse_article_content(text)
        if len(paragraphs) == 0:
            return
        plain_article = (os.linesep + os.linesep).join(paragraphs)
        with open(self.__DEFAULT_BLOOMBERG_FILE, 'a') as f:
            f.write(plain_article.encode('utf-8'))
            f.close()
        self.__index_counter += 1

    # make http request to link
    def __get_content_from_link(self, link):
        r = requests.get(self.__DEFAULT_BLOOMBERG_HOST + link)
        text = r.text
        # return text.encode('utf-8')
        return text

    # parse page and add links to queue
    def __search_for_links(self, content):
        soup = BeautifulSoup(content)
        links = [tag['href'] for tag in soup.findAll('a', href=True) if tag['href'].startswith('/news')]
        return links

    def __parse_article_content(self, content):
        soup =  BeautifulSoup(content)
        article_body = soup.find('div', {'itemprop' : 'articleBody'})
        if article_body is not None:
            paragraphs = [tag.text.replace('\n',' ') for tag in article_body.contents if isinstance(tag, Tag)]
            paragraphs = paragraphs[:-2]
            return paragraphs
        else:
            return []

    # start to crawle from link in start_page argument
    def crawle(self, start_page=__DEFAULT_BLOOMBERG_HOST):
        self.__links_set.add(start_page)
        self.__links_queue.put(start_page)
        downloaded_pages_counter = 0
        while (not self.__links_queue.empty()):
            current_link = self.__links_queue.get(block=False)
            try:
                text = self.__get_content_from_link(current_link)
                self.__index_page(text, current_link)
                links = self.__search_for_links(text)
                [self.__links_queue.put(link) for link in links if not link in self.__links_set]
                self.__links_set.update(links)
                # piece of debug information, just to understand that all things are right
                downloaded_pages_counter += 1
                if (downloaded_pages_counter % self.__DEFAULT_PAGES_NUMBER_TO_LOG_THRESHOLD == 0):
                    print downloaded_pages_counter, 'pages processed', self.__links_queue.qsize(), ' links in queue', len(self.__links_set), ' links in set'
            except Exception as e:
                logging.warn("link " + current_link + ' was processed incorrectly')
                logging.exception(e)

bloomberg_crawler = crawler()
bloomberg_crawler.crawle()