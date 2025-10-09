# -*- coding: utf-8 -*-
# Create Date: 2025/10/07
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: ggd.py
# Description: GGD 模型

from torch_geometric.nn import GCNConv
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Literal


class GraphEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 512, output_dim: int = 256):
        super().__init__()
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, output_dim)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.conv1(x, edge_index))
        x = self.dropout(x)
        x = self.conv2(x, edge_index)
        return x


class GraphGenerator(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 512):
        super().__init__()
        self.generator = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Tanh()
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.generator(x)


class GraphDiscriminator(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.discriminator = nn.Sequential(
            nn.Linear(input_dim, input_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(input_dim // 2, input_dim // 4),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(input_dim // 4, 1)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.discriminator(x)


class GGD(nn.Module):
    def __init__(self, 
            input_dim: int, 
            hidden_dim: int = 512, 
            output_dim: int = 256):
        super().__init__()
        self.encoder = GraphEncoder(input_dim, hidden_dim, output_dim)
        self.generator = GraphGenerator(input_dim, hidden_dim)
        self.discriminator = GraphDiscriminator(output_dim)
        
        self.projection_head = nn.Sequential(
            nn.Linear(output_dim, output_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(output_dim, output_dim)
        )
        
        self.generation_type: Literal['noise', 'transform'] = 'transform'
        
    def generate_fake_features(self, x: torch.Tensor) -> torch.Tensor:
        match self.generation_type:
            case 'noise':
                noise = torch.randn_like(x)  # 完全随机噪声
                fake_features = self.generator(noise)
            case _:  # transform
                noisy_x = x + torch.randn_like(x) * 0.1
                fake_features = self.generator(noisy_x)
        return fake_features
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        real_repr = self.encoder(x, edge_index)
        real_proj = self.projection_head(real_repr)
        
        fake_features = self.generate_fake_features(x)
        
        fake_repr = self.encoder(fake_features, edge_index)
        fake_proj = self.projection_head(fake_repr)
        
        return real_proj, fake_proj, real_repr
    
    def loss(self, real_proj: torch.Tensor, fake_proj: torch.Tensor, real_repr: torch.Tensor) -> torch.Tensor:
        # 判别器损失
        real_scores = self.discriminator(real_repr)
        fake_scores = self.discriminator(fake_proj.detach())
        
        label_smoothing = 0.1
        disc_real_loss = F.binary_cross_entropy_with_logits(
            real_scores.squeeze(), 
            torch.ones_like(real_scores.squeeze()) * (1 - label_smoothing)
        )
        disc_fake_loss = F.binary_cross_entropy_with_logits(
            fake_scores.squeeze(), 
            torch.zeros_like(fake_scores.squeeze()) + label_smoothing
        )
        discriminator_loss = disc_real_loss + disc_fake_loss
        
        # 生成器损失
        fake_scores_gen = self.discriminator(fake_proj)
        generator_loss = F.binary_cross_entropy_with_logits(
            fake_scores_gen.squeeze(),
            torch.ones_like(fake_scores_gen.squeeze())  # 希望判别器认为是真的
        )
        
        # 对比损失
        # 使用余弦相似度
        real_proj = F.normalize(real_proj, dim=1)
        sim_matrix = torch.mm(real_proj, real_proj.t())

        batch_size = real_proj.size(0)
        temperature = 0.5
        
        pos_mask = torch.eye(batch_size, device=real_proj.device)  # 正样本 mask
        neg_mask = 1 - pos_mask  # 负样本 mask

        exp_sim = torch.exp(sim_matrix / temperature)
        pos_sim = (exp_sim * pos_mask).sum(dim=1)
        neg_sim = (exp_sim * neg_mask).sum(dim=1)
        
        contrastive_loss = -torch.log(pos_sim / (neg_sim + pos_sim + 1e-8)).mean()
        
        # 总损失
        total_loss = discriminator_loss + 0.5 * generator_loss + 0.3 * contrastive_loss
        
        return total_loss


