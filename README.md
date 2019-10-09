# Desafio: Oncase

## Build

O projeto foi desenvolvido em <i>Python3.6</i>. 

#### Criar virtualenv para a execução do projeto.

```
  virtualenv --python=python3.6 oncase-env
```

#### Ativar <i>Environment</i>

```
source oncase-env/bin/activate
```

#### Instalar dependências

```
  pip install -r requirements.txt
```

#### Execução
No diretório principal, executar o seguinte comando no terminal:
```
  scrapy crawl techtudo (ou o nome de outro Crawler)
```

## Resolução: Web Crawling/Scraping
Primeiro, os sites https://www.techtudo.com.br e https://www.tecmundo.com.br foram inspecionados para saber quais elementos seriam extraídos. A biblioteca utilizada para realizar o crawl/scrap das páginas foi <i>Scrapy</i>, escrita em <i>Python</i>. O procedimento ocorre da seguinte forma:

- A primeira página a ser visitada é a página principal, onde estão contidas as últimas notícias. As URLs disponíveis para os artigos de notícia mais recentes são coletados e visitados pelo crawler.
- Dentro de cada URL de notícia, os dados referentes ao título, subtítulo e texto são extraídos. O nome do autor e a data de postagem também são coletados. Lembrando que a mesma deve possuir domínio igual ao da página principal, para evitar a visita em páginas de outros portais.
- Terminada a raspagem de cada artigo, o crawler visita a próxima página do portal que exibe notícias menos recentes. O processo é recursivo, acabando apenas quando não há mais páginas a serem visitadas.

Os dados brutos de cada página são representados por objetos da classe <i>Item</i> que possui um atributo específico para cada dado citado anteriormente. Após o objeto ser criado, o mesmo passa por 5 <i>pipelines</i> responsáveis por tratar e validar os dados. As <i>pipelines</i> são descritas a seguir:

- <b>TechTudoPipeline</b>: responsável por tratar os dados (remover caracteres indesejados e coletar apenas as palavras desejadas) e verificar se os campos extraídos não estão vazios.
- <b>RepeatedArticlePipeline</b>: caso o crawler visite uma página com data anterior à mais recente já armazenada no banco de dados, um flag que ordena a parada dos crawlers é ativado e os dados são descartados. Dessa forma, resolve as cargas incrementais no banco de dados através do próprio crawler. Lembrando que a data do artigo mais recente é consultada no banco de dados quando uma instância desta <i>pipeline</i>  criada.
- <b>DuplicatesPipeline</b>: evita que páginas repetidas sejam armazenadas no mesmo processo.
- <b>EmptyPipeline</b>: caso o campo de texto esteja vazio, todos os dados são descartados. Foi possível notar que os dados de páginas mais antigas, postadas em 2017, não eram coletados. Isso deve-se ao fato de que a estrutura da página mudou ligeiramente com o passar o do tempo.
- <b>MySQLWriterPipeline</b>: se os dados passarem por todas as pipelines anteriores sem problemas, os dados são enviados a um banco de dados relacional MySQL na nuvem (serviço RDS da Amazon Web Services). A conexão é feita através das bibliotecas <i>SQLAlchemy</i> e <i>MySQL-Connector</i>.

Os arquivos de <i>log</i> do processo são armazenados no servidor, exibindo a quantidade de itens que foram coletados, a quantidade de itens não coletados, os itens que já se encontram no banco de dados, entre outras informações.

Ao final do primeiro processo, foram coletadas informações de quase 20 mil páginas, datadas entre 2017 e 2019, com apenas uma excessão de 2012. Os dados então são coletados no <i>Jupyter Notebook</i> para uma breve análise mostrada a seguir.

## Análise de dados (TechTudo)

A figura a seguir mostra a quantidade de artigos postados nos anos destacados. Nota-se a presença de apenas um artigo no ano de 2012, destoando-se do restante dos anos (provavelmente algum erro na postagem ou um artigo de 2012 foi reaberto).

![img1](https://i.ibb.co/Xj0Y48r/articles-per-year.png)

A figura a seguir ilustra a quantidade total de artigos por ano dos 10 autores que mais escreveram no site.

![img2](https://i.ibb.co/SKXx8vY/authors.png)

A figura a seguir indica os produtos/serviços mais citados e sua ocorrência em títulos de artigos.

![img3](https://i.ibb.co/jLtJn3v/Captura-de-tela-de-2019-10-08-23-04-28.png)

## Arquitetura do sistema

O sistema conta com dois serviços da Amazon Web Services (AWS):

- 1 instância do Relational Database System (RDS) MySQL
- 1 instância do servidor EC2 Linux Ubuntu 18.04

O servidor periodicamente realiza o crawl nos sites escolhidos e, após coletados os dados, realiza uma carga incremental na base de dados. Como já foi visto, é durante o próprio processo de crawling que evita-se a extração de dados repetidos.

![img4](https://i.ibb.co/XzGRNkD/Captura-de-tela-de-2019-10-09-00-24-56.png)


## CRON Jobs

A instância do EC2 foi programada para executar o crawl/scrap a cada hora por meio do agendador de tarefas CRONTAB do prórpio servidor Linux. A seguir, a imagem retirada da plataforma AWS ilustra o uso da CPU nos exatos momentos agendados. A ideia é tornar o processo automatizado e disponibilizar imediatamente os dados no banco para possíveis análises.

![img5](https://i.ibb.co/7Ytb8Bk/Captura-de-tela-de-2019-10-08-21-30-34.png)



