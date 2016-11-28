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
from cninfo.util.mysql_util import SqlUtil

logger = logging.getLogger(__name__)
class CninfoSpider(scrapy.Spider):
    # 下载文件路径
    file_dir = "d:\\cninfo_download"
    # 火狐浏览器驱动地址
    firefox_driver_path = "D:\Program Files\Mozilla Firefox\geckodriver-v0.10.0-win64\geckodriver.exe"
    uuid1 = uuid.uuid1()
    search_key = u'濮耐股份'
    download_count = 0

    list = ['company_name','e_company_name','register_add','summary','legal','Secretaries',
            'register_money','company_type','zip_code','tel','fax','URL','market_time','shares_time',
            'publish_number','publish_price','publish_ratio','public_mode','underwriting','referee','recommend']

    def __init__(self):
        # 连接mysql数据库，并查询论文名称
        self.init_mysql()
        logger.info('init mysql database')

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
    def init_mysql(self):
        '''
        初始化连接mysql数据库
        :return: 连接对象
        '''
        self.mysql_util = SqlUtil('127.0.0.1', 'root', '123456', 'fm')
        self.mysql_util.connect()

    def GetNowTime(self):
        '''
        获取当前系统时间
        :return:
        '''
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def parse(self, response):
        s_time = self.GetNowTime()
        self.driver.get(response.url)
        self.driver.implicitly_wait(30)
        try:
            # 搜索公司
            self.driver.find_element_by_xpath('//*[@id="common_top_input_obj"]').clear()
            self.driver.find_element_by_xpath('//*[@id="common_top_input_obj"]').send_keys(self.search_key)
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
            # 公司存在就不更新，否则会影响uuid的值，无法匹配公司公告
            query_sql3 = """select * from cninfo_company where summary = '%s'""" %self.search_key
            resluts = self.mysql_util.get_data_from_db(query_sql3)
            if resluts:
                logger.info('----------company is Exsit----------')
            else:
                items = self.get_company_base(items)


            # TODO 爬虫数据更新
            e_time = self.GetNowTime()
            u_count = len(items)
            # 插入更新语句
            insert_sql = """
                    insert into spider_info(site,s_time,e_time,update_count,download_count)
                    values('巨潮资讯网','%s','%s','%s','%s')"""%(s_time,e_time,u_count,self.download_count)
            results = self.mysql_util.exec_db_cmd(insert_sql)
            if results:
                logger.info('----------Update spider data is success----------')
            else:
                logger.info('----------No spider data is success----------')

        except Exception,e:
            logger.info(e)
        finally:
            # 关闭数据库连接
            self.mysql_util.disconnect()
            self.driver.close()
            return items

    def get_company_base(self, items):
        """
        公司概况
        :param items:
        :return:
        """
        self.driver.find_element_by_xpath('//*[@id="brief"]/a').click()
        self.driver.switch_to_frame('i_nr')
        # 切换到不同的frame,都得等待元素的加载，防止No Elements not find
        self.driver.implicitly_wait(30)
        item = CninfoCompanyItem()
        trs = self.driver.find_elements_by_xpath('/html/body/div[2]/div[1]/div[2]/table/tbody/tr')
        if trs:
            for i in range(1, len(trs) + 1):
                td_name = self.driver.find_element_by_xpath(
                        '/html/body/div[2]/div[1]/div[2]/table/tbody/tr[%d]/td[1]' % i)
                td_value = self.driver.find_element_by_xpath(
                        '/html/body/div[2]/div[1]/div[2]/table/tbody/tr[%d]/td[2]' % i)
                # print('name = %s,value = %s'%(td_name.text,td_value.text))
                item[self.list[i - 1]] = td_value.text
            # 添加外键
            item['f_key'] = self.uuid1
            print item
        items.append(item)
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
                                    # TODO 查看接口为J的值，是否与dds的长度相等，第二页第一条出现错误
                                    # 公告标题
                                    a_tag = self.driver.find_element_by_xpath(
                                            '//*[@id="ul_a_latest"]/li[%d]/div[%d]/dd[%d]/span[1]/a' % (i, div_num, j))
                                    # 获取link
                                    link = a_tag.get_attribute('href')
                                    title = a_tag.text

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

                                    print 'date=%s,title = %s,type = %s,link = %s,filename = %s' % (date, title, type, link,filename)

                                    # TODO 增量更新公告信息
                                    query_sql = """select * from cninfo where link = '%s'""" %link
                                    results = self.mysql_util.get_data_from_db(query_sql)

                                    # 根据公司名称获取对应的uuid
                                    query_forekey = """select f_key from cninfo_company where summary = '%s'""" %self.search_key
                                    forekey = self.mysql_util.get_data_from_db(query_forekey)

                                    if results:
                                        logger.info('----------Data is Exsit----------')
                                    else:
                                        # 下载数据
                                        self.download_data(a_tag, public_main_window)
                                        item = CninfoItem()
                                        if forekey:
                                            item['uuid'] = forekey
                                        else:
                                            item['uuid'] = self.uuid1

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

            flag,page_num = self.next_page(flag, page_num)

        return flag,items

    def download_data(self, a_tag, public_main_window):
        """
        下载数据
        :param a_tag:
        :param public_main_window:
        :return:
        """
        a_tag.click()

        time.sleep(random.randint(5,10))
        logger.info('----------random sleep,wait download complete----------')
        # 下载条数更新
        self.download_count = self.download_count + 1
        # TODO 关闭下载页
        handles = self.driver.window_handles
        for h in handles:
            if h != public_main_window:
                self.driver.switch_to_window(h)
                self.driver.close()
        # 切换到当前frame
        self.driver.switch_to_window(public_main_window)
        self.driver.switch_to_frame('i_nr')

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
        return flag,page_num


if __name__ == '__main__':
    scrapy.cmdline.execute(argv=['scrapy','crawl','cninfo_spider'])
