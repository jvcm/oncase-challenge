import scrapy
from oncase_crawler.items import Article


class TechTudoSpider(scrapy.Spider):
    name = "techtudo"
    end_page = 100
    start_urls = [
        'https://www.techtudo.com.br/'
    ]

    def parse(self, response):
        # Visit author page
        articles = response.css('div.feed-post-body-title a::attr(href)').getall()
        next_page = response.css('div.load-more a::attr(href)').get()    

        for article in (articles):
            yield response.follow(article, callback = self.article_parse)

        if (next_page is not None) and ((TechTudoSpider.start_urls[0] in next_page) or (next_page[0] == '/')) :
            yield response.follow(next_page, callback = self.parse)

    def article_parse(self, response):

        article = Article(
            author = response.css('p.content-publication-data__from::text').get(),
            title = response.css('div.title h1.content-head__title::text').get(),
            subtitle = response.css('div.subtitle h2.content-head__subtitle::text').get(),
            date= response.css('p.content-publication-data__updated time::text').get(),
            text= response.css('p.content-text__container').getall(),
            url = response.url
        )

        yield article

