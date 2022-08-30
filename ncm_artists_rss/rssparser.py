"""
filename: rssparser.py
author: hexsix <hexsixology@gmail.com>
date: 2022/08/30
description: 
"""

import logging
import re
import time
from typing import Dict

import feedparser
import httpx

logger = logging.getLogger('rssparser')


class rssparser(object):
    def __init__(self, rss_url: str, use_proxies: bool, proxies: Dict):
        rss_json = self.download(rss_url, use_proxies, proxies)
        self.items = []
        self.parse(rss_json)

    def download(self, rss_url: str, use_proxies: bool, proxies: Dict) -> Dict:
        logger.info('Downloading RSS ...')
        rss_json = {}
        for retry in range(3):
            if retry > 0:
                logger.info(f'The {retry + 1}th attempt, 3 attempts in total.')
            try:
                if use_proxies:
                    with httpx.Client(proxies=proxies) as client:
                        response = client.get(rss_url, timeout=10.0)
                    rss_json = feedparser.parse(response.text)
                else:
                    with httpx.Client() as client:
                        response = client.get(rss_url, timeout=10.0)
                    rss_json = feedparser.parse(response.text)
                if rss_json:
                    break
            except Exception as e:
                if retry + 1 < 3:
                    logger.warning(
                        f'Failed, next attempt will start soon: {e}')
                    time.sleep(6)
                else:
                    logger.error(f'Failed to download RSS: {e}')
        if not rss_json:
            raise Exception('Failed to download RSS.')
        return rss_json

    def parse(self, rss_json: Dict):
        logger.info('Parsing RSS ...')
        filtered_cnt = 0
        for entry in rss_json['entries']:
            try:
                publish_mktime = time.mktime(time.strptime(
                    entry['published'], '%a, %d %b %Y %H:%M:%S GMT'))
                now_mktime = time.time()
                if now_mktime - publish_mktime > 24 * 60 * 60 - 1:
                    filtered_cnt += 1
                    continue
                item = dict()
                item['title'] = entry['title']
                item['author'] = entry['author']
                item['published'] = entry['published']
                item['link'] = entry['link']
                item['album_id'] = re.search(
                    r'\d{4,15}', entry['link']).group()
                item['cover'] = re.search(
                    r'https:\/\/[^\"\s]*', entry['summary']).group()
                self.items.append(item)
            except Exception as e:
                logger.info(f'Exception: {e}')
                continue
        logger.info(
            f"Parse RSS End. {len(self.items)}/{len(rss_json['entries'])} Succeed.")
        return self.items


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    rp = rssparser(
        rss_url='https://rsshub.app/ncm/artist/12390232',
        use_proxies=True,
        proxies={
            "http://": "http://127.0.0.1:8889",
            "https://": "http://127.0.0.1:8889"
        }
    )
    import pprint
    pprint.pprint(rp.items)
