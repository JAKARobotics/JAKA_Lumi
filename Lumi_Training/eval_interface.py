import cv2
import torch
import numpy as np
import os
import pickle
import argparse
import matplotlib.pyplot as plt
from copy import deepcopy
from itertools import repeat
# from save_image_to_disk import *
# from JAKA_utils import *
from sympy import false
from tqdm import tqdm
from einops import rearrange
# import wandb
import time
from torchvision import transforms
from utils import load_data  # data functions
from utils import sample_box_pose, sample_insertion_pose  # robot functions
from utils import compute_dict_mean, set_seed, detach_dict, calibrate_linear_vel, \
    postprocess_base_action  # helper functions
from policy import ACTPolicy, CNNMLPPolicy
from visualize_episodes import save_videos
from detr.models.latent_model import Latent_Model_Transformer
import IPython
e = IPython.embed

class ACT:
    def __init__(self,task_name):
        set_seed(0)
        from constants import SIM_TASK_CONFIGS
        task_config = SIM_TASK_CONFIGS[task_name]
        dataset_dir = task_config['dataset_dir']
        state_dim = 7
        lr_backbone = 1e-5
        backbone = 'resnet18'
        enc_layers = 4
        dec_layers = 7
        nheads = 8
        self.policy_config = {'lr': task_config['lr'],
                             'num_queries': task_config['chunk_size'],
                             'kl_weight': task_config['kl_weight'],
                             'hidden_dim': task_config['hidden_dim'],
                             'dim_feedforward': task_config['dim_feedforward'],
                             'lr_backbone': lr_backbone,
                             'backbone': backbone,
                             'enc_layers': enc_layers,
                             'dec_layers': dec_layers,
                             'nheads': nheads,
                             'camera_names': task_config['camera_names'],
                             'vq': task_config['use_vq'],
                             'action_dim': 7,
                        }
        self.config = {
            'ckpt_dir': task_config['ckpt_dir'],
            'state_dim': state_dim,
            'lr': task_config['lr'],
            'task_name': task_name,
            'episode_len':task_config['episode_len'],
        }
        self.policy = ACTPolicy(self.policy_config)
        ckpt_path = os.path.join(self.config["ckpt_dir"], "policy_best.ckpt")
        print(ckpt_path)
        loading_status = self.policy.deserialize(torch.load(ckpt_path))
        print(loading_status)
        self.policy.cuda()
        self.policy.eval()
        print(f'Loaded: {ckpt_path}')
        stats_path = os.path.join(self.config["ckpt_dir"], f'dataset_stats.pkl')
        with open(stats_path, 'rb') as f:
            self.stats = pickle.load(f)
    def get_image(images, camera_names, device='cpu'):
        curr_images = []
        for cam_name in camera_names:
            # print('推理的图像格式为（学习的时候图像格式为480*640*3）：',images[cam_name].shape)
            curr_image = rearrange(images[cam_name], 'h w c -> c h w')
            curr_images.append(curr_image)
        curr_image = np.stack(curr_images, axis=0)
        curr_image = torch.from_numpy(curr_image / 255.0).float().cuda().unsqueeze(0)
        return curr_image

    def eval_bc(self,obs):
        set_seed(0)
        pre_process = lambda s_qpos: (s_qpos - self.stats['qpos_mean']) / self.stats['qpos_std']
        post_process = lambda a: a * self.stats['action_std'] + self.stats['action_mean']
        with torch.inference_mode():
            qpos_numpy = np.array(obs['qpos'])
            qpos = pre_process(qpos_numpy)
            qpos = torch.from_numpy(qpos).float().cuda().unsqueeze(0)
            curr_image = ACT.get_image(obs['images'], self.policy_config['camera_names'])
            all_actions = self.policy(qpos, curr_image)
            processed_actions = []
            num_timesteps = all_actions.shape[1]  # 获取时间步的总数
            for t in range(num_timesteps):
                # 获取当前时间步的动作
                raw_action = all_actions[:, t]
                raw_action = raw_action.squeeze(0).cpu().numpy()  # 转换为 numpy 数组
                action = post_process(raw_action)  # 后处理动作
                processed_actions.append(action)  # 将处理后的动作添加到列表中
        return processed_actions
    def eval_with_temporal_agg(self,obs,index):
        num_queries = self.policy_config['num_queries']
        all_time_actions = torch.zeros([self.config['episode_len'], self.config['episode_len'] + num_queries, 16]).cuda()
        pre_process = lambda s_qpos: (s_qpos - self.stats['qpos_mean']) / self.stats['qpos_std']
        post_process = lambda a: a * self.stats['action_std'] + self.stats['action_mean']
        with torch.inference_mode():
            qpos_numpy = np.array(obs['qpos'])
            qpos = pre_process(qpos_numpy)
            qpos = torch.from_numpy(qpos).float().cuda().unsqueeze(0)
            curr_image = ACT.get_image(obs['images'], self.policy_config['camera_names'])
            all_actions = self.policy(qpos, curr_image)
            all_time_actions[[index], index:index + num_queries] = all_actions
            actions_for_curr_step = all_time_actions[:, index]
            actions_populated = torch.all(actions_for_curr_step != 0, axis=1)
            actions_for_curr_step = actions_for_curr_step[actions_populated]
            k = 0.01
            exp_weights = np.exp(-k * np.arange(len(actions_for_curr_step)))
            exp_weights = exp_weights / exp_weights.sum()
            exp_weights = torch.from_numpy(exp_weights).cuda().unsqueeze(dim=1)
            raw_action = (actions_for_curr_step * exp_weights).sum(dim=0, keepdim=True)
            raw_action = raw_action.squeeze(0).cpu().numpy()
            action = post_process(raw_action)
        return action
if __name__ == '__main__':
    act = ACT("sim_transfer_cube_scripted")
    # action = act.eval_bc(obs=obs)
