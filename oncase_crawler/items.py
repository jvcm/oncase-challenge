# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# Classe do item que representa a pagina de noticias a ser extraida
# Para cada URL valida e com dados relevantes, um objeto da classe abaixo e' criado
# com os atributos representando campos diferentes da noticia
class Article(scrapy.Item):
    # define the fields for your item here like:
    author = scrapy.Field()
    title = scrapy.Field()
    subtitle = scrapy.Field()
    date = scrapy.Field()
    text = scrapy.Field()
    url = scrapy.Field()
    pass

