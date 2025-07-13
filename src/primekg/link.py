from unike.utils import Link
from unike.module.model import RotatE, ComplEx
import pandas as pd

ent_tol = 129375
rel_tol = 30

rotate_model = RotatE(
    ent_tol=ent_tol,
    rel_tol=rel_tol,
    dim=1024,
    margin=6.0,
    epsilon=2.0,
)

rotate_model.load_checkpoint('src/primekg/checkpoints/rotate/all/rotate-200.pth')

link = Link(
    in_path='primekg/kg/',
    model=rotate_model
)

dmd_ent_id = [32149]
drug_dis_rel_id = [3]
all_drug_ent_id = [link.ent2id[ent_name] for ent_name in link.ent2id.keys() if ent_name.split(':')[-1] == 'drug']
len(all_drug_ent_id)

df = link.link(dmd_ent_id, drug_dis_rel_id, all_drug_ent_id, device='cuda:3')
print(df.query("head == 32149 and rel == 3 and tail == 14769"))