# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb.cursors
from twisted.enterprise import adbapi
import logging
from cninfo.items import *


class CninfoPipeline(object):
    def process_item(self, item, spider):
        return item


logger = logging.getLogger(__name__)
class MySQLStoreCninfoPipeline(object):
    """
    数据存储到mysql
    """
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        '''
        从settings文件加载属性
        :param settings:
        :return:
        '''
        dbargs = dict(
                host=settings['MYSQL_HOST'],
                db=settings['MYSQL_DBNAME'],
                user=settings['MYSQL_USER'],
                passwd=settings['MYSQL_PASSWD'],
                charset='utf8',
                cursorclass=MySQLdb.cursors.DictCursor,
                use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):
        if isinstance(item, CninfoItem):
            deferred = self.dbpool.runInteraction(self._do_insert, item, spider)
        elif isinstance(item, CninfoCompanyItem):
            deferred = self.dbpool.runInteraction(self._do_insert_company_info, item, spider)

        deferred.addErrback(self._handle_error)
        # d.addBoth(lambda _: item)
        return deferred

    # 将每行更新或写入数据库中
    def _do_insert(self, conn, item, spider):
        """
        # 公告信息
        uuid = scrapy.Field()
        date = scrapy.Field()
        title = scrapy.Field()
        type = scrapy.Field()
        link = scrapy.Field()
        filename = scrapy.Field()
        """
        conn.execute("""
                    insert into cninfo(u_id,cn_date, title,cn_type,link,filename)
                    values(%s,%s, %s, %s, %s,%s)
            """, (item['uuid'], item['date'], item['title'], item['type'], item['link'], item['filename']))

    def _do_insert_company_info(self, conn, item, spider):
        """
       # 公司概况
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
       """
        conn.execute("""
                        insert into cninfo_company(company_name, e_company_name,register_add,summary,legal,Secretaries,
                        register_money,company_type,zip_code,
                        tel,fax,URL,market_time,shares_time,publish_number,publish_price,publish_ratio,public_mode,
                        underwriting,referee,recommend,f_key)
                        values(%s, %s, %s, %s,%s,%s, %s, %s, %s,%s,%s, %s, %s, %s,%s,%s, %s, %s, %s,%s,%s,%s)
                """, (
        item['company_name'], item['e_company_name'], item['register_add'], item['summary'], item['legal'],
        item['Secretaries'], item['register_money'],
        item['company_type'], item['zip_code'], item['tel'], item['fax'], item['URL'], item['market_time'],
        item['shares_time'], item['publish_number'],
        item['publish_price'], item['publish_ratio'], item['public_mode'], item['underwriting'],
        item['referee'], item['recommend'], item['f_key']))

    def _handle_error(self, failue):
        logger.error(failue)
