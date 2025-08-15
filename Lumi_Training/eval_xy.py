from time import sleep

import cv2
import torch
import numpy as np
import os
import pickle
import argparse
# import matplotlib.pyplot as plt
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
#
# from constants import FPS
# from constants import PUPPET_GRIPPER_JOINT_OPEN
from utils import load_data  # data functions
from utils import sample_box_pose, sample_insertion_pose  # robot functions
from utils import compute_dict_mean, set_seed, detach_dict, calibrate_linear_vel, \
    postprocess_base_action  # helper functions
from policy import ACTPolicy, CNNMLPPolicy
# from visualize_episodes import save_videos

from detr.models.latent_model import Latent_Model_Transformer


import IPython

e = IPython.embed
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from cv_bridge import CvBridge
# from eval_interface import *
from constants import *
from std_srvs.srv import SetBool
# from example_interfaces.srv import AddTwoInts
# 窗口配置
# window_width = 1920 // 4
# window_height = 1080 // 2
camera_names = ['front_cam', 'right_cam']
# for i, name in enumerate(camera_names):
#     cv2.namedWindow(name, cv2.WINDOW_NORMAL)
#     cv2.resizeWindow(name, window_width, window_height)
#     cv2.moveWindow(name, window_width * i, 0)


class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
#        print("b1")
        self.bridge = CvBridge()
 #       print("b2")
        # 初始化图像存储变量
        self.images = {
            # 'head_cam': None,
            'right_cam': None,
           # 'left_cam': None,
            'front_cam': None
        }

        # 创建四个独立的订阅者
        # self.create_subscription(Image, '/head_camera/color/image_raw',
        #                          lambda msg: self.image_callback(msg, 'head_cam'), 10)
        self.create_subscription(Image, '/right_camera/color/image_raw',
                                 lambda msg: self.image_callback(msg, 'right_cam'), 10)
        # self.create_subscription(Image, '/left_camera/color/image_raw',
        #                          lambda msg: self.image_callback(msg, 'left_cam'), 10)
        self.create_subscription(Image, '/front_camera/color/image_raw',
                                 lambda msg: self.image_callback(msg, 'front_cam'), 10)


    def image_callback(self, msg, camera_name):
        try:
   #         print("b3")
            self.images[camera_name] = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
  #          print("b5")
        except Exception as e:
            self.get_logger().error(f"{camera_name} error: {e}")
    def clear(self):
        self.images = {
            # 'head_cam': None,
            'right_cam': None,
            # 'left_cam': None,
            'front_cam': None
        }
    def get_images(self):
        print("b4")
        return [self.images[name] for name in camera_names]


class JointStateSubscriber(Node):
    def __init__(self):
        super().__init__('joint_state_subscriber')

        # 初始化状态存储变量
        self.states = {
            # 'left_arm_pos': None,
            'right_arm_pos': None,
            # 'left_gripper_pos': None,
            'right_gripper_pos': None,
            # 'left_arm_vel': None,
            'right_arm_vel': None
        }

        # 创建六个独立的订阅者
        # self.create_subscription(JointState, '/left_arm/joint_states',
        #                          lambda msg: self.joint_callback(msg, 'left_arm_pos'), 10)
        self.create_subscription(JointState, '/right_arm/joint_states',
                                 lambda msg: self.joint_callback(msg, 'right_arm_pos'), 10)
        # self.create_subscription(JointState, '/left_gripper/current_pos',
        #                          lambda msg: self.joint_callback(msg, 'left_gripper_pos'), 10)
        self.create_subscription(JointState, '/right_gripper/current_pos',
                                 lambda msg: self.joint_callback(msg, 'right_gripper_pos'), 10)
        # self.create_subscription(JointState, '/left_arm/joint_states_vel',
        #                          lambda msg: self.joint_callback(msg, 'left_arm_vel'), 10)
        self.create_subscription(JointState, '/right_arm/joint_states_vel',
                                 lambda msg: self.joint_callback(msg, 'right_arm_vel'), 10)
    def clear(self):
        self.states = {
            # 'left_arm_pos': None,
            'right_arm_pos': None,
            # 'left_gripper_pos': None,
            'right_gripper_pos': None,
            # 'left_arm_vel': None,
            'right_arm_vel': None
        }
    def joint_callback(self, msg, state_type):
        try:
            if 'pos' in state_type:
                self.states[state_type] = msg.position[:7] if 'arm' in state_type else [msg.position[0]]
            elif 'vel' in state_type:
                self.states[state_type] = msg.velocity[:7]
        except Exception as e:
            self.get_logger().error(f"{state_type} error: {e}")

    def get_states(self):
        # 检查所有状态是否已接收
        if all(v is not None for v in self.states.values()):
            # q_pos = np.concatenate([self.states['left_arm_pos'],self.states['left_gripper_pos'],self.states['right_arm_pos'],self.states['right_gripper_pos']])
            q_pos = np.concatenate([self.states['right_arm_pos'],self.states['right_gripper_pos']])
            q_vel = np.concatenate([
                # self.states['left_arm_vel'],
                # self.states['left_gripper_pos'],  # 保持原始逻辑
                self.states['right_arm_vel'],
                self.states['right_gripper_pos']
            ])
            return q_pos, q_vel
        return None, None


