# -*- coding: utf-8 -*-
# Create Date: 2025/06/07
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: pubmed.py
# Description: 获取 PubMed 数据

from typing import Optional, Literal
from dataclasses import dataclass
import re

import requests
from bs4 import BeautifulSoup
from loguru import logger
import pandas as pd

from type import Markdown


@dataclass
class Article:
    url: str
    doi: str
    pmid: str
    title: str
    abstract: Markdown
    keywords: list[str]
    mesh_terms: list[str]


def get_article(url: str) -> Optional[Article]:
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1", class_="heading-title").text.strip()
    doi = soup.find("span", class_="identifier doi").find("a").text.strip()
    pmid = soup.find("span", class_="identifier pubmed").find("strong").text.strip()
    abstract_content = soup.find("div", id="abstract")
    abstract = Markdown.from_html(str(abstract_content.find("div", class_="abstract-content")))
    keywords = []
    if ps := abstract_content.find("p", recursive=False):
        keywords = [s.strip() for s in ps.text.replace("Keywords:", "").split(";")]
    mesh_terms = [btn.text.strip() for btn in soup.find("div", class_="mesh-terms keywords-section").find_all("button", class_="keyword-actions-trigger trigger keyword-link")]
    return Article(url, doi, pmid, title, abstract, keywords, mesh_terms)


def search_article_urls(term: str, max_count: int = None, filters: list[str] = None) ->list[str]:   
    logger.info(f"search article urls: {term}")  
    base_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={term}"
    for v in filters:
        base_url += f"&filter={v}"
    
    page = 1
    article_urls = []
    while True:
        url = f"{base_url}&page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article")
        if not articles:
            break
        logger.info(f"page {page} found {len(articles)} articles")
        for article in articles:
            article_urls.append("https://pubmed.ncbi.nlm.nih.gov" + article.find("a")["href"])
        if max_count and len(article_urls) >= max_count:
            article_urls = article_urls[:max_count]
            logger.info(f"max_count reached")
            break
        page += 1

    logger.success(f"return {len(article_urls)} article urls")
    return article_urls


if __name__ == "__main__":
    
    df = pd.read_csv('data/orphanet/orphanet_mesh.csv')
    for _, row in df.iterrows():
        name = row['name']
        mesh = row['mesh']
        mesh_name = row['mesh_name']
        if pd.isna(mesh_name):
            search_article_urls(f'"{name}"[Title/Abstract]')
    
    # article_urls = search_article_urls('"Acute myocardial infarction"[pt] AND "Acute myocardial infarction"[pt]')
    # print(article_urls)
