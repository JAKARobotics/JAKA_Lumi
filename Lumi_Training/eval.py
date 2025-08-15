import cv2
import torch
import numpy as np
import os
import pickle
import argparse
import matplotlib.pyplot as plt
from copy import deepcopy
from itertools import repeat
from save_image_to_disk import *
# from JAKA_utils import *
from sympy import false
from tqdm import tqdm
from einops import rearrange
import wandb
import time
from torchvision import transforms

from constants import FPS
from constants import PUPPET_GRIPPER_JOINT_OPEN
from utils import load_data  # data functions
from utils import sample_box_pose, sample_insertion_pose  # robot functions
from utils import compute_dict_mean, set_seed, detach_dict, calibrate_linear_vel, \
    postprocess_base_action  # helper functions
from policy import ACTPolicy, CNNMLPPolicy
from visualize_episodes import save_videos

from detr.models.latent_model import Latent_Model_Transformer
# 初始化 OpenCV 窗口
screen_width = 1920  # 或者使用屏幕分辨率自适应的方法
screen_height = 1080  # 例如 1920x1080

# 初始化窗口
cv2.namedWindow('left', cv2.WINDOW_NORMAL)
cv2.namedWindow('middle', cv2.WINDOW_NORMAL)
cv2.namedWindow('right', cv2.WINDOW_NORMAL)

# 设置每个窗口的大小为屏幕的三分之一大小
window_width = screen_width // 3
window_height = screen_height // 2

# 设置每个窗口的位置，使它们占据屏幕的三分之一
cv2.moveWindow('left', 0, 0)  # 左边窗口
cv2.resizeWindow('left', window_width, window_height)

cv2.moveWindow('middle', window_width, 0)  # 中间窗口
cv2.resizeWindow('middle', window_width, window_height)

cv2.moveWindow('right', window_width * 2, 0)  # 右边窗口
cv2.resizeWindow('right', window_width, window_height)

import IPython

e = IPython.embed


def get_auto_index(dataset_dir):
    max_idx = 1000
    for i in range(max_idx + 1):
        if not os.path.isfile(os.path.join(dataset_dir, f'qpos_{i}.npy')):
            return i
    raise Exception(f"Error getting auto index, or more than {max_idx} episodes")

left_robot = Robot('192.168.2.222')
right_robot = Robot('192.168.2.223')
for i in range(20):
    left_robot.move_robot(
            [-0.6457718232379019, -1.0995574287564276, 0.7504915783575616, -1.2042771838760873, 0.47123889803846897,
             1.0471975511965976, 0.0])
    right_robot.move_robot(
            [0.6459845908728373, -1.1034952671598062, -0.7624523260870142, -1.2064142769752697, -0.4805595013881306,
             -1.0510644578917985, 0.0])
    left_robot.set_grapper(1)
    right_robot.set_grapper(1)
ctx = Context()
device_list = ctx.query_devices()
print('######################', device_list.get_count())
device1 = device_list.get_device_by_index(2)
device2 = device_list.get_device_by_index(1)
device3 = device_list.get_device_by_index(0)
pipeline1 = initialize_pipeline(device1)
pipeline2 = initialize_pipeline(device2)
pipeline3 = initialize_pipeline(device3)
# pipelines = [pipeline1, pipeline2,pipeline3]
pipelines = [ pipeline2,pipeline3]
image1 = capture_color_image(pipeline1)
image2 = capture_color_image(pipeline2)
image3 = capture_color_image(pipeline3)
cv2.imshow('left', image1)
cv2.imshow('middle', image2)
cv2.imshow('right', image3)
cv2.waitKey(10)
def main(args):

    set_seed(1)
    # command line parameters
    is_eval = args['eval']
    ckpt_dir = args['ckpt_dir']
    policy_class = args['policy_class']
    onscreen_render = args['onscreen_render']
    task_name = args['task_name']
    batch_size_train = args['batch_size']
    batch_size_val = args['batch_size']
    num_steps = args['num_steps']
    eval_every = args['eval_every']
    validate_every = args['validate_every']
    save_every = args['save_every']
    resume_ckpt_path = args['resume_ckpt_path']

    # get task parameters
    from constants import SIM_TASK_CONFIGS
    task_config = SIM_TASK_CONFIGS[task_name]
    dataset_dir = task_config['dataset_dir']
    # num_episodes = task_config['num_episodes']
    episode_len = task_config['episode_len']
    camera_names = task_config['camera_names']
    stats_dir = task_config.get('stats_dir', None)
    sample_weights = task_config.get('sample_weights', None)
    train_ratio = task_config.get('train_ratio', 0.99)
    name_filter = task_config.get('name_filter', lambda n: True)

    # fixed parameters
    state_dim = 7
    lr_backbone = 1e-5
    backbone = 'resnet18'
    if policy_class == 'ACT':
        enc_layers = 4
        dec_layers = 7
        nheads = 8
        policy_config = {'lr': args['lr'],
                         'num_queries': args['chunk_size'],
                         'kl_weight': args['kl_weight'],
                         'hidden_dim': args['hidden_dim'],
                         'dim_feedforward': args['dim_feedforward'],
                         'lr_backbone': lr_backbone,
                         'backbone': backbone,
                         'enc_layers': enc_layers,
                         'dec_layers': dec_layers,
                         'nheads': nheads,
                         'camera_names': camera_names,
                         'vq': args['use_vq'],
                         'vq_class': args['vq_class'],
                         'vq_dim': args['vq_dim'],
                         'action_dim': 7,
                         'no_encoder': args['no_encoder'],
                         }
    # elif policy_class == 'Diffusion':
    #
    #     policy_config = {'lr': args['lr'],
    #                      'camera_names': camera_names,
    #                      'action_dim': 16,
    #                      'observation_horizon': 1,
    #                      'action_horizon': 8,
    #                      'prediction_horizon': args['chunk_size'],
    #                      'num_queries': args['chunk_size'],
    #                      'num_inference_timesteps': 10,
    #                      'ema_power': 0.75,
    #                      'vq': False,
    #                      }
    config = {
        'num_steps': num_steps,
        'eval_every': eval_every,
        'validate_every': validate_every,
        'save_every': save_every,
        'ckpt_dir': ckpt_dir,
        'resume_ckpt_path': resume_ckpt_path,
        'episode_len': episode_len,
        'state_dim': state_dim,
        'lr': args['lr'],
        'policy_class': policy_class,
        'onscreen_render': onscreen_render,
        'policy_config': policy_config,
        'task_name': task_name,
        'seed': args['seed'],
        'temporal_agg': args['temporal_agg'],
        'camera_names': camera_names,
        # 'real_robot': not is_sim,
        'load_pretrain': args['load_pretrain'],
    }

    if not os.path.isdir(ckpt_dir):
        os.makedirs(ckpt_dir)
    eval_bc(config, 'policy_best.ckpt', save_episode=True, num_rollouts=10)


