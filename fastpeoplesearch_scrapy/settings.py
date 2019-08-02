# -*- coding: utf-8 -*-

# Scrapy settings for fastpeoplesearch_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'fastpeoplesearch_scrapy'

SPIDER_MODULES = ['fastpeoplesearch_scrapy.spiders']
NEWSPIDER_MODULE = 'fastpeoplesearch_scrapy.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'fastpeoplesearch_scrapy (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# CONCURRENT_REQUESTS = 100
CONCURRENT_REQUESTS_PER_DOMAIN = 5
CONCURRENT_REQUESTS_PER_IP = 5
# DOWNLOADER_MIDDLEWARES = {
#     'scrapy_crawlera.CrawleraMiddleware': 610
# }
#
# CRAWLERA_ENABLED = True
# CRAWLERA_APIKEY = '1abf1f4ff7864e10a664398ecfcc506a'

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
RETRY_ENABLED = False
DOWNLOAD_TIMEOUT = 100

HTTPCACHE_ENABLED = True
HTTPCACHE_IGNORE_HTTP_CODES = [302, 503, 403]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.DummyPolicy'
# HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.RFC2616Policy'
# COOKIES_ENABLED = True
# AUTOTHROTTLE_ENABLED = True
# DOWNLOAD_DELAY = 5.0
# AUTOTHROTTLE_TARGET_CONCURRENCY = 5

dont_filter = True
