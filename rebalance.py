#coding=utf-8
from models import UserHomeLayout
import hashlib
import MySQLdb
from consistent import MysqlHashClient
import settings
import logging
from multiprocessing import Pool


class Rebalance(object):
    """
    Rebalance add or remove db
    """

    def __init__(self, new_config, old_config, table_name):
        self.old_config = old_config
        self.new_config = new_config
        self.table_name = table_name
        self.new_client = MysqlHashClient(self.new_config)
        self.old_client = MysqlHashClient(self.old_config)
        self.init_old_host(self.old_config)


    def init_old_host(self, hosts_config):
        self.old_mysql_list = []
        self.i_old_mysql_list = []
        self.hosts = hosts_config.get("hosts")
        self.pool = Pool(len(self.hosts))
        i = 0
        for h in self.hosts:
            conn = MySQLdb.connect(**h)
            self.old_mysql_list.append(conn)
            self.i_old_mysql_list.append(i)
            i += 1

#    def run(self):
#        print  self.i_old_mysql_list
#        self.pool.map(self.do_run, self.i_old_mysql_list)


    def run(self):
        for host in self.old_mysql_list:
        #host = self.old_mysql_list[ihost]
            print host.get_host_info()
            limit = 100
            offset = 0

            while True:
                sql = "select ikey,value from %s limit %s offset %s" % (self.table_name, limit, offset)
                logging.debug(sql)
                cursor = host.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()

                if not rows:
                    cursor.close()
                    print "* " * 20
                    break

                move_count = 0
                for row in rows or []:
                    guid = row[0]
                    value = row[1]

                    nc = self.new_client.get_client(guid)
                    oc = self.old_client.get_client(guid)
                    #print nc.__dict__
                    if nc.get_host_info() == oc.get_host_info():
                        pass
                    else:
                        print "move form %s to %s" % (oc.get_host_info(), nc.get_host_info()), guid, value
                        #key in old and new not same
                        self.move(guid, value)
                        move_count += 1

                #next page
                offset += limit - move_count


    def move(self, key, value):
        self.old_client.delete(key, table_name=self.table_name)
        self.new_client.set(key, value, table_name=self.table_name)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    rb = Rebalance(settings.host_config, settings.old_host_config, settings.rebalance_db_table)
    rb.run()
#    nc = rb.new_client.get_client("bdbb8cb597f1299d252389ea69c0a436")
#    oc = rb.old_client.get_client("bdbb8cb597f1299d252389ea69c0a436")

    #print nc.get_host_info(),oc.get_host_info()