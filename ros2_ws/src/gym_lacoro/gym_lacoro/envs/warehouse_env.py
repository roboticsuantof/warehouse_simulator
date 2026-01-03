from typing import Optional
import gymnasium as gym
import rclpy
import numpy as np
from gym_lacoro.warehouse_env_node import WarehouseEnvNode
from gym_lacoro.utils import load_yaml

class WarehouseEnvContinuous(gym.Env):

    def __init__(self,
        max_speed_lin: float = 0.6,  #  meters / sec
        max_speed_ang: float = 1.0,  #  radians / sec
        step_time: float = 0.1,
        points_path: Optional[str] = None
        ):
        self.max_speed_lin = max_speed_lin  #  v = meters / sec
        self.max_speed_ang = max_speed_ang  #  omega = radians / sec
        self.step_time = step_time

        if points_path is not None:
            self.missions = load_yaml(points_path)["scenarios"]
            self.mission_idx = -1
            self.mission_total = len(self.missions)

        self.init_pos = np.array([0., 0., 0.])
        self.goal_pos = np.array([0., 0.])
        self.current_goal_pos = self.init_pos
        self.is_towards_goal = False

        # Acción Continua: [Velocidad Lineal (0 a 0.6), Velocidad Angular (-1.0 a 1.0)]
        self.action_space = gym.spaces.Box(
            low=np.array([0.0, -max_speed_ang]), 
            high=np.array([max_speed_lin, max_speed_ang]), 
            dtype=np.float32
        )
        
        # Define what the agent can observe
        self.observation_space = gym.spaces.Dict(
            {
                "odometry": gym.spaces.Box(0, float("inf"), shape=(2,), dtype=np.float32),   # [x, y] coordinates
                # "imu": gym.spaces.Box(0, float("inf"), shape=(3,), dtype=np.float32),  # [x, y] coordinates
                # "lidar": gym.spaces.Box(0, float("inf"), shape=(920,), dtype=np.float32),  # [x, y] coordinates
                "target": gym.spaces.Box(0, float("inf"), shape=(1,), dtype=np.float32),  # [x, y] coordinates
            }
        )

        # ROS
        # 1. Iniciar Nodo ROS interno
        if not rclpy.ok():
            rclpy.init()
        self.node = WarehouseEnvNode()
    
    def get_next_mission(self):
        self.mission_idx += 1
        self.mission_idx = self.mission_idx % self.mission_total
        return self.missions[self.mission_idx]

    def _get_node_state(self):
        odometry = np.zeros((5,))
        imu = np.zeros((3, ))
        lidar = np.zeros((920,))
        # target = np.zeros((1,))

        if 'odometry' in self.node.state.keys():
            odometry = np.array(self.node.state['odometry'])
        
        # if 'imu' in self.node.state.keys():
        #     imu = np.array(self.node.state['imu'])
        
        if 'lidar' in self.node.state.keys():
            lidar = np.array(self.node.state['lidar'])
            lidar = np.clip(lidar, 0.5, 10.)
            lidar /= 10.

        return {
            "odometry": odometry,
            "imu": imu,
            "lidar": lidar,
            # "target": target,
            }


    def _get_obs(self):
        """Convert internal state to observation format.

        Returns:
            dict: Observation with agent and target positions
        """

        state = self._get_node_state()
        target = np.array([self.get_goal_distance()])

        return {
            "odometry": state['odometry'][-2:],
            # "imu": imu,
            # "lidar": lidar,
            "target": target,
            }

    def _get_info(self, obs):
        """Compute auxiliary information for debugging.

        Returns:
            dict: Info with distance between agent and target
        """
        return {
            "distance": self.get_goal_distance()
        }
    
    def perform_action(self, action):
        # manda accion y spin
        self.node.send_velocity_command(action[0], action[1])
        rclpy.spin_once(self.node, timeout_sec=self.step_time)

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        """Start a new episode.

        Args:
            seed: Random seed for reproducible episodes
            options: Additional configuration (unused in this example)

        Returns:
            tuple: (observation, info) for the initial state
        """
        # IMPORTANT: Must call this first to seed the random number generator
        super().reset(seed=seed)
        rclpy.spin_once(self.node, timeout_sec=self.step_time)
        self.prev_distance = 0

        # stop action
        self.perform_action([0, 0])

        # options for start point
        if options is not None:
            if "init_pos" in options.keys():
                self.init_pos = options['init_pos']
            
            if "goal_pos" in options.keys():
                self.goal_pos = options['goal_pos']
        else:
            mission = self.get_next_mission()
            print("Mission name:", mission["name"])
            self.init_pos = mission["start"]
            self.goal_pos = mission["goal"]
        
        self.current_goal_pos = self.init_pos[:2]
        self.is_towards_goal = False

        observation = self._get_obs()
        info = self._get_info(observation)

        return observation, info
    
    def get_current_pos(self):
        return self._get_node_state()['odometry'][:2]
    
    def get_goal_distance(self):
        current_pos = self.get_current_pos()
        return np.linalg.norm(current_pos - self.current_goal_pos)

    def compute_reward(self, obs):
        """
        The challenge does not impose a fixed reward function, but typical components may include:
        - Positive reward for reaching pickup or delivery points.
        - Negative reward for collisions (especially with actors).
        - Penalties for large deviations from the shortest path.
        - Time penalty to encourage efficient trajectories.
        - Optional: Safety margin rewards for maintaining a safe distance to actors.
        """
        terminated, truncated = False, False

        distance = self.get_goal_distance()

        vel_comp = ((self.prev_distance - distance) / self.step_time)# - (self.max_speed_lin * self.step_time)
        dist_comp = distance * 0.01
        #print("reward vel:", vel_comp)#, "dist:", dist_comp)

        reward = vel_comp - dist_comp

        if distance <= 0.3:
            if not self.is_towards_goal:
                print("switching to goal_pos")
                self.current_goal_pos = self.goal_pos
                self.is_towards_goal = True
                reward = 5
            else:
                print("Goal reached!")
                truncated = True
                reward = 10

        if distance > 40:
            print("EP end too much distance:", distance)
            terminated = True
            reward = -10

        return reward, terminated, truncated
        
    def check_terminal_state(self):
        """
        7.3 Episode Termination Conditions.
        An episode terminates when any of the following occurs:
            - The robot completes the predefined number of deliveries.
            - A collision with a human actor occurs (episode is invalid for scoring).
            - Optional: The robot is detected as “stuck” (no progress after a certain time).
        return terminated, truncated
        """
        return False, False

    def check_tolerance(self):
        """
        7.5 Tolerance Objective
        The tolerance thresholds that must be considered for evaluating the agent’s behavior in the environment are:
        - Distance to obstacles: 0.5 m. Any distance smaller than this value is considered a collision.
        - Distance to actors: 0.7 m. Any distance smaller than this value is considered an incident.
        - Distance to goal: 0.3 m. A distance greater than this value is considered as not having reached the goal.
        """
        pass

    def step(self, action):
        """Execute one timestep within the environment.

        Args:
            action: The action to take (0-3 for directions)

        Returns:
            tuple: (observation, reward, terminated, truncated, info)
        """

        obs = self._get_obs()
        self.prev_distance = self.get_goal_distance()

        self.perform_action(action)

        observation = self._get_obs()
        info = self._get_info(observation)

        reward, terminated, truncated = self.compute_reward(observation)

        # Check if agent reached the target
        # terminated, truncated = self.check_terminal_state()

        return observation, reward, terminated, truncated, info
    
    def close(self):
        self.perform_action([0, 0])
