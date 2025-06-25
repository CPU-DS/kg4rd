# -*- coding: utf-8 -*-
# Create Date: 2025/06/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: obo_parser.py
# Description: OBO 文件解析并提取同义词


from collections import defaultdict
from tqdm import tqdm
import csv


class OBOParser:
    def __init__(self, obo_path, id_prefix=None):
        self.obo_path = obo_path
        self.id_prefix = id_prefix
        self.terms = []
        self.xref_mapping = defaultdict(list)

    def parse(self):
        with open(self.obo_path, 'rt', encoding='utf-8') as f:
            current_term = None

            for line in tqdm(f, desc="Parsing OBO"):
                line = line.strip()

                if line.startswith('[Term]'):
                    current_term = {
                        'id': '', 
                        'name': '', 
                        'def': '',
                        'synonyms': [], 
                        'xrefs': [], 
                        'is_a': [],
                        'intersection_of': [], 
                        'relationship': [], 
                        'is_not': []
                    }
                elif line.startswith(('[Typedef]', '[Instance]')):
                    current_term = None

                elif current_term is not None:
                    self._process_line(line, current_term)

                if line == '' and current_term is not None:
                    self._store_term(current_term)
                    current_term = None

            if current_term is not None:
                self._store_term(current_term)

        return self.terms

    def _process_line(self, line, term):
        if line.startswith('id:'):
            term['id'] = line.split(':', 1)[1].strip()
        elif line.startswith('name:'):
            term['name'] = line.split(':', 1)[1].strip()
        elif line.startswith('def:'):
            term['def'] = line.split('"', 2)[1].strip()
        elif line.startswith('synonym:'):
            synonym = line.split('"', 2)[1].strip()
            term['synonyms'].append(synonym)
        elif line.startswith('is_a:'):
            is_a = line.split(' ', 1)[1].split('!')[0].strip()
            is_a = is_a.split('{', 1)[0].strip()
            term['is_a'].append(is_a)
        elif line.startswith("intersection_of"):
            if '!' in line:
                intersection_of = line.split(' ')[1]
                if '_' in intersection_of:
                    intersection_of = intersection_of + " " + line.split('!')[1].strip()
                else:
                    intersection_of = line.split('!')[1].strip()
            else:
                intersection_of = line.split(' ')[1].strip()
            term['intersection_of'].append(intersection_of)
        elif line.startswith("disjoint_from"):
            is_not = 'is disjoint from ' + line.split('!')[1].strip()
            term['is_not'].append(is_not)
        elif line.startswith("relationship"):
            relationship = line.split(' ')[1]
            if "!" in line:
                relationship = relationship + " " + line.split('!')[1].strip()
            if relationship.startswith('MONDO'):
                relationship = relationship[13:]
            if relationship.startswith('excluded_subClassOf'):
                is_not = 'is not a subtype of ' + relationship[19:]
                term['is_not'].append(is_not)
            elif relationship != 'should_conform_to':
                term['relationship'].append(relationship)

    def _store_term(self, term):
        if self.id_prefix and not term['id'].startswith(self.id_prefix):
            return
        self.terms.append({
            'id': term['id'],
            'name': term['name'],
            'synonyms': term['synonyms'],
            'def': term['def']
        })


if __name__ == "__main__":
    OBO_PATH = [
        ("data/go/go-basic.obo", "data_synonyms/go_synonyms.csv", None),
        ("data/hdo/HumanDO.obo", "data_synonyms/do_synonyms.csv", "DOID"),
        ("data/hpo/hp.obo", "data_synonyms/hpo_synonyms.csv", None),
        ("data/mondo/mondo.obo", "data_synonyms/mondo_synonyms.csv", "MONDO"),
        ("data/uberon/ext.obo", "data_synonyms/uberon_synonyms.csv", "UBERON"),
    ]

    for obo_path, output_path, id_prefix in OBO_PATH:
        parser = OBOParser(obo_path, id_prefix)
        all_terms = parser.parse()

        for term in all_terms:
            term['synonyms'] = [x for x in set(term['synonyms']) if x != term['name']]

        with open(output_path, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id', 'name', 'preferred_name'])

            for term in all_terms:
                writer.writerow([term['id'], term['name'], True])
                for synonym in term['synonyms']:
                    writer.writerow([term['id'], synonym, ''])