class servo_move(Node):
    def __init__(self):
        super().__init__('servo_move')
        # Create a service client
        self.client = self.create_client(
            SetBool,
            'force_control_mode_enable'
        )
        self.client2 = self.create_client(
            SetBool,
            '/right_arm/servo_move_enable'
        ) 
    def send_request(self, value):
        request = SetBool.Request()
        request.data = value
        # self.client.call_async(request)  # open force control mode
        # sleep(1.2)
        self.client2.call_async(request) # enable servo mode

def get_auto_index(dataset_dir):
    max_idx = 1000
    for i in range(max_idx + 1):
        if not os.path.isfile(os.path.join(dataset_dir, f'qpos_{i}.npy')):
            return i
    raise Exception(f"Error getting auto index, or more than {max_idx} episodes")
def main(args):
    #print("1")
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
    num_episodes = task_config['num_episodes']
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

   # print("2")
    if not os.path.isdir(ckpt_dir):
        os.makedirs(ckpt_dir)
    eval_bc(config, 'policy_best.ckpt', save_episode=True, num_rollouts=10)
   # print("3")


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
def crop_and_resize_for_stereo(image):
    h, w = image.shape[:2]

    # Define fixed diagonal crop points (adjust these values as needed)

        # Top-left and bottom-right points for left camera
    x1, y1 = int(w * 0.3), int(h * 0.5)  # 10% from top-left
    x2, y2 = int(w * 0.8), int(h * 1)  # 10% from bottom-right

    # Crop the image
    cropped = image[y1:y2, x1:x2]

    # Resize back to original dimensions
    resized = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

    return resized
def get_image(images, camera_names, device='cpu'):
    curr_images = []
    for cam_name in camera_names:
        if "left" in cam_name or "right" in cam_name:
            images[cam_name] = cv2.cvtColor(images[cam_name], cv2.COLOR_RGB2BGR)
            images[cam_name] = crop_and_resize_for_stereo(images[cam_name])
            images[cam_name] = cv2.cvtColor(images[cam_name], cv2.COLOR_BGR2RGB)
        # print('推理的图像格式为（学习的时候图像格式为480*640*3）：',images[cam_name].shape)
        curr_image = rearrange(images[cam_name], 'h w c -> c h w')
        curr_images.append(curr_image)
#    cv2.imwrite("/home/check_points/left.png",images["left_cam"])
 #   cv2.imwrite("/home/check_points/right.png",images["right_cam"])
  #  cv2.imwrite("/home/check_points/front.png",images["front_cam"])
    curr_image = np.stack(curr_images, axis=0)
    curr_image = torch.from_numpy(curr_image / 255.0).float().cuda().unsqueeze(0)
    return curr_image


def wait_for_all_data(camera_sub, joint_sub):
    camera_sub.clear()
    joint_sub.clear()
    while True:
        #sleep(0.1)
        # for _ in range(20):
        rclpy.spin_once(camera_sub, timeout_sec=0.1)
        rclpy.spin_once(joint_sub, timeout_sec=0.1)
        # Get all data
        images = camera_sub.get_images()
        q_pos, q_vel = joint_sub.get_states()
        # print(images)
        print("q_vel",q_vel)
        print("q_pos",q_pos)
        print(f"图像: {'已获取' if images and all(img is not None for img in images) else '未就绪'}")
        if (q_pos is not None and
                q_vel is not None and
                all(img is not None for img in images)):
            print("所有数据已就绪!")
            return images, q_pos, q_vel
