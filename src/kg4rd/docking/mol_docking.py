# -*- coding: utf-8 -*-
# Create Date: 2025/10/09
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: mol_docking.py
# Description: 使用AutoDock Vina进行分子对接

import os
import subprocess
from typing import Any, Optional
import pandas as pd
import yaml
from mol_prepare import ProteinPreparation, LigandPreparation
import json


class MolecularDocking:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        
        self.vina_path = self.config['vina']['executable']
        self.protein_prep = ProteinPreparation(config_path)
        self.ligand_prep = LigandPreparation()
    
    def dock_single(self, 
                    receptor_pdbqt: str, 
                    ligand_pdbqt: str,
                    center: dict[str, float], 
                    size: dict[str, float],
                    output_prefix: str) -> dict[str, Any]:
        output_pdbqt = f"{output_prefix}_docked.pdbqt"

        cmd = [
            self.vina_path,
            "--receptor", receptor_pdbqt,
            "--ligand", ligand_pdbqt,
            "--center_x", str(center['center_x']),
            "--center_y", str(center['center_y']),
            "--center_z", str(center['center_z']),
            "--size_x", str(size['size_x']),
            "--size_y", str(size['size_y']),
            "--size_z", str(size['size_z']),
            "--exhaustiveness", str(self.config['vina']['exhaustiveness']),
            "--num_modes", str(self.config['vina']['num_modes']),
            "--energy_range", str(self.config['vina']['energy_range']),
            "--out", output_pdbqt,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        stdout = r.stdout
        with open(f'{output_prefix}.log', 'w') as f:
            f.write(stdout)
        
        docking_results = self._parse_vina_output(stdout, output_pdbqt)
        return docking_results
    
    def _parse_vina_output(self, log: str, output_pdbqt: str) -> dict[str, Any]:
        results = {
            'poses': [],
            'best_affinity': None,
            'output_file': output_pdbqt
        }
        
        lines = log.split('\n')
        
        start_idx = None
        for i, line in enumerate(lines):
            if "mode |   affinity | dist from best mode" in line:
                start_idx = i + 2  # 结果表格
                break
        
        if start_idx is None:
            return results

        for i in range(start_idx, len(lines)):
            line = lines[i].strip()  # 每一行结果
            if not line or "Writing output" in line:
                break
            
            parts = line.split()
            if len(parts) >= 3:
                pose = {
                    'mode': int(parts[0]),
                    'affinity': float(parts[1]),
                    'rmsd_lb': float(parts[2]),
                    'rmsd_ub': float(parts[3]) if len(parts) > 3 else float(parts[2])
                }
                results['poses'].append(pose)
        
        if results['poses']:
            results['best_affinity'] = results['poses'][0]['affinity']
        return results
    
    def dock_multiple(self, 
                      receptor_pdbqt: str, 
                      ligand_files: list[str],
                      center: dict[str, float], 
                      size: dict[str, float],
                      output_dir: str) -> pd.DataFrame:
        all_results = []
        
        for ligand_file in ligand_files:
            ligand_name = os.path.splitext(os.path.basename(ligand_file))[0]
            output_prefix = os.path.join(output_dir, ligand_name)
            
            result = self.dock_single(
                receptor_pdbqt, 
                ligand_file,
                center, 
                size, 
                output_prefix
            )
            
            result['ligand_name'] = ligand_name
            result['ligand_file'] = ligand_file
            all_results.append(result)

        df_results = self._create_results_dataframe(all_results)
        df_results.to_csv(os.path.join(output_dir, "docking_results.csv"), index=False)
        return df_results
    
    def _create_results_dataframe(self, results: list[dict]) -> pd.DataFrame:

        data = []
        
        for result in results:
            ligand_name = result['ligand_name']
            
            # 添加最佳构象信息
            if result['poses']:
                best_pose = result['poses'][0]
                data.append({
                    'ligand_name': ligand_name,
                    'best_affinity': best_pose['affinity'],
                    'best_rmsd_lb': best_pose['rmsd_lb'],
                    'best_rmsd_ub': best_pose['rmsd_ub'],
                    'num_poses': len(result['poses']),
                    'output_file': result['output_file']
                })
        
        df = pd.DataFrame(data)
        df = df.sort_values('best_affinity', ascending=True)  # 按亲和力排序（越负越好）
        return df
    
    def virtual_screening(self, receptor_pdb: str, ligands_path: str, output_dir: str) -> pd.DataFrame:
        
        # 准备受体
        receptor_clean = os.path.join(output_dir, "receptor_clean.pdb")
        receptor_pdbqt = os.path.join(output_dir, "receptor.pdbqt")
        
        self.protein_prep.clean_protein(receptor_pdb, receptor_clean)
        self.protein_prep.prepare_receptor(receptor_clean, receptor_pdbqt)
        
        # 获取对接盒子
        box_info = self.protein_prep.get_binding_site(receptor_clean)
        center = {k: v for k, v in box_info.items() if 'center' in k}
        size = {k: v for k, v in box_info.items() if 'size' in k}
        
        # 准备配体
        with open(ligands_path, 'r') as f:
            ligands = json.load(f)
            
        smiles_list = [ligand['smiles'] for ligand in ligands]  # 配体 SMILES 列表
        ligand_names = [ligand['name'] for ligand in ligands]  # 配体名称
        
        ligand_files = []
        ligand_props = []
        
        for smiles, ligand_name in zip(smiles_list, ligand_names):
            
            mol = self.ligand_prep.smiles_to_mol(smiles)
            
            # 计算分子性质
            props = self.ligand_prep.calc_properties(mol)
            props['ligand_name'] = ligand_name
            props['smiles'] = smiles
            
            # 检查类药性
            drug_likeness = self.ligand_prep.check_drug_likeness(mol)
            props.update(drug_likeness)
            
            # 准备PDBQT文件
            ligand_pdbqt = os.path.join(output_dir, f"{ligand_name}.pdbqt")
            self.ligand_prep.prepare_ligand(mol, ligand_pdbqt)
            
            ligand_files.append(ligand_pdbqt)
            ligand_props.append(props)

        docking_results = self.dock_multiple(
            receptor_pdbqt, ligand_files, center, size, output_dir
        )
        
        # 合并分子性质和对接结果
        df_props = pd.DataFrame(ligand_props)
        df_final = pd.merge(docking_results, df_props, on='ligand_name', how='inner')
        
        # 添加评分
        df_final['docking_score'] = -df_final['best_affinity']  # 转换为正分数
        
        # 保存完整结果
        final_results_file = os.path.join(output_dir, "virtual_screening_results.csv")
        df_final.to_csv(final_results_file, index=False)
        
        return df_final
    
    def evaluate_docking(self, 
                         results_df: pd.DataFrame,
                        affinity_threshold: Optional[float] = None) -> dict[str, Any]:
        if affinity_threshold is None:  # 亲和力阈值 kcal/mol
            affinity_threshold = self.config['scoring']['affinity_threshold']
        
        evaluation = {
            'total_ligands': len(results_df),
            'affinity_threshold': affinity_threshold,
            'hits': len(results_df[results_df['best_affinity'] <= affinity_threshold]),
            'hit_rate': 0,
            'best_affinity': results_df['best_affinity'].min(),
            'worst_affinity': results_df['best_affinity'].max(),
            'mean_affinity': results_df['best_affinity'].mean(),
            'std_affinity': results_df['best_affinity'].std()
        }
        
        if evaluation['total_ligands'] > 0:
            evaluation['hit_rate'] = evaluation['hits'] / evaluation['total_ligands']
        
        # 如果有类药性信息，添加统计
        if 'lipinski_pass' in results_df.columns:
            evaluation['lipinski_pass'] = results_df['lipinski_pass'].sum()
            evaluation['lipinski_pass_rate'] = evaluation['lipinski_pass'] / len(results_df)
        
        return evaluation
