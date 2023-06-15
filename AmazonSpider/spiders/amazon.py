import os
import time
from time import sleep
import pandas as pd
import scrapy
import numpy
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from func_timeout import func_set_timeout
import func_timeout
from amazoncaptcha import AmazonCaptcha
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions

# from AmazonSpider.items import AmazonspiderItem
from selenium.webdriver.support.wait import WebDriverWait
import random


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = []
    start_urls = ['https://www.amazon.com']
    page_url = "https://www.amazon.com/-/zh/dp/"
    asinArray = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wait = None
        self.options = ChromeOptions()
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,
            }
        }
        self.options.add_experimental_option('prefs', prefs)
        # options.add_argument("--headless")

    def parse(self, response, *args, **kwargs):
        print("start!!!")
        # 获取当前页面所有商品信息
        self.get_movie_url()

        column_name = ['电影id', '电影名称', '上映时间', '电影风格', '电影导演', '电影主演', '电影演员', '电影版本', '电影评分']
        result_df = pd.DataFrame([column_name])
        result_df.to_csv('data.csv', mode='a', header=False, index=False)

        for asin in self.asinArray:
            product_url = urljoin(self.page_url, str(asin))
            # product_url = urljoin(self.page_url, '6303636462')
            # print(product_url)
            try:
                yield scrapy.Request(product_url, callback=self.parse_detail)
            except Exception as e:
                print('[data error]', e)

    @func_set_timeout(5)  # 设定函数超执行时间_
    def parse_detail(self, response):

        # 存储的数据
        publish_date = ""
        movie_style = ''
        movie_director = ''
        movie_actor = ''
        movie_main_actor = ''
        product_format = ''
        movie_score = ""
        movie_asign = response.url.split('/')[-1]
        print("当前电影编号", movie_asign)

        # 检查是否遭遇验证码
        soup = BeautifulSoup(response.text, 'lxml')
        title = str(soup.select('title')[0].getText())
        print('当前页面：', title)

        # # 尝试处理验证码(目前尚未成功)
        # if title == "Amazon.com":
        #     driver = Chrome(options=self.options)
        #     driver.get(response.url)
        #     time.sleep(random.random())
        #     input_element = driver.find_element_by_id("captchacharacters")
        #
        #     # 获取验证码图片
        #     src = soup.find(
        #         class_="a-row a-text-center").findChild(name="img").attrs["src"]
        #     captcha = AmazonCaptcha.fromlink(src)
        #     solution = captcha.solve(keep_logs=True)
        #     print("验证码为：", solution)
        #
        #     print(driver.title)
        #
        #     input_element.send_keys(solution)
        #
        #     button = driver.find_element_by_xpath("//button")
        #     button.click()
        #
        #     print("已解决验证码√")
        #
        #     soup = BeautifulSoup(response.text, 'lxml')
        #     title = str(soup.select('title')[0].getText())
        #     print('新的title:', title)

        if title != "Amazon.com":
            # 用于检查页面类型
            checkPageType = str(response.xpath('//a[@class="av-retail-m-nav-text-logo"]/text()').extract_first())
            # print(checkPageType)

            try:
                # 爬取常规页面
                if checkPageType.find("Prime Video") == -1:
                    print("common page")
                    # 电影标题
                    movie_title = response.xpath('//div[@id="titleSection"]/h1/span/text()').extract_first()
                    # print('movie_title', movie_title)

                    # 商品格式
                    formatIndex = 1
                    formatXpathFront = '//div[@id="bylineInfo"]/span['
                    formatXpathEnd = ']/text()'
                    for i in range(8):
                        formatXpath = formatXpathFront + str(formatIndex) + formatXpathEnd
                        info = str(response.xpath(formatXpath).extract_first())
                        if info.find("格式") != -1:
                            formatIndex += 1
                            formatXpath = formatXpathFront + str(formatIndex) + formatXpathEnd
                            product_format = response.xpath(formatXpath).extract_first()
                            # print('product_format', product_format)
                            break
                        formatIndex += 1

                    # 电影风格
                    movie_style = response.xpath(
                        '//tr[@class="a-spacing-small po-genre"]/td[2]/span/text()').extract_first()
                    # print('movie_style', movie_style)

                    # 列表信息爬取
                    liIndex = 1
                    liXpathFront = '//div[@id="detailBullets_feature_div"]/ul/li['
                    liXpathEnd1 = ']/span/span[1]/text()'
                    liXpathEnd2 = ']/span/span[2]/text()'
                    while True:
                        liXpath1 = liXpathFront + str(liIndex) + liXpathEnd1
                        liXpath2 = liXpathFront + str(liIndex) + liXpathEnd2
                        info_type = str(response.xpath(liXpath1).extract_first())
                        if info_type == 'None':
                            break
                        info_type = info_type.split(' ')[0]
                        info_type = info_type[:-1]
                        print('info_type', info_type)

                        if info_type.find('发布日期') != -1:
                            publish_date = str(response.xpath(liXpath2).extract_first())
                            # print('publish_date', publish_date)
                        elif info_type.find('演员') != -1:
                            movie_main_actor = str(response.xpath(liXpath2).extract_first())
                            # print('movie_main_actor', movie_main_actor)
                        elif info_type.find('导演') != -1:
                            movie_director = str(response.xpath(liXpath2).extract_first())
                            # print('movie_director', movie_director)
                        liIndex += 1

                    # # 爬取商品描述
                    # movie_description = str(response.xpath('//div[@id="productDescription"]/p/span/text()').extract_first())
                    # # print('movie_description', movie_description)

                    # # 爬取电影时长
                    # movie_duration = response.xpath(
                    #     '//tr[@class="a-spacing-small po-runtime"]/td[2]/span/text()').extract_first()
                    # # print('movie_duration', movie_duration)

                    # 爬取电影评分
                    movie_score = response.xpath(
                        '//span[@id="acrPopover"]/span[@class="a-declarative"]/a/i[1]/span/text()').extract_first()
                    # print('movie_score', movie_score)

                # 爬取prime video
                else:
                    product_format = 'prime video'
                    print("进入prime video")
                    movie_title = response.xpath('//div[@class="_1m_axH"]/h1/text()').extract_first()
                    # movie_description = response.xpath('//div[@class="_3qsVvm _1wxob_"]/div/text()').extract_first()
                    # print('movie_title', movie_title)
                    # print('movie_description', movie_description)

                    # 电影简介信息表
                    primeMeta = {}
                    dts = response.xpath('//div[@id="meta-info"]//dl/dt')
                    for dt in dts:
                        key = ''.join(dt.xpath('.//text()').extract())
                        value = ''.join(dt.xpath('../dd//text()').extract())
                        primeMeta[key] = value

                    # 电影详情信息表
                    product_detail = response.xpath('//*[@id="btf-product-details"]/div//dl/dt')
                    for detail in product_detail:
                        key = ''.join(detail.xpath('.//text()').extract())
                        value = ''.join(detail.xpath('../dd//text()').extract())
                        primeMeta[key] = value

                    # 爬取导演
                    movie_director_group = []
                    if "导演" in primeMeta:
                        movie_director_group = primeMeta["导演"]
                    for i in movie_director_group:
                        movie_director = movie_director + str(i)
                    # print('movie_director', movie_director)

                    # 爬取主演
                    movie_main_actor_group = []
                    if "主演" in primeMeta:
                        movie_main_actor_group = primeMeta["主演"]
                    for i in movie_main_actor_group:
                        movie_main_actor = movie_main_actor + str(i)
                    # print('movie_main_actor', movie_main_actor)

                    # 爬取电影风格
                    movie_style_group = []
                    if "类型" in primeMeta:
                        movie_style_group = primeMeta["类型"]
                    for i in movie_style_group:
                        movie_style = movie_style + str(i)
                    # print('movie_style', movie_style)

                    # 爬取电影演员
                    movie_actor_group = []
                    if "配角" in primeMeta:
                        movie_actor_group = primeMeta["配角"]
                    for i in movie_actor_group:
                        movie_actor = movie_actor + str(i)
                    # print('movie_actor', movie_actor)

                    # # 爬取电影出版社
                    # movie_press_group = []
                    # if "工作室" in primeMeta:
                    #     movie_press_group = primeMeta["工作室"]
                    # for i in movie_press_group:
                    #     movie_press = movie_press + str(i)
                    # # print('movie_press', movie_press)

                    # 爬取发布时间
                    publish_date = response.xpath(
                        '//div[@class="_3QwtCH _16AW_S _2LF_6p dv-node-dp-badges _1Yhs0c HaWow5"]/span[@class="XqYSS8"]/span[@data-automation-id="release-year-badge"]/text()').extract_first()
                    # print('publish_date', publish_date)

                    # # 爬取电影时长
                    # movie_duration = str(
                    #     response.xpath(
                    #         '//div[@class="_3QwtCH _16AW_S _2LF_6p dv-node-dp-badges _1Yhs0c HaWow5"]/span[@class="XqYSS8"]/span[@data-automation-id="runtime-badge"]/text()').extract_first())
                    # # print('movie_duration', movie_duration)

                    # 爬取电影评分
                    movie_score = response.xpath('//div[@class="abwJ5F _16AW_S _2LF_6p"]/strong/text()').extract_first()
                    # print('movie_score', movie_score)

                # '电影id', '电影名称', '上映时间', '电影风格', '电影导演', '电影主演', '电影演员', '电影版本', '电影评分'
                movie_title = str(movie_title).strip()
                movie_score = str(movie_score).split(' ')[0]
                result_data = [movie_asign, movie_title, publish_date, movie_style, movie_director, movie_main_actor,
                               movie_actor, product_format, movie_score]
                print(result_data)

                result_df = pd.DataFrame([result_data])
                result_df.to_csv('data.csv', mode='a', header=False, index=False)
                print('结束\n')
            except Exception as e:
                print('[data error]', e)

    def get_movie_url(self):
        # 获取当前所有的商品号
        IDFilePath = "E://project//DataWarehouse//failed_id.csv"
        IDData = pd.read_csv(IDFilePath)
        asin = numpy.array(IDData.loc[:])
        self.asinArray = asin.ravel()
