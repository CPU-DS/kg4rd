# -*- coding: utf-8 -*-
# Create Date: 2025/06/07
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: pubmed.py
# Description: 获取 PubMed 数据

from typing import Optional, Literal
from dataclasses import dataclass
import re
import os
import time
import requests
from bs4 import BeautifulSoup
from loguru import logger
import pandas as pd
from tqdm import tqdm
from glob import glob
from retry import retry
from type import Markdown


@dataclass
class Article:
    url: str
    doi: str | None
    pmid: str
    title: str
    abstract: Markdown
    keywords: list[str]
    mesh_terms: list[str]

@retry(tries=5, delay=60)
def get_article(url: str) -> Optional[Article]:
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1", class_="heading-title").text.strip()
    doi = None
    if doi_span := soup.find("span", class_="identifier doi"):
        doi = doi_span.find("a").text.strip()
    pmid = soup.find("span", class_="identifier pubmed").find("strong").text.strip()
    abstract_content = soup.find("div", id="abstract")
    if not abstract_content:
        return None
    abstract = Markdown.from_html(str(abstract_content.find("div", class_="abstract-content")))
    keywords = []
    if ps := abstract_content.find("p", recursive=False):
        keywords = [s.strip() for s in ps.text.replace("Keywords:", "").split(";")]
    mesh_terms = [btn.text.strip() for btn in soup.find("div", class_="mesh-terms keywords-section").find_all("button")]
    return Article(url, doi, pmid, title, abstract, keywords, mesh_terms)

@retry(tries=5, delay=60)
def search_article_urls(term: str, max_count: int = None, filters: list[str] = None, size: int = None) ->list[str]:   
    logger.info(f"search article urls: {term}")  
    base_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={term}"
    for v in filters:
        base_url += f"&filter={v}"
    if size:
        base_url += f"&size={size}"
    
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
    exits = []
    
    for f in glob('data/data_abstract/*.csv'):
        filename = os.path.basename(f)
        exits.append(filename.split('.')[0])
    
    logger.info(f"exits: {exits}")
    df = pd.read_csv('data/data/orphanet/orphanet_mesh.csv')
    for idx, row in df.iterrows():
        
        logger.info(f'{idx}/{len(df)}')
        
        mesh = row['mesh']
        
        if mesh in exits:
            logger.info(f'{mesh} already exists')
            continue

        mesh_name = row['mesh_name']
        if (not pd.isna(mesh)) and mesh.startswith('D') and (not pd.isna(mesh_name)):
            logger.info(f'{mesh_name}({mesh})')
            data = []
            
            urls = search_article_urls(term=f'"{mesh_name}"[Mesh]', filters=['datesearch.y_5'], size=200, max_count=3000)
            for url in tqdm(urls):
                article = get_article(url=url)
                if article:
                    data.append({
                        'title': article.title,
                        'abstract': article.abstract.markdown,
                        'url': article.url,
                        'doi': article.doi,
                        'pmid': article.pmid,
                        'keywords':";".join(article.keywords),
                        'mesh_terms': ";".join(article.mesh_terms),
                    })
            
            pd.DataFrame(data).to_csv(f'data/data_abstract/{mesh}.csv', index=False)
