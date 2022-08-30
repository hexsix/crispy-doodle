"""
author: hexsix
date: 2022/08/18
description: request telegram api
"""

import logging
from typing import Dict

import telegram


logger = logging.getLogger('telegram_api')


class Bot(object):

    def __init__(self, token: str, chat_id: str, use_proxies: bool, proxies: Dict):
        self.chat_id = chat_id
        if use_proxies:
            pp = telegram.utils.request.Request(
                proxy_url=proxies['https://'])
            self._b = telegram.Bot(token=token, request=pp)
        else:
            self._b = telegram.Bot(token=token)

    def construct_caption(self, item: Dict) -> str:
        def escape(text: str) -> str:
            escape_chars = [
                '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for escape_char in escape_chars:
                text = text.replace(escape_char, '\\' + escape_char)
            return text
        caption = f'*{escape(item["title"])}*\n' \
            f'{escape(item["published"])}\n' \
            f'\n' \
            f'{escape(item["link"])}'
        return caption

    def send(self, item: Dict) -> bool:
        logger.info(f'send album: {item["title"]}')
        try:
            self._b.send_photo(chat_id=self.chat_id,
                               photo=item['cover'],
                               caption=self.construct_caption(item),
                               parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2)
        except:
            logger.error(f'send {item["title"]} error')
            return False
        return True


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    from rssparser import rssparser
    rp = rssparser(
        rss_url='https://rsshub.app/ncm/artist/12390232',
        use_proxies=True,
        proxies={
            "http://": "http://127.0.0.1:8889",
            "https://": "http://127.0.0.1:8889"
        }
    )
    bot = Bot(
        token='0123456789:9876543210',
        chat_id='-100123456789',
        use_proxies=True,
        proxies={
            "http://": "http://127.0.0.1:8889",
            "https://": "http://127.0.0.1:8889"
        }
    )
    for item in rp.items:
        bot.send(item)
