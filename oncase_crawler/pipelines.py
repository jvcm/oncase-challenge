# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
from scrapy.exceptions import DropItem
from unicodedata import normalize
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://admin:admin123@articles-db.cxptre9ih5mz.us-east-2.rds.amazonaws.com:3306/articles', echo=False)

class TechTudoPipeline(object):
    def process_item(self, item, spider):
        
      def fix_string(txt):
         return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
   
      list_html = item['text']
      text_html = ' '.join(list_html)
      item['text'] = BeautifulSoup(text_html, "lxml").text

      if item['author']:
         if 'Por' in item['author']:
            item['author'] =  item['author'].split(',')[0].split('Por')[-1][1:]
      else:
         item['author'] = ''
      item['author'] = fix_string(item['author'])

      if not item['title']:
         item['title'] = ''
      item['title'] =  fix_string(item['title'])

      if not item['subtitle']:
         item['subtitle'] = ''
      item['subtitle'] =  fix_string(item['subtitle'])

      if not item['date']:
         item['date'] = ''
      item['date'] =  fix_string(item['date'])

      if not item['text']:
         item['text'] = ''
      item['text'] =  fix_string(item['text'])
      
      return item

        
    
class DuplicatesPipeline(object):  
   def __init__(self): 
      self.ids_seen = set() 

   def process_item(self, item, spider):
      if item['url'] in self.ids_seen: 
         raise DropItem("Repeated items found: %s" % item) 
      else: 
         self.ids_seen.add(item['url']) 
         return item

class MySQLWriterPipeline(object):  
   def process_item(self, item, spider):
      line = pd.DataFrame(
         {
            'author': [item['author']],
            'title': [item['title']],
            'subtitle': [item['subtitle']],
            'date': [item['date']],
            'text': [item['text']],
            'url': [item['url']]
         }
      )
      try:
         line.to_sql(name='test', con=engine, if_exists='append',index=False)
      except:
         print('failed to push data to db')
      pass


# class JsonWriterPipeline(object):

#     def open_spider(self, spider):
#         self.file = open('quotes.jl', 'w')

#     def close_spider(self, spider):
#         self.file.close()

#     def process_item(self, item, spider):
#         line = json.dumps(dict(item)) + "\n"
#         self.file.write(line)
#         return item

