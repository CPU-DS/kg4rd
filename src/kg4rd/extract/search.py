# -*- coding: utf-8 -*-
# Create Date: 2025/09/11
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: search.py
# Description: 结果搜索

from typing import Optional
import json
from pprint import pprint

result_path = 'data/data_abstract/result'

def search_by_uid(uid: str) -> Optional[dict]:
    mesh_id, pmid, _ = tuple(uid.split(':'))
    with open(f'{result_path}/{mesh_id}.json') as f:
        data = json.load(f)
    for item in data:
        if item['pmid'] == int(pmid):
            for triple in item['extracted_relations']:
                if triple['uid'] == uid:
                    return item
    return None

if __name__ == '__main__':
    pprint(search_by_uid('D020388:38271438:AY7gCD52dmNamEuxC4aFrQ'))
