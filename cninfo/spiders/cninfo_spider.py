# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import scrapy.cmdline
from scrapy.http.response import Response
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import logging
import random
import re
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from autopy import alert
from autopy import mouse
from autopy import key
import autopy

from PIL import Image
import pytesseract

import urllib
from io import BytesIO

import uuid

from cninfo.items import *

logger = logging.getLogger(__name__)
class CninfoSpider(scrapy.Spider):
    # 下载文件路径
    file_dir = "d:\\cninfo_download"
    # 火狐浏览器驱动地址
    firefox_driver_path = "D:\Program Files\Mozilla Firefox\geckodriver-v0.10.0-win64\geckodriver.exe"

    list = ['company_name','e_company_name','register_add','summary','legal','Secretaries',
            'register_money','company_type','zip_code','tel','fax','URL','market_time','shares_time',
            'publish_number','publish_price','publish_ratio','public_mode','underwriting','referee','recommend']

    uuid1 = uuid.uuid1()

    def __init__(self):
        # 实例化一个火狐配置对象
        pf = webdriver.FirefoxProfile()
        # 设置成0代表下载到浏览器默认下载路径；设置成2则可以保存到指定目录
        pf.set_preference("browser.download.folderList", 2)
        # 设置下载路径
        pf.set_preference("browser.download.dir",self.file_dir)
        # 不询问下载路径；后面的参数为要下载页面的Content-type的值
        # 禁用pdf
        pf.set_preference('pdfjs.disabled',True)
        pf.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')
        # pf.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
        pf.set_preference("prefs.converted-to-utf8",True)
        self.driver = webdriver.Firefox(firefox_profile=pf,executable_path=self.firefox_driver_path)
        logger.info('---------- init firefox ----------')

        # options = webdriver.ChromeOptions()
        # prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': File_DIR}
        # options.add_experimental_option('prefs', prefs)
        # options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        # self.driver = webdriver.Chrome(chrome_options=options,executable_path='D:\program\chromedriver_win32\chromedriver.exe')

    name = "cninfo_spider"
    allowed_domains = ["www.cninfo.com.cn"]
    start_urls = (
        'http://www.cninfo.com.cn',
    )

    def parse(self, response):
        self.driver.get(response.url)
        self.driver.implicitly_wait(30)
        try:
            # 搜索公司
            self.driver.find_element_by_xpath('//*[@id="common_top_input_obj"]').clear()
            self.driver.find_element_by_xpath('//*[@id="common_top_input_obj"]').send_keys(u'濮耐股份')
            self.driver.find_element_by_xpath('/html/body/div[1]/div/div[4]/div/a/img').click()
            time.sleep(10)
            # ----------------
            # # 公告全文
            self.driver.switch_to_frame('i_nr')
            # TODO 获取公告主窗口
            public_main_window = self.driver.current_window_handle

            flag = True
            page_num = 1
            items = []
            while(flag):
                time.sleep(random.randint(60,90))
                logger.info('---------- sleep time ,next page---------- ')
                # TODO 防止页面没有加载完成，出现异常，待测试
                self.driver.implicitly_wait(30)
                flag,items = self.get_info(flag, page_num,items,public_main_window)

            # TODO 切换到主页
            self.driver.switch_to_window(public_main_window)
            # ------------------------
            # 公司概况
            self.driver.find_element_by_xpath('//*[@id="brief"]/a').click()
            self.driver.switch_to_frame('i_nr')
            # 切换到不同的frame,都得等待元素的加载，防止No Elements not find
            self.driver.implicitly_wait(30)
            item = CninfoCompanyItem()
            trs = self.driver.find_elements_by_xpath('/html/body/div[2]/div[1]/div[2]/table/tbody/tr')
            if trs:
                for i in range(1,len(trs)+1):
                    td_name = self.driver.find_element_by_xpath(
                        '/html/body/div[2]/div[1]/div[2]/table/tbody/tr[%d]/td[1]' % i)
                    td_value = self.driver.find_element_by_xpath(
                            '/html/body/div[2]/div[1]/div[2]/table/tbody/tr[%d]/td[2]'%i)
                    # print('name = %s,value = %s'%(td_name.text,td_value.text))
                    item[self.list[i-1]] = td_value.text
                #   添加外键
                item['f_key'] = self.uuid1
                print item
            items.append(item)
        except Exception,e:
            logger.info(e)
        finally:
            self.driver.close()
            return items

    def get_info(self, flag, page_num,items,public_main_window):
        """
        1,获取公司概况
        2,获取公告信息
        3,下载公告信息
        :param flag:
        :param page_num:
        :return:
        """
        lis = self.driver.find_elements_by_xpath('//*[@id="ul_a_latest"]/li')
        # 最外层列表
        if lis:
            print('---------当前第%d页---------' % page_num)
            date = ''
            for i in range(1, len(lis) + 1):

                # 判断是否有按钮
                toggle_miuns = self.driver.find_elements_by_xpath('//*[@id="ul_a_latest"]/li[%d]/div[1]' % i)
                if toggle_miuns:
                    for tm in toggle_miuns:
                        tm_text = tm.get_attribute('class')
                        print tm_text
                        # 展开隐藏的公告
                        if tm_text == 't0':
                            tm.click()

                # 公告日期
                divs = self.driver.find_elements_by_xpath('//*[@id="ul_a_latest"]/li[%d]/div' % i)
                div_num = 1
                date = None
                if divs:
                    for div in divs:
                        class_text = div.get_attribute('class')

                        title = None
                        type = None
                        link = None
                        filename = None
                        if class_text == 'g1':
                            date = div.text
                        elif class_text == 'g3':
                            dds = self.driver.find_elements_by_xpath(
                                    '//*[@id="ul_a_latest"]/li[%d]/div[%d]/dd' % (i, div_num))
                            if dds:
                                # 公告列表（内层）
                                for j in range(1, len(dds) + 1):
                                    print 'dds length = %d'%len(dds)
                                    item = CninfoItem()
                                    # TODO 查看接口为J的值，是否与dds的长度相等，第二页第一条出现错误
                                    # 公告标题 {"method":"xpath","selector":"//*[@id=\"ul_a_latest\"]/li[1]/div[2]/dd[2]/span[1]/a"}
                                    a_tag = self.driver.find_element_by_xpath(
                                            '//*[@id="ul_a_latest"]/li[%d]/div[%d]/dd[%d]/span[1]/a' % (i, div_num, j))
                                    # TODO 进入公告详情页
                                    title = a_tag.text
                                    # -----------------
                                    # a_tag.click()
                                    # # TODO 关闭下载页
                                    # handles = self.driver.window_handles
                                    # for h in handles:
                                    #     if h != public_main_window:
                                    #         self.driver.switch_to_window(h)
                                    #         self.driver.close()
                                    # #   切换到当前frame
                                    # self.driver.switch_to_window(public_main_window)
                                    # self.driver.switch_to_frame('i_nr')
                                    # --------------------

                                    # 获取link
                                    link = a_tag.get_attribute('href')
                                    # 获取fileName
                                    if link:
                                        splits = link.split('?')
                                        if splits[0]:
                                            split2 = splits[0].split('/')
                                            filename = split2[len(split2) - 1]
                                    # 公告类型
                                    span = self.driver.find_element_by_xpath(
                                            '//*[@id="ul_a_latest"]/li[%d]/div[%d]/dd[%d]/span[2]' % (i, div_num, j))
                                    type = span.text
                                    # 公告时间
                                    # self.driver.find_element_by_xpath('')
                                    print 'date=%s,title = %s,type = %s,link = %s,filename = %s' % (date, title, type, link,filename)
                                    item['uuid'] =self.uuid1
                                    item['date'] = date
                                    item['title'] = title
                                    item['type'] = type
                                    item['link'] = link
                                    item['filename'] = filename
                                    # logger.info(item)
                                    print item
                                    items.append(item)
                                    time.sleep(random.randint(2,6))
                                    logger.info('---------- sleep time ,wait download next data---------- ')

                        div_num = div_num + 1

            flag = self.next_page(flag, page_num)

        return flag,items

    def next_page(self, flag, page_num):
        """
        点击下一页
        :param flag:
        :param page_num:
        :return:
        """
        pagination_as = self.driver.find_elements_by_xpath('//*[@id="Pagination"]/a')
        if pagination_as:
            for i in range(1, len(pagination_as) + 1):
                a = self.driver.find_element_by_xpath('//*[@id="Pagination"]/a[%d]' % i)
                if a.text == u'后一页':
                    page_num = page_num + 1
                    flag = True
                    a.click()
                else:
                    flag = False
        return flag


if __name__ == '__main__':
    scrapy.cmdline.execute(argv=['scrapy','crawl','cninfo_spider'])
