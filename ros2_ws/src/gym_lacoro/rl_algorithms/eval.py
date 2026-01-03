import gymnasium as gym
from typing import Callable, Tuple
import time
import numpy as np
import sys
from gym_lacoro.envs.warehouse_env import WarehouseEnvContinuous
from gym_lacoro.utils import load_yaml
# from stable_baselines3 import TD3
# from stable_baselines3.td3.policies import TD3Policy, CnnPolicy, MultiInputPolicy

from stable_baselines3 import PPO
from stable_baselines3.ppo.policies import CnnPolicy, MultiInputPolicy


def evaluate_agent(agent_select_action: Callable,
                   env: gym.Env,
                   n_episodes: int,
                   n_steps: int,
                   init_pos: Tuple[float, float, float],
                   goal_pos: Tuple[float, float]):
    steps = []
    rewards = []
    times = []

    for i in range(n_episodes):
        timemark = time.time()
        state, info = env.reset(options={
            "init_pos": init_pos,
            "goal_pose": goal_pos
            })
        print("info", info)
        ep_reward = 0
        ep_steps = 0
        end = False

        while not end:
            action = agent_select_action(state)
            next_state, reward, done, truncated, info = env.step(action)
            end = done or truncated
            ep_steps += 1
            ep_reward += reward
            state = next_state
            prefix = f"Run {i+1:02d}/{n_episodes:02d}"
            sys.stdout.write(f"\r{prefix} | Reward: {ep_reward:.4f} | "
                             f"Length: {ep_steps}  ")
            if ep_steps == n_steps or truncated:
                end = True

        elapsed_time = time.time() - timemark

        steps.append(ep_steps)
        rewards.append(ep_reward)
        times.append(elapsed_time)

    ttime = np.sum(times).round(3)
    tsteps = np.mean(steps)
    treward = np.mean(rewards).round(4)
    sys.stdout.write(f"\r- Evaluated in {ttime:.3f} seconds | "
                     f"Initial Pose {init_pos} | "
                     f"Goal Position {goal_pos} | "
                     f"Mean reward: {treward:.4f} | "
                     f"Mean lenght: {tsteps}\n")
    sys.stdout.flush()

    return ep_reward, ep_steps, elapsed_time




def action_selection(observations):
    if type(observations) is dict:
        for k in observations.keys():
            observations[k] = np.array(observations[k], dtype=np.float32)
            if observations[k].shape[0] != 1:
                observations[k] = observations[k][np.newaxis, ...]
    else:
        observations = np.array(observations, dtype=np.float32)
        if observations.shape[0] != 1:
            observations = observations[np.newaxis, ...]
    # print("observations", observations)
    actions, states = model.predict(
        observations,  # type: ignore[arg-type]
        state=None,
        episode_start=None,
        deterministic=True,
    )
    # print("actions", actions)
    return actions[0]


# eval_args = parse_args()
# saved_args = load_json_dict(eval_args.logspath + '/arguments.json')
# env_params = args2env_params(saved_args)

# Environment
env = WarehouseEnvContinuous()

# Algorithm
algorithm, policy = PPO, MultiInputPolicy
policy_args = None

# Evaluation loop

agent_path = "/home/kishouandrea/lacoro-reto/ros2_ws/src/gym_lacoro/rl_algorithms/models/PPO/warehouse_final"
model = algorithm.load(agent_path)

# --- EJEMPLO DE USO ---
# Asumiendo que el archivo está en una carpeta 'config'
ruta = '/home/kishouandrea/lacoro-reto/ros2_ws/src/warehouse_simulator/resources/points_training.yaml' 
datos_mision = load_yaml(ruta)

for mission in datos_mision["scenarios"]:
    print("EValuando mission", mission["name"])
    # Ejemplo: Si el yaml tiene una lista de goals, podrías acceder así:
    # print(datos_mision['goals'][0])
    evaluate_agent(action_selection, env, 1, 300, mission["start"], mission["goal"])
    break

env.close()
