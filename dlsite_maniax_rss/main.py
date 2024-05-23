"""
filename: main.py
author: hexsix <hexsixology@gmail.com>
date: 2022/05/26
description: 
"""

import json
import getopt
import logging
import os
import sys

from rssparser import rssparser
from telegram_api import Bot


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('main')


def arg_parse(argv):
    rss_url = 'https://rss.owo.nz/dlsite/new/maniax'
    token = ''
    chat_id = ''
    use_proxies = False
    proxies = {}
    creators = []
    if os.path.exists('dlsite_maniax_rss/configs.json'):
        configs = json.load(open('dlsite_maniax_rss/configs.json', 'r', encoding='utf8'))
        use_proxies = configs['use_proxies']
        proxies = configs['proxies']
    if os.path.exists('dlsite_maniax_rss/creators.json'):
        creators = json.load(open('dlsite_maniax_rss/creators.json', 'r', encoding='utf8'))
    try:
        opts, args = getopt.getopt(argv, 't:c:', ['token=', 'chat_id='])
        for opt, arg in opts:
            if opt in ['-t', '--token']:
                token = arg
            elif opt in ['-c', '--chat_id']:
                chat_id = arg
    except:
        logger.error('parse argv error')
    logger.info(f"rss url: {rss_url}\n" \
                f"creators: {creators}\n" \
                f"telegram chat id: {chat_id}\n" \
                f"telegram token: ******\n" \
                f"use proxies: {use_proxies}\n" \
                f"proxies: {json.dumps(proxies)}")
    return rss_url, token, chat_id, use_proxies, proxies, creators


def main(argv) -> None:
    logger.info('============ App Start ============')
    rss_url, token, chat_id, use_proxies, proxies, creators = arg_parse(argv)
    rp = rssparser(
        rss_url=rss_url,
        use_proxies=use_proxies,
        proxies=proxies,
        creators=creators
    )
    bot = Bot(
        token=token,
        chat_id=chat_id,
        use_proxies=use_proxies,
        proxies=proxies
    )
    for item in rp.items:
        bot.send(item)
    logger.info('============ App End ============')


if __name__ == '__main__':
    main(sys.argv[1:])
