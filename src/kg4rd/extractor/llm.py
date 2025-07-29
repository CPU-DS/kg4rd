# -*- coding: utf-8 -*-
# Create Date: 2025/06/03
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: llm.py
# Description: 大模型了类


from google.genai.types import GenerateContentConfig
from google import genai
from google.genai.types import HttpOptions
from retry import retry
import json
from enum import Enum
import os
from typing import TypeVar, Generic, overload
from pydantic import BaseModel
from abc import ABC, abstractmethod

T = TypeVar('T')

class Triple(BaseModel, Generic[T]):
    subject: str
    predicate: T
    object: str


class LLM(ABC):
    @abstractmethod
    def extract_relations(*args, **kwargs):
        raise NotImplementedError
    
    @staticmethod
    def get_llm(name: str, *args, **kwargs) -> 'LLM':
        match name:
            case 'gemini':
                return Gemini(*args, **kwargs)
            case _:
                return Gemini(*args, **kwargs)
    
class Gemini(LLM):
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'), http_options=HttpOptions(timeout=3*60*1000))

    @retry(tries=5, delay=60)
    def extract_relations(self, system_prompt, full_prompt, relations):
        RelationType = Enum('RelationType', {name: name for name in relations})

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                response_mime_type="application/json",
                response_schema=list[Triple[RelationType]]
            )
        )
        return json.loads(str(response.text))