def eval_bc(config, ckpt_name, save_episode=True, num_rollouts=50):
    rclpy.init(args=None)
    camera_sub = CameraSubscriber()
    joint_sub = JointStateSubscriber()
    action_publisher = Node('action_publisher')
    servo_move_enable = servo_move()
    # 创建控制指令发布者
    # left_pub = action_publisher.create_publisher(JointState, '/left_arm/robot_command_servo_j', 10)
    right_pub = action_publisher.create_publisher(JointState, '/right_arm/robot_command_servo_j', 10)
    # left_gripper_pub = action_publisher.create_publisher(JointState, '/left_gripper/set_pos', 10)
    right_gripper_pub = action_publisher.create_publisher(JointState, '/right_gripper/set_pos', 10)
    #sleep(10)
    rclpy.spin_once(servo_move_enable, timeout_sec=1)
    servo_move_enable.send_request(True)
    print("before cam")
    #sleep(2)
    rclpy.spin_once(camera_sub, timeout_sec=0.1)
    print("after cam")
    rclpy.spin_once(joint_sub, timeout_sec=0.1)
    rclpy.spin_once(action_publisher, timeout_sec=0.1)
    set_seed(0)
    ckpt_dir = config['ckpt_dir']
    policy_class = config['policy_class']
    policy_config = config['policy_config']
    camera_names = config['camera_names']
    max_timesteps = 200
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
    # query_frequency = policy_config['num_queries']
    query_frequency = 50
    if temporal_agg:
        query_frequency = 1
        # num_queries = policy_config['num_queries']
        num_queries = 50
    max_timesteps = int(max_timesteps * 3)  # may increase for real-world tasks
    try:
        for rollout_id in range(num_rollouts):
            rollout_id += 0
            ### evaluation loop
            if temporal_agg:
                all_time_actions = torch.zeros([max_timesteps, max_timesteps + num_queries, 7]).cuda()
            with torch.inference_mode():
                for t in range(max_timesteps):
                    images, q_pos, q_vel = wait_for_all_data(
                        camera_sub,
                        joint_sub
                    )

                
                    # cv2.waitKey(1)
                    ### process previous timestep to get qpos and image_list
                    print('第',t,"轮",'######################更新OBS############################')
                    obs = {
                        'qpos': q_pos,
                        'qvel': q_vel,
                        'images': dict(zip(camera_names, images))
                    }

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
                    print(action)
                    # left_cmd = JointState()
                    # left_gripper_cmd = JointState()
                    right_gripper_cmd = JointState()
                    # left_cmd.position = action[:7].tolist()
                    # left_gripper_cmd.position = [float(action[7])]
                    # right_gripper_cmd.position = [float(action[15])]
                    # left_gripper_cmd.position = [action[7]]
                    right_gripper_cmd.position = [action[6]]
                    right_cmd = JointState()
                    right_cmd.position = action[:6].tolist()
                    # left_gripper_pub.publish(left_gripper_cmd)
                    right_gripper_pub.publish(right_gripper_cmd)
                    # left_pub.publish(left_cmd)
                    right_pub.publish(right_cmd)
                    sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        servo_move_enable.send_request(False)
        # cv2.destroyAllWindows()
        camera_sub.destroy_node()
        joint_sub.destroy_node()
        action_publisher.destroy_node()
        rclpy.shutdown()


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
    parser.add_argument('--chunk_size', action='store', type=int, help='chunk_size', required=False,default=50)
    parser.add_argument('--hidden_dim', action='store', type=int, help='hidden_dim', required=False,default=512)
    parser.add_argument('--dim_feedforward', action='store', type=int, help='dim_feedforward', required=False,default=3200)
    parser.add_argument('--lr', action='store', type=float, help='lr', required=False,default=1e-5 )
    parser.add_argument('--ckpt_dir', action='store', type=str, help='ckpt_dir', required=False,default='/root/datasets/check_points/')
    parser.add_argument('--policy_class', action='store', type=str, help='policy_class, capitalize', required=False,default='ACT')
    parser.add_argument('--task_name', action='store', type=str, help='task_name', required=False,default='sim_transfer_cube_scripted')
    parser.add_argument('--batch_size', action='store', type=int, help='batch_size', required=False,default=2)
    parser.add_argument('--seed', action='store', type=int, help='seed', required=False,default=0)
    parser.add_argument('--num_steps', action='store', type=int, help='num_steps', required=False,default=2000)
    main(vars(parser.parse_args()))
