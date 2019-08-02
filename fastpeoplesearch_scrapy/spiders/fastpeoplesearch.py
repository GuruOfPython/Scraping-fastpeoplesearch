# -*- coding: utf-8 -*-
import scrapy
import os
import csv
from scrapy.http import FormRequest
from nameparser import HumanName
import requests
from lxml import html
import random
import re

'''
https://www.fastpeoplesearch.com/address/1024-e-princeton-st--b_ontario-ca-91764
https://www.fastpeoplesearch.com/address/1364--1364-12-west-8th-st_san-bernardino-ca-92411
1364 & 1364 1/2 West 8Th St		San Bernardino	CA	92411

'''


class FastpeoplesearchSpider(scrapy.Spider):
    name = 'fastpeoplesearch'
    allowed_domains = ['www.fastpeoplesearch.com']
    start_urls = []

    # handle_httpstatus_list = [200]
    def __init__(self):
        self.save_directory = os.getcwd() + '/Result'

        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

        result_file_name = self.save_directory + '/190115 Tom Krol List for St Joe and Elkhart Counties.csv'
        self.already_data = []
        try:
            csv_reader = csv.reader(open(result_file_name, "r", encoding="utf-8"))
            for i, line in enumerate(csv_reader):
                self.already_data.append(line[:12])
        except:
            self.already_data = []
        self.create_result_file(result_file_name=result_file_name)

        self.input_data = csv.reader(open("190115 Tom Krol List for St Joe and Elkhart Counties - All with no numbers.csv", "r", encoding="utf-8"))

        self.total_data = []
        self.links = []
        self.total_cnt = 0

        self.start_url = "https://www.fastpeoplesearch.com/"

    def start_requests(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            # 'Referer': 'https://www.fastpeoplesearch.com'
        }
        for i, line in enumerate(self.input_data):
            print(line)
            if i == 0:
                self.insert_row(result_row=line + ["Phone 1", "Phone 2", "Phone 3", "Email"])
                continue

            # print(i, line)
            if line in self.already_data:
                print("[Already] {}".format(i))
                continue
            address = line[4]
            city = line[5]
            state = line[6]
            zip_code = line[7]

            url = make_url(address=address, city=city, state=state, zip_code=zip_code)
            url = url + "/page/{}"
            page = 1
            pxy = random.choice(PROXIES)
            # print(pxy)
            request = FormRequest(
                url=url.format(page),
                headers=headers,
                method="GET",
                callback=self.get_first_links,
                errback=self.fail_first_links,
                dont_filter=True,
                meta={
                    "line": line,
                    "url": url,
                    "page": page,
                    'proxy': pxy,
                    'handle_httpstatus_all': True,
                    'dont_redirect': True,
                }
            )
            yield request

    def get_first_links(self, response):
        line = response.meta["line"]
        url = response.meta["url"]
        page = response.meta["page"]
        address = line[4]
        city = line[5]
        state = line[6]
        zip_code = line[7]
        first_name = line[0]
        last_name = line[1]

        if response.status == 404:
            new_line = line
            self.total_cnt += 1
            self.insert_row(result_row=new_line)
            print("[Details {}] {}".format(self.total_cnt, [address, url]))

        elif response.status in [403, 302, 503]:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                # 'Referer': 'https://www.fastpeoplesearch.com'
            }
            pxy = random.choice(PROXIES)
            # print(pxy)
            request = FormRequest(
                url=url.format(page),
                headers=headers,
                method="GET",
                callback=self.get_first_links,
                errback=self.fail_first_links,
                dont_filter=True,
                meta={
                    "line": line,
                    "url": url,
                    "page": page,
                    'proxy': pxy,
                    'handle_httpstatus_all': True,
                    'dont_redirect': True,
                }
            )
            yield request
        else:
            links = []
            rows = response.xpath('//div[@class="card-block"]')
            if rows:
                for row in rows:
                    try:
                        full_name = row.xpath('.//*[@class="card-title"]/text()').extract_first()
                    except:
                        full_name = row.xpath('.//*[@class="card-title"]/text()').extract_first()
                    try:
                        link = response.urljoin(row.xpath('.//a[text()="View Free Details"]/@href').extract_first())
                    except:
                        link = ""
                    name = HumanName(full_name)
                    first_name_v = name.first
                    last_name_v = name.last
                    if first_name_v.lower() == first_name.lower() and last_name_v.lower() == last_name.lower():
                        links.append(link)
            try:
                next_btn = response.xpath('//link[@rel="next"]/@href').extract_first()
            except:
                next_btn = ""

            if not links and next_btn:
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                    # 'Referer': url.format(page)
                }
                page += 1
                pxy = random.choice(PROXIES)
                # print(pxy)
                request = FormRequest(
                    url=url.format(page),
                    headers=headers,
                    method="GET",
                    callback=self.get_first_links,
                    errback=self.fail_first_links,
                    dont_filter=True,
                    meta={
                        "line": line,
                        "url": url,
                        "page": page,
                        'proxy': pxy,
                        'handle_httpstatus_all': True,
                        'dont_redirect': True,
                    }
                )
                yield request

            if not links and not next_btn:
                self.total_cnt += 1
                self.insert_row(result_row=line)
                print("[Details {}] {}".format(self.total_cnt, [address, url]))

            if links:
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                    # 'Referer': url.format(page)
                }
                pxy = random.choice(PROXIES)
                # print(pxy)
                request = FormRequest(
                    url=links[0],
                    headers=headers,
                    method="GET",
                    callback=self.get_phones,
                    errback=self.fail_phones,
                    dont_filter=True,
                    meta={
                        "line": line,
                        'proxy': pxy,
                        'links': links,
                        'handle_httpstatus_all': True,
                        'dont_redirect': True,
                    }
                )

                yield request

    def fail_first_links(self, failure):
        pass

        line = failure.request.meta["line"]
        url = failure.request.meta["url"]
        page = failure.request.meta["page"]

        # print("[Failure] {}".format(url.format(page)))

        pxy = random.choice(PROXIES)
        # print(pxy)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            # 'Referer': 'https://www.fastpeoplesearch.com'
        }
        request = FormRequest(
            url=url.format(page),
            headers=headers,
            method="GET",
            callback=self.get_first_links,
            errback=self.fail_first_links,
            dont_filter=True,
            meta={
                "line": line,
                "url": url,
                "page": page,
                'proxy': pxy,
                'handle_httpstatus_all': True,
                'dont_redirect': True,
            }
        )
        yield request

    def get_phones(self, response):
        line = response.meta["line"]
        links = response.meta["links"]
        address = line[4]
        city = line[5]
        state = line[6]
        zip_code = line[7]
        first_name = line[0]
        last_name = line[1]

    def fail_phones(self, failure):
        line = failure.request.meta['line']
        links = failure.request.meta['links']
        print("[Failure] {}".format(links))

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            # 'Referer': 'https://www.fastpeoplesearch.com'
        }
        pxy = random.choice(PROXIES)
        # print(pxy)
        request = FormRequest(
            url=links[0],
            headers=headers,
            method="GET",
            callback=self.get_phones,
            errback=self.fail_phones,
            dont_filter=True,
            meta={
                "line": line,
                'proxy': pxy,
                'links': links,
                'handle_httpstatus_all': True,
                'dont_redirect': True,
            }
        )

        yield request