def make_policy(policy_class, policy_config):
    if policy_class == 'ACT':
        policy = ACTPolicy(policy_config)
    elif policy_class == 'CNNMLP':
        policy = CNNMLPPolicy(policy_config)
    elif policy_class == 'Diffusion':
        policy = DiffusionPolicy(policy_config)
    else:
        raise NotImplementedError
    return policy


def make_optimizer(policy_class, policy):
    if policy_class == 'ACT':
        optimizer = policy.configure_optimizers()
    elif policy_class == 'CNNMLP':
        optimizer = policy.configure_optimizers()
    elif policy_class == 'Diffusion':
        optimizer = policy.configure_optimizers()
    else:
        raise NotImplementedError
    return optimizer

def get_image(images, camera_names, device='cpu'):
    curr_images = []
    for cam_name in camera_names:
        # print('推理的图像格式为（学习的时候图像格式为480*640*3）：',images[cam_name].shape)
        curr_image = rearrange(images[cam_name], 'h w c -> c h w')
        curr_images.append(curr_image)
    curr_image = np.stack(curr_images, axis=0)
    curr_image = torch.from_numpy(curr_image / 255.0).float().cuda().unsqueeze(0)
    return curr_image

def eval_bc(config, ckpt_name, save_episode=True, num_rollouts=50):
    set_seed(0)
    ckpt_dir = config['ckpt_dir']
    policy_class = config['policy_class']
    policy_config = config['policy_config']
    camera_names = config['camera_names']
    max_timesteps = config['episode_len']
    temporal_agg = True
    # load policy and stats
    ckpt_path = os.path.join(ckpt_dir, ckpt_name)
    policy = make_policy(policy_class, policy_config)
    loading_status = policy.deserialize(torch.load(ckpt_path))
    print(loading_status)
    policy.cuda()
    policy.eval()
    print(f'Loaded: {ckpt_path}')
    stats_path = os.path.join(ckpt_dir, f'dataset_stats.pkl')
    with open(stats_path, 'rb') as f:
        stats = pickle.load(f)
    pre_process = lambda s_qpos: (s_qpos - stats['qpos_mean']) / stats['qpos_std']
    post_process = lambda a: a * stats['action_std'] + stats['action_mean']
    query_frequency = policy_config['num_queries']
    if temporal_agg:
        query_frequency = 1
        num_queries = policy_config['num_queries']
    max_timesteps = int(max_timesteps * 1)  # may increase for real-world tasks
    for rollout_id in range(num_rollouts):
        for i in range(20):
            left_robot.move_robot(
                [-0.6457718232379019, -1.0995574287564276, 0.7504915783575616, -1.2042771838760873, 0.47123889803846897,
                 1.0471975511965976, 0.0])
            right_robot.move_robot(
                [0.6459845908728373, -1.1034952671598062, -0.7624523260870142, -1.2064142769752697, -0.4805595013881306,
                 -1.0510644578917985, 0.0])
            left_robot.set_grapper(1)
            right_robot.set_grapper(1)
        rollout_id += 0
        ### evaluation loop
        if temporal_agg:
            all_time_actions = torch.zeros([max_timesteps, max_timesteps + num_queries, 16]).cuda()
        with torch.inference_mode():
            for t in range(max_timesteps):
                ### process previous timestep to get qpos and image_list
                print('第',t,"轮",'######################更新OBS############################')
                obs = {
                    'qpos': left_robot.get_joint_position() + right_robot.get_joint_position(),
                    'qvel': left_robot.get_joint_vel() + right_robot.get_joint_vel(),
                    'images': {cn: capture_color_image(pipeline) for cn, pipeline in
                               zip(camera_names, pipelines)}
                }

                # cv2.imshow('left', obs["images"]["left_cam"])
                cv2.imshow('middle', obs["images"]["middle_cam"])
                cv2.imshow('right', obs["images"]["right_cam"])
                cv2.waitKey(1)
                qpos_numpy = np.array(obs['qpos'])
                qpos = pre_process(qpos_numpy)
                qpos = torch.from_numpy(qpos).float().cuda().unsqueeze(0)
                if t % query_frequency == 0:
                    curr_image = get_image(obs['images'], camera_names)
                if t == 0:
                    # warm up
                    for _ in range(10):
                        policy(qpos, curr_image)
                    print('network warm up done')
                    time1 = time.time()

                ### query policy
                time3 = time.time()
                if config['policy_class'] == "ACT":
                    if t % query_frequency == 0:
                        print('第',t,"轮",'######################更新动作############################')
                        all_actions = policy(qpos, curr_image)
                    if temporal_agg:
                        all_time_actions[[t], t:t + num_queries] = all_actions
                        actions_for_curr_step = all_time_actions[:, t]
                        actions_populated = torch.all(actions_for_curr_step != 0, axis=1)
                        actions_for_curr_step = actions_for_curr_step[actions_populated]
                        k = 0.01
                        exp_weights = np.exp(-k * np.arange(len(actions_for_curr_step)))
                        exp_weights = exp_weights / exp_weights.sum()
                        exp_weights = torch.from_numpy(exp_weights).cuda().unsqueeze(dim=1)
                        raw_action = (actions_for_curr_step * exp_weights).sum(dim=0, keepdim=True)
                    else:
                        raw_action = all_actions[:, t % query_frequency]
                ### post-process actions
                time4 = time.time()
                raw_action = raw_action.squeeze(0).cpu().numpy()
                action = post_process(raw_action)
                right_robot.move_robot(action[8:15])
                right_robot.set_grapper(action[15:16])
                left_robot.move_robot(action[0:7])
                left_robot.set_grapper(action[7:8])
                print(action)



