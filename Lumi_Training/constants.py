import pathlib
import os

### Task parameters
DATA_DIR = '/root/datasets/synthetic_demo_data_shift1/augmented_hdf5'
SIM_TASK_CONFIGS = {
    'sim_transfer_cube_scripted':{
        'dataset_dir': DATA_DIR,
        'num_episodes': 25,
        'episode_len': 400,
        'camera_names': ['front_cam','right_cam'],
        'ckpt_dir' : "/root/datasets/check_points",
        'lr' : 1e-5,
        'chunk_size':25,
        'kl_weight':10,
        'hidden_dim': 512,
        'dim_feedforward': 3200,
        'use_vq': False,
        'action_dim': 7,
    },
}








