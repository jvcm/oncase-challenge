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
import datetime
import os

# Engine responsavel por estabelecer a conexao com o banco de dados
USER_PASSWORD_IP_DB = os.environ['MYSQL_DB_ONCASE']
ENGINE = create_engine(USER_PASSWORD_IP_DB, echo=False)
MAX_COUNT = 12

# Pipeline responsavel por processar os dados: remover caracteres indesejados, espacos
# no comeco e fim das strings e substituir o item por uma string vazia, caso
# o campo do item venha no formato NoneType
class TechTudoPipeline(object):

   def process_item(self, item, spider):
        
      def fix_string(txt):
         return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
   
      list_html = item['text']
      text_html = ' '.join(list_html)
      item['text'] = BeautifulSoup(text_html, "lxml").text

      if item['author']:
         if 'Por' in item['author']:
            item['author'] =  item['author'].split(',')[0].split('Por')[-1][1:].strip()
      else:
         item['author'] = ''
      item['author'] = fix_string(item['author']).strip()

      if not item['title']:
         item['title'] = ''
      item['title'] =  fix_string(item['title']).strip()

      if not item['subtitle']:
         item['subtitle'] = ''
      item['subtitle'] =  fix_string(item['subtitle']).strip()

      if not item['date']:
         item['date'] = ''
      item['date'] =  fix_string(item['date']).strip()

      if not item['text']:
         item['text'] = ''
      item['text'] =  fix_string(item['text']).strip()
      
      return item


# Pipeline responsavel por descartar artigos repetidos durante o crawling
class RepeatedArticlePipeline(object):

   date = ''
   count = 0

   # No momento em que a instância da pipeline é gerada, o banco de dados é consultado para avaliar
   # qual a data da notícia mais recente que já foi coletada.
   # Caso haja algum problema na conexão, um aviso é passado e o programa finalizado (!!!!ajeitar!!!!)
   def __init__(self):
      try: 
         self.date = pd.read_sql(sql = 'techtudo', con=ENGINE, columns= ['date'], parse_dates={'date': '%d/%m/%Y %Hh%M'}).max()[0]
      except:
         print('Failed to conect to DB')
         pass
   
   # Se o item coletado não for vazio e a data do artigo coletado for mais recente que da última notícia presente no DB,
   # o item passa pela pipeline sem problemas.
   # Caso contrário, a flag para encerrar novos crawlers é ativado e o item descartado.
   def process_item(self, item, spider):
      article_date = datetime.datetime.strptime(item['date'].strip(), "%d/%m/%Y %Hh%M")

      if (not self.date) or (article_date > self.date):
         return item
      elif article_date <= self.date:
         self.count += 1
         if self.count >= MAX_COUNT:
            spider.close_spider = True
         raise DropItem("Incremental crawl not satisfied")
         

# Pipeline responsavel por descartar artigos repetidos durante o crawling
class DuplicatesPipeline(object):  
   def __init__(self): 
      self.ids_seen = set() 

   def process_item(self, item, spider):
      if item['url'] in self.ids_seen: 
         raise DropItem("Repeated items found: %s" % item) 
      else: 
         self.ids_seen.add(item['url']) 
         return item

# Pipeline responsavel por descartar artigos que possuem o campo do texto principal vazio
# Foram encontrados artigos vazios na base de dados, geralmente em noticias antigas
# onde o formato HTML/CSS era diferente do esperado
class EmptyPipeline(object):  

   def process_item(self, item, spider):
      if not item['text']: 
         raise DropItem("Empty URL: {}".format(item['url'])) 
      else: 
         return item

# Pipeline responsavel por enviar os dados ao banco de dados relacional MySQL
# Os dados serão enviados apenas se passarem pelas pipelines prévias
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
         line.to_sql(name=spider.name, con=ENGINE, if_exists='append',index=False)
      except:
         print('Failed to push data to db')
      return item