def forward_pass(data, policy):
    image_data, qpos_data, action_data, is_pad = data
    image_data, qpos_data, action_data, is_pad = image_data.cuda(), qpos_data.cuda(), action_data.cuda(), is_pad.cuda()
    return policy(qpos_data, image_data, action_data, is_pad)  # TODO remove None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval', action='store_true')
    parser.add_argument('--onscreen_render', action='store_true')
    parser.add_argument('--load_pretrain', action='store_true', default=False)
    parser.add_argument('--eval_every', action='store', type=int, default=500, help='eval_every', required=False)
    parser.add_argument('--validate_every', action='store', type=int, default=500, help='validate_every',
                        required=False)
    parser.add_argument('--save_every', action='store', type=int, default=500, help='save_every', required=False)
    parser.add_argument('--resume_ckpt_path', action='store', type=str, help='resume_ckpt_path', required=False)
    parser.add_argument('--skip_mirrored_data', action='store_true')
    parser.add_argument('--actuator_network_dir', action='store', type=str, help='actuator_network_dir', required=False)
    parser.add_argument('--history_len', action='store', type=int)
    parser.add_argument('--future_len', action='store', type=int)
    parser.add_argument('--prediction_len', action='store', type=int)
    parser.add_argument('--temporal_agg', action='store_true')
    parser.add_argument('--use_vq', action='store_true')
    parser.add_argument('--vq_class', action='store', type=int, help='vq_class')
    parser.add_argument('--vq_dim', action='store', type=int, help='vq_dim')
    parser.add_argument('--no_encoder', action='store_true')

    # for ACT
    parser.add_argument('--kl_weight', action='store', type=int, help='KL Weight', required=False,default=10)
    parser.add_argument('--chunk_size', action='store', type=int, help='chunk_size', required=False,default=100)
    parser.add_argument('--hidden_dim', action='store', type=int, help='hidden_dim', required=False,default=512)
    parser.add_argument('--dim_feedforward', action='store', type=int, help='dim_feedforward', required=False,default=3200)
    parser.add_argument('--lr', action='store', type=float, help='lr', required=False,default=1e-5 )
    parser.add_argument('--ckpt_dir', action='store', type=str, help='ckpt_dir', required=False,default='check_points')
    parser.add_argument('--policy_class', action='store', type=str, help='policy_class, capitalize', required=False,default='ACT')
    parser.add_argument('--task_name', action='store', type=str, help='task_name', required=False,default='sim_transfer_cube_scripted')
    parser.add_argument('--batch_size', action='store', type=int, help='batch_size', required=False,default=2)
    parser.add_argument('--seed', action='store', type=int, help='seed', required=False,default=0)
    parser.add_argument('--num_steps', action='store', type=int, help='num_steps', required=False,default=2000)
    main(vars(parser.parse_args()))
