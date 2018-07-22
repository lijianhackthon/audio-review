# coding=utf-8
# Created on 2018-07-20
# Author: Binbin Zhang

import os
import socket
import glob
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

class UpdateHandler(tornado.web.RequestHandler):
    def get(self):
        id = int(self.get_argument('id', 0, strip=True));
        operation = self.get_argument('operation', 'true', strip=True);
        db = dbhelper.DbHelper(**self.application.db_config)
        db.update(id, operation, 'true')

class AdminHandler(tornado.web.RequestHandler):
    def get(self):
        page = int(self.get_argument('page', 0, strip=True))
        page_items = int(self.get_argument('page_items', 10, strip=True))
        db = dbhelper.DbHelper(**self.application.db_config)
        review_count = db.get_review_count()
        num_pages = int((review_count - 1) / page_items) + 1;
        if page < 0: page = 0
        if page >= num_pages: page = num_pages - 1
        start_page = page - 5
        if start_page < 0: start_page = 0
        end_page = page + 5
        if end_page > num_pages: end_page = num_pages - 1

        items = db.get_all_review(page * page_items, page_items)
        self.render("static/admin.html", items = items,
                                         page_items = page_items,
                                         page = page,
                                         num_pages = num_pages,
                                         start_page = start_page,
                                         end_page = end_page)

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
            (r'/admin', AdminHandler),
            (r'/update', UpdateHandler),
            (r'/static/', tornado.web.StaticFileHandler, dict(path=settings['static_path']))
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

        with open(FLAGS.config_file, "r") as fid:
            self.config = json.load(fid)
        self.db_config = self.config["db"]
        # wait mysql to start service
        logging.info('waiting mysql be full ready, 20s')
        time.sleep(20)
        db = dbhelper.DbHelper(**self.db_config)
        if not db.table_exist():
            db.create_table()
            # update index
            all_wav_files = glob.glob(r'wav/*/*.wav')
            for i, wav in enumerate(all_wav_files):
                db.insert(wav, 'false', 'false')
                if i % 50 == 0:
                    logging.info('creating index %d', i)

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

