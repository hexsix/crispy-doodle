"""
filename: rssparser.py
author: hexsix <hexsixology@gmail.com>
date: 2022/08/30
description: 
"""

import logging
import re
import time
from typing import Dict, List

from bs4 import BeautifulSoup
import feedparser
import httpx

logger = logging.getLogger('rssparser')


class rssparser(object):
    def __init__(self, rss_url: str, use_proxies: bool, proxies: Dict, creators: List[str]):
        self.creators = creators
        rss_json = self.download(rss_url, use_proxies, proxies)
        self.items = []
        self.parse(rss_json, creators)

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

    def parse(self, rss_json: Dict, creators: List[str]):
        logger.info('Parsing RSS ...')
        filtered_cnt = 0
        for entry in rss_json['entries']:
            try:
                item = dict()

                if 'type_SOU' not in entry['summary']:
                    filtered_cnt += 1
                    continue
                soup = BeautifulSoup(entry['summary'], 'html.parser')
                """work_category
                <div class="work_category type_SOU">
                    <a href="https://www.dlsite.com/maniax/fsr/=/work_type/SOU" target="_blank">
                        ボイス・ASMR
                    </a>
                </div>
                """
                work_category = 'ボイス・ASMR'

                """img
                <img alt="オナサポ科のJK双子ママ♪～焦らしテクで快楽絶頂!～ [犬走り]" class="lazy" src="https://img.dlsite.jp/resize/images2/work/doujin/RJ392000/RJ391233_img_main_240x240.jpg"/>
                """
                # try:
                #     item['img_url'] = soup.select_one('img').attrs['src']
                # except KeyError:
                #     item['img_url'] = ''

                """work_name
                <dt class="work_name">
                    <span class="period_date">
                        2022年06月22日 23時59分 割引終了
                    </span>
                    <div class="icon_wrap">
                        <span class="icon_lead_01 type_exclusive" title="DLsite専売">
                            DLsite専売
                        </span>
                    </div>
                    <a href="https://www.dlsite.com/maniax/work/=/product_id/RJ391233.html" target="_blank" title="オナサポ科のJK双子ママ♪～焦らしテクで快楽絶頂!～">
                        オナサポ科のJK双子ママ♪～焦らしテクで快楽絶頂!～
                    </a>
                </dt>
                """
                item['work_name'] = soup.select_one(
                    '.work_name').select_one('a').attrs['title']

                """ author and filter
                """
                item['author'] = entry['author']
                flag_author_subscribed = False
                for creator in creators:
                    if creator in item['author']:
                        flag_author_subscribed = True
                if not flag_author_subscribed:
                    filtered_cnt += 1
                    continue

                """tags
                """
                item['tags'] = []
                for t in entry['tags']:
                    tag = t['term']
                    if '/' in tag:
                        tag = tag.replace('/', '/#')
                    tag = '#' + tag
                    item['tags'].append(tag)
                item['link'] = entry['link']
                item['rj_code'] = re.search(r'RJ\d*', entry['link']).group()
                self.items.append(item)
            except Exception as e:
                logger.info(f'Exception: {e}')
                continue
        logger.info(
            f"Parse RSS End. {len(self.items)}/{len(rss_json['entries'])} Succeed. {filtered_cnt} filtered. Others failed.")
        return self.items


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    rp = rssparser(
        rss_url='https://rsshub.app/dlsite/new/maniax',
        use_proxies=True,
        proxies={
            "http://": "http://127.0.0.1:8889",
            "https://": "http://127.0.0.1:8889"
        },
        creators=["柚木つばめ", "秋野かえで"]
    )
    import pprint
    pprint.pprint(rp.items)
