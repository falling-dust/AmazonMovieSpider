# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random
from local_fake_useragent import UserAgent

class MyUserAgentMiddleware(UserAgentMiddleware):
    '''
    设置User-Agent
    '''

    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            # 采用了随机请求头库，此处其实已作废
            user_agent=crawler.settings.get('USER_AGENTS_LIST')
        )

    def process_request(self, request, spider):
        # agent = random.choice(self.user_agent)
        ua = UserAgent()
        agent = ua.rget
        # print(agent)
        request.headers['User-Agent'] = agent
