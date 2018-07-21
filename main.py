# coding=utf-8
# Created on 2018-07-20
# Author: Binbin Zhang

import os
import socket
import time
import logging
import argparse
import json
import tornado.ioloop
import tornado.web

import dbhelper

FLAGS = None

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world %s" % socket.gethostname())

class Application(tornado.web.Application):
    def __init__(self):
        logging.basicConfig(level = logging.DEBUG,
                            format = '%(levelname)s %(asctime)s (%(filename)s:%(funcName)s():%(lineno)d) %(message)s')
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
        }
        logging.info(settings)
        handlers = [
            (r'/', MainHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

        with open(FLAGS.config_file, "r") as fid:
            self.config = json.load(fid)
        self.db_config = self.config["db"]
        # Wait mysql to start service
        time.sleep(5)
        db = dbhelper.DbHelper(**self.db_config)
        if not db.table_exist():
            db.create_table()

    def start(self):
        logging.info('server start, port: %d...' % 8000)
        self.listen(8000)
        tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    usage = 'usage: python main.py config.json'
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('config_file', help='json config file')
    FLAGS = parser.parse_args()
    Application().start()

