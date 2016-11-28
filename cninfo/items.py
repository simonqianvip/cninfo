# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CninfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 公告信息
    uuid = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    type = scrapy.Field()
    link = scrapy.Field()
    filename = scrapy.Field()

class CninfoCompanyItem(scrapy.Item):
    """
    公司概况
    """
    # 公司全称
    company_name = scrapy.Field()
    # 英文名称
    e_company_name = scrapy.Field()
    # 注册地址
    register_add = scrapy.Field()
    # 公司简称
    summary = scrapy.Field()
    # 法人
    legal = scrapy.Field()
    # 董秘
    Secretaries = scrapy.Field()
    # 注册资本(万元)
    register_money = scrapy.Field()
    # 行业种类
    company_type = scrapy.Field()
    # 邮政编码
    zip_code = scrapy.Field()
    # 公司电话
    tel = scrapy.Field()
    # 公司传真
    fax = scrapy.Field()
    # 公司网址
    URL = scrapy.Field()
    # 上市时间
    market_time = scrapy.Field()
    # 招股时间
    shares_time = scrapy.Field()
    # 发行数量（万股）
    publish_number = scrapy.Field()
    # 发行价格（元）
    publish_price = scrapy.Field()
    # 发行市盈率
    publish_ratio = scrapy.Field()
    # 发行方式
    public_mode = scrapy.Field()
    # 主承销商
    underwriting = scrapy.Field()
    # 上市推荐人
    referee = scrapy.Field()
    # 保荐机构
    recommend = scrapy.Field()
    # 外键
    f_key = scrapy.Field()
    pass
