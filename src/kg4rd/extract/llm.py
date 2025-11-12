# -*- coding: utf-8 -*-
# Create Date: 2025/06/03
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: llm.py
# Description: 大模型类

from google.genai.types import GenerateContentConfig
from google import genai
from google.genai.types import HttpOptions
from openai import OpenAI
from retry import retry
import json
from enum import Enum
import os
import logging
from typing import TypeVar, Generic, Any
from pydantic import BaseModel
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

T = TypeVar('T')

class Triple(BaseModel, Generic[T]):
    subject: str
    predicate: T
    object: str


class LLM(ABC):

    name: str
    config: dict[str, Any]

    @abstractmethod
    def extract_relations(*args, **kwargs) -> list:
        raise NotImplementedError
    
    @staticmethod
    def get_llm(name: str, *args, **kwargs) -> 'LLM':
        match name:
            case 'gemini':
                return Gemini(*args, **kwargs)
            case 'deepseek':
                return DeepSeek(*args, **kwargs)
            case _:
                return Gemini(*args, **kwargs)
    
class Gemini(LLM):

    name = 'gemini-2.5-flash'
    config = {
        'temperature': 0.3
    }
    
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv('GEMINI_API_KEY'), 
            http_options=HttpOptions(timeout=3*60*1000)
        )  # GOOGLE_API_KEY or GEMINI_API_KEY

    @retry(tries=5, delay=60, logger=logger)
    def extract_relations(self, system_prompt, full_prompt, relations, *args, **kwargs) -> list:
        RelationType = Enum('RelationType', {name: name for name in relations})

        response = self.client.models.generate_content(
            model=self.name,
            # contents='你好'
            contents=full_prompt,
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=self.config['temperature'],
                response_mime_type="application/json",
                response_schema=list[Triple[RelationType]],
                # thinking_config=ThinkingConfig(thinking_budget=0)
            )
        )
        return json.loads(str(response.text))
    
class DeepSeek(LLM):

    name = 'deepseek-chat'
    config = {
        'temperature': 1.0,
    }

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    @retry(tries=5, delay=60, logger=logger)
    def extract_relations(self, system_prompt, full_prompt, *args, **kwargs) -> list:
        response = self.client.chat.completions.create(
            model=self.name,
            messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt},
                ],
            stream=False,
            temperature=self.config['temperature'],
            response_format={
                'type': 'json_object'
            }
        )
        r = response.choices[0].message.content
        if r is None or len(r.strip()) == 0:
            return []   
        r = r.strip()
        if not r.startswith('[') and r.endswith(']'):
            r = '[' + r
        r = json.loads(r)
        if isinstance(r, list):
            return r
        elif isinstance(r, dict):  # maybe {'output_data': []}
            ks = list(r.keys())
            if isinstance((rs:= r[ks[0]]), list):
                return rs
        return []
                