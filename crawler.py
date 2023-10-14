#! /usr/bin/env python

import argparse
import functools
import json
import random
import time
import sys
import os
import urllib.parse

import bs4, requests


class GoogleScholar(object):
    FORMATABLE_URL = "https://scholar.google.com.br/scholar?start={page_number}&q={query}&hl=pt-BR&as_sdt=0,5&as_ylo={min_year}"

    def __init__(self, query: str, min_year: int) -> None:
        self.url = functools.partial(GoogleScholar.FORMATABLE_URL.format, query=query, min_year=min_year)

    def __iter__(self):
        return GoogleScholarIterator(self.url)

class GoogleScholarIterator(object):

    def __init__(self, url_with_query: functools.partial, **kwargs) -> None:
        self.url_with_query = url_with_query
        self.page_number = kwargs.get("page_number", 0)

    def __next__(self):
        url = self.url_with_query(page_number=self.page_number)

        page = requests.get(url)

        soup = bs4.BeautifulSoup(page.text, 'html.parser')
        results = soup.find(id='gs_res_ccl_mid')

        if not results:
            raise StopIteration()

        articles = results.find_all(class_='gs_r gs_or gs_scl')

        if not articles:
            raise StopIteration()

        parsed_articles = [ self.parse_article(article) for article in articles  if article is not None ]

        self.page_number = self.page_number + 1

        return parsed_articles

    def parse_article(self, article) -> dict | None:
        try:
            pdf_link = article.find(class_="gs_or_ggsm")
            pdf_link = pdf_link.find('a', href=True)['href'] if pdf_link is not None else '-'
            title = article.find(class_='gs_rt').text
            publication_link = article.find(class_='gs_rt').a['href']

            try:
                number_citations = str(article.find(class_='gs_ri').find(class_='gs_fl'))
                number_citations = number_citations[number_citations.find("Citado por")+11:]
                number_citations = number_citations[:number_citations.find("</")]
                if not number_citations.isnumeric():
                    number_citations = None
            except Exception:
                number_citations = None

            try:
                info = article.find(class_='gs_a').text
                authors = ",".join(info.split(", ")[:-2])
                conference = info.split(', ')[-1]
                year = conference[conference.find("20"):]
                year = year[:4]
            except Exception:
                authors = None
                conference = None
                year = None

            return dict(title=title,
                        authors=authors,
                        publication_link=publication_link,
                        number_citations=number_citations,
                        pdf_link=pdf_link,
                        conference=conference,
                        year=year)

        except Exception as e:
            print('[Exception]: ', e, file=sys.stderr)
            return None

def main(query: str, num_articles: int, min_year: int, stop_pretty_print: bool):
    query = urllib.parse.quote_plus(query)

    for articles in GoogleScholar(query=query, min_year=min_year):

        match stop_pretty_print:
            case False:
                for article in articles:
                    print(json.dumps(article))

            case True:
                for article in articles:
                    print(json.dumps(article, indent=4))

        num_articles = num_articles - len(articles)

        if num_articles <= 0:
            break

        time.sleep(random.randint(1, 3))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool to craw articles with giver query in google scholar.")

    parser.add_argument("--query",
                        type=str,
                        help="Query to search for, if not given the script search for the enviroment variable: GOOGLE_SCHOLAR_QUERY.",
                        default=os.getenv("GOOGLE_SCHOLAR_QUERY", ""),
                        required=False)

    parser.add_argument("--max", type=int, help="Max amount of articles to crawl.", required=True)
    parser.add_argument("--min-year", type=int, help="Min year to consider the article.", required=True)
    parser.add_argument("--stop-pretty-print", action="store_false", help="Print json line by line to ease piping comands.")

    args = parser.parse_args()

    if not args.query:
        parser.error('--query is required when enviroment variable GOOGLE_SCHOLAR_QUERY is not set.')

    main(query=args.query,
         num_articles=args.max,
         min_year=args.min_year,
         stop_pretty_print=args.stop_pretty_print)

