# -*- coding: utf-8 -*-
# Create Date: 2025/06/07
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: types.py
# Description: 中间类型

from typing import Any
import html2text


class Markdown:
    
    html2md = html2text.HTML2Text()
    html2md.ignore_links = True
    html2md.ignore_images = True
    html2md.ignore_tables = True
    html2md.body_width = 0
    
    def __init__(self, markdown: str) -> None:
        self.markdown = markdown
    
    @classmethod
    def from_html(cls, html: Any) -> "Markdown":
        return cls(cls.html2md.handle(str(html)).strip())

    def __str__(self) -> str:
        return self.markdown
    
    def __repr__(self) -> str:
        return self.markdown
    