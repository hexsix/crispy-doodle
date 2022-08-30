"""
filename: main.py
author: hexsix <hexsixology@gmail.com>
date: 2022/07/18
description: 
"""

import imp
import json
import getopt
import logging
import os
import time
import sys
from typing import Any, Dict, List

from rssparser import rssparser
from telegram_api import Bot


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()


def arg_parse(argv):
    token = ''
    chat_id = ''
    use_proxies = False
    proxies = {}
    artists = {}
    if os.path.exists('ncm_artists_rss/configs.json'):
        configs = json.load(open('ncm_artists_rss/configs.json', 'r', encoding='utf8'))
        use_proxies = configs['use_proxies']
        proxies = configs['proxies']
    if os.path.exists('ncm_artists_rss/artists.json'):
        artists = json.load(open('ncm_artists_rss/artists.json', 'r', encoding='utf8'))
    try:
        opts, args = getopt.getopt(argv, 't:c:', ['token=', 'chat_id='])
        for opt, arg in opts:
            if opt in ['-t', '--token']:
                token = arg
            elif opt in ['-c', '--chat_id']:
                chat_id = arg
    except:
        logger.error('parse argv error')
    logger.info(f"artists: {json.dumps(artists)}\n" \
                f"telegram chat id: {chat_id}\n" \
                f"telegram token: ******\n" \
                f"use proxies: {use_proxies}\n" \
                f"proxies: {json.dumps(proxies)}")
    return token, chat_id, use_proxies, proxies, artists


def rss_url_generator(artists: Dict[str, str]) -> Any:
    for key in artists:
        artist_name, artist_id = key, artists[key]
        rss_url = f'https://rsshub.app/ncm/artist/{artist_id}'
        yield artist_name, rss_url


def main(argv) -> None:
    logger.info('============ App Start ============')
    token, chat_id, use_proxies, proxies, artists = arg_parse(argv)
    bot = Bot(
        token=token,
        chat_id=chat_id,
        use_proxies=use_proxies,
        proxies=proxies
    )
    for artist_name, rss_url in rss_url_generator(artists):
        logger.info(f'{artist_name}：{rss_url}')
        rp = rssparser(
            rss_url=rss_url,
            use_proxies=use_proxies,
            proxies=proxies
        )
        for item in rp.items:
            bot.send(item)
    logger.info('============ App End ============')


if __name__ == '__main__':
    main(sys.argv[1:])
