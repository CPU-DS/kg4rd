# -*- coding: utf-8 -*-
# Create Date: 2025/08/01
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: main.py
# Description: 分子对接主程序

import os
import argparse
from datetime import datetime

from mol_docking import MolecularDocking
from summary import DockingSummary, DockingVisualize


def main(perotein_pdb: str, ligands_path: str, config_path: str, output_dir: str | None = None):
    
    if output_dir is None:
        output_dir = f"src/kg4rd/docking/output/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    docking = MolecularDocking(config_path)
    
    # 执行虚拟筛选
    results = docking.virtual_screening(
        perotein_pdb,
        ligands_path,
        output_dir
    )
    
    # 分析结果
    summary = DockingSummary(results)
    summary.create_markdown_report(f"{output_dir}/summary/report.md")
    
    # 可视化结果
    visualize = DockingVisualize(results)
    visualize.create_summary_report(f"{output_dir}/summary")


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--protein', type=str, help='the pdb file of the protein')
    # parser.add_argument('--ligands', type=str, help='the SMILES file of the ligands')
    # parser.add_argument('--config', type=str, help='the path of the config file')
    # parser.add_argument('--output_dir', type=str, default=None, help='the path of the output directory (optional)')
    
    # args = parser.parse_args()
    # main(args.protein, args.ligands, args.config, args.output_dir)
    main(
        'src/kg4rd/docking/data/3I40.pdb', 
        'src/kg4rd/docking/data/ligands.json', 
        'src/kg4rd/docking/config.yaml',
        'src/kg4rd/docking/output'
    )
