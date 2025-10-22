# -*- coding: utf-8 -*-
# Create Date: 2025/10/09
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: mol_prep.py
# Description: 处理蛋白质和配体

from typing import Optional
from openbabel.openbabel import OBConversion, OBMol
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem.rdDistGeom import EmbedMolecule
from rdkit.Chem.rdForceFieldHelpers import MMFFOptimizeMolecule
from Bio.PDB import PDBParser, PDBIO, Select
import yaml
from meeko import MoleculePreparation, PDBQTWriterLegacy
import os


class ProteinPreparation:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def clean_protein(self, pdb_file: str, output_file: str, remove_water: bool = True, remove_heterogens: bool = True):
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('protein', pdb_file)
        
        class CleanSelect(Select):
            def accept_residue(self, residue):  # type: ignore
                if remove_water and residue.get_resname() == 'HOH':  # 移除水分子
                    return 0
                if remove_heterogens and residue.get_id()[0] != ' ':  # 移除杂原子
                    return 0
                return 1  # 只保留标准残基
        
        io = PDBIO()
        io.set_structure(structure)
        io.save(output_file, CleanSelect())
    
    def prepare_receptor(self, pdb_file: str, output_pdbqt: str):
        obConversion = OBConversion()
        obConversion.SetInAndOutFormats("pdb", "pdbqt")

        obConversion.AddOption("r", OBConversion.OUTOPTIONS)  # 刚性受体, 不添加ROOT/扭转键
        
        mol = OBMol()
        obConversion.ReadFile(mol, pdb_file)
        
        mol.AddPolarHydrogens()  # 只添加极性氢原子
        obConversion.WriteFile(mol, output_pdbqt)  # 写入刚性受体PDBQT
     
    def get_binding_site(self, pdb_file: str, 
                        ligand_residue: Optional[str] = None) -> dict[str, float]:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('protein', pdb_file)
        
        if ligand_residue and structure: # 如果指定了配体，计算配体周围的盒子
            ligand_atoms = []
            for model in structure:
                for chain in model:
                    for residue in chain:
                        if residue.get_resname() == ligand_residue:
                            ligand_atoms.extend(residue.get_atoms())
            
            if ligand_atoms:
                coords = np.array([atom.get_coord() for atom in ligand_atoms])
                center = coords.mean(axis=0)
                size = coords.max(axis=0) - coords.min(axis=0) + 10  # 添加10 埃边距
            else:
                center, size = self._get_protein_center(structure)
        else:
            center, size = self._get_protein_center(structure)
        
        return {
            'center_x': float(center[0]),
            'center_y': float(center[1]),
            'center_z': float(center[2]),
            'size_x': float(size[0]),
            'size_y': float(size[1]),
            'size_z': float(size[2])
        }
    
    def _get_protein_center(self, structure) -> tuple[np.ndarray, np.ndarray]:
        # 计算蛋白质几何中心
        atoms = list(structure.get_atoms())
        coords = np.array([atom.get_coord() for atom in atoms])
        center = coords.mean(axis=0)
        size = np.array([self.config['grid_box']['size_x'],
                        self.config['grid_box']['size_y'],
                        self.config['grid_box']['size_z']])
        return center, size


class LigandPreparation:    
    def __init__(self):
        pass
    
    def smiles_to_mol(self, smiles: str, optimize: bool = True) -> Chem.Mol:

        mol = Chem.MolFromSmiles(smiles)  # 从 SMILES 创建分子对象
        mol = Chem.AddHs(mol)  # 添加氢原子
        
        # 生成3D构象
        if optimize:
            EmbedMolecule(mol, randomSeed=42)
            MMFFOptimizeMolecule(mol)
        
        return mol
    
    def prepare_ligand(self, mol: Chem.Mol, output_pdbqt: str):
        # 使用 meeko 准备配体
        preparator = MoleculePreparation()
        mol_prep = preparator.prepare(mol)[0]  # 原来是 list
        
        # 写入 PDBQT 文件
        writer = PDBQTWriterLegacy()
        string, _, _ = writer.write_string(mol_prep)
        with open(output_pdbqt, 'w') as f:
            f.write(string)
    
    def calc_properties(self, mol: Chem.Mol) -> dict[str, float]:
        properties = {
            'molecular_weight': Descriptors.ExactMolWt(mol),  # type: ignore # 分子量
            'logp': Descriptors.MolLogP(mol),  # type: ignore # LogP
            'hbd': Descriptors.NumHDonors(mol),  # type: ignore # 氢键供体
            'hba': Descriptors.NumHAcceptors(mol),  # type: ignore # 氢键受体
            'rotatable_bonds': Descriptors.NumRotatableBonds(mol),  # type: ignore # 可旋转键
            'tpsa': Descriptors.TPSA(mol),  # type: ignore # 拓扑极性表面积
            'num_atoms': mol.GetNumAtoms(),  # 原子数
            'num_heavy_atoms': mol.GetNumHeavyAtoms()  # 重原子数
        }
        
        return properties
    
    def check_drug_likeness(self, mol: Chem.Mol) -> dict[str, bool]:
        props = self.calc_properties(mol)
        
        rules = {
            'molecular_weight_ok': props['molecular_weight'] <= 500,
            'logp_ok': props['logp'] <= 5,
            'hbd_ok': props['hbd'] <= 5,
            'hba_ok': props['hba'] <= 10,
            'rotatable_bonds_ok': props['rotatable_bonds'] <= 10,
            'tpsa_ok': props['tpsa'] <= 140
        }
        
        rules['lipinski_pass'] = all([
            rules['molecular_weight_ok'],
            rules['logp_ok'],
            rules['hbd_ok'],
            rules['hba_ok']
        ])
        
        return rules


if __name__ == "__main__":
    ligand_prep = LigandPreparation()
    mol = ligand_prep.smiles_to_mol('CC(=O)Oc1ccccc1C(=O)O')
    ligand_prep.prepare_ligand(mol, 'src/kg4rd/docking/ligand.pdbqt')