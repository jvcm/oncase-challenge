import scrapy
from oncase_crawler.items import Article
from scrapy.exceptions import CloseSpider

# Spider responsavel por visitar as paginas do site www.techtudo.com.br e extrair os dados
# encontrados em cada artigo de noticias
class TechTudoSpider(scrapy.Spider):
    name = "techtudo"
    start_urls = [
        'https://www.techtudo.com.br/'
    ]
    close_spider = False

# Metodo responsavel por fazer o parse das informacoes na pagina de busca de noticias
    def parse(self, response):
        # Visit author page

        articles = response.css('div.feed-post-body-title a::attr(href)').getall()
        next_page = response.css('div.load-more a::attr(href)').get()    

        # Visita-se cada artigo encontrado na pagina de resultados para extrair os dados
        # chamando o metodo 'article_parse'
        for article in (articles):
            yield response.follow(article, callback = self.article_parse)

        # Quando todos os artigos sao extraidos com sucesso (ou nao), o link para
        # "proxima pagina" e' visitado e novos artigos sao mostrados no campo de busca
        if (next_page is not None) and ((TechTudoSpider.start_urls[0] in next_page) or (next_page[0] == '/')) :
            yield response.follow(next_page, callback = self.parse)


# Em cada pagina de artigo, as informacoes sao extraidas pelo metodo 'article_parse'
# Os dados serao subsequentemente tratados atraves das pipelines
    def article_parse(self, response):

        # Caso a flag na pipeline de itens repetidos no DB for ativada, o programa levanta uma exceção
        # e novos dados não serao mais coletados
        if self.close_spider:
            raise CloseSpider('Crawl is finished')

        article = Article(
            author = response.css('p.content-publication-data__from::text').get(),
            title = response.css('div.title h1.content-head__title::text').get(),
            subtitle = response.css('div.subtitle h2.content-head__subtitle::text').get(),
            date= response.css('p.content-publication-data__updated time::text').get(),
            text= response.css('p.content-text__container').getall(),
            url = response.url
        )

        yield article

