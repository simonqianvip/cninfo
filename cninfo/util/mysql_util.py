# -*-coding:utf-8_-*-

import MySQLdb
import logging

# Function: mysql util class
logger = logging.getLogger(__name__)
class SqlUtil():
    """
    mysql until
    """
    def __init__(self, ip_addr, user_name, passwd, db_name, port=3306):
        self.ip_addr = ip_addr
        self.user_name = user_name
        self.passwd = passwd
        self.db_name = db_name
        self.port = port

    # Function: connect to mysql server
    def connect(self):
        '''
        get connect
        :return:
        '''
        try:
            # use_unicode=True
            self.conn = MySQLdb.connect(host=self.ip_addr, user=self.user_name, passwd=self.passwd,
                                        port=self.port, charset='utf8' )
            self.conn.select_db(self.db_name)
        except MySQLdb.Error, e:
            logger.info("Mysql connect Error %s" % (e))

    # Function: disconnect to mysql server
    def disconnect(self):
        '''
        close connect
        :return:
        '''
        try:
            self.conn.close();
        except MySQLdb.Error, e:
            logger.info("Mysql disconnect Error %s" % (e))
        finally:
            logger.info('----------close mysql connecting----------')

    # Parameter: mysql query cmd string
    def get_data_from_db(self, sql_cmd_str):
        """
        Function: get data from mysql db(select)
        :param sql_cmd_str:
        :return:
        """
        try:
            cur = self.conn.cursor()
            cur.execute(sql_cmd_str)
            results = cur.fetchall()
            cur.close()
        except MySQLdb.Error, e:
            logger.info("Mysql get_data_from_db Error %s" % (e))
            return []
        return results

    # Parameter: mysql exec cmd string
    def exec_db_cmd(self, sql_cmd_str):
        """
        exec mysql cmd string(insert into,delete,create table,drop table...)
        :param sql_cmd_str:
        :return:
        """
        try:
            cur = self.conn.cursor()
            cur.execute(sql_cmd_str)
            self.conn.commit()
            cur.close()
        except MySQLdb.Error, e:
            logger.info("Mysql exec_db_cmd Error %s" % (e))


if __name__ == '__main__':
    sqlutil = SqlUtil('127.0.0.1', 'root', '123456', 'fm')
    sqlutil.connect()
    param = "'%"+u'亿'+"%'"
    query_sql = '''select company_name,money from fm where money like %s'''%param
    # print query_sql
    result = sqlutil.get_data_from_db(query_sql)
    for r in result:
        print r[0]+","+r[1]

    # print item
