import gymnasium as gym
from gymnasium import spaces
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math

class WarehouseEnv(gym.Env):
    def __init__(self):
        super(WarehouseEnv, self).__init__()

        # 1. Iniciar Nodo ROS interno
        if not rclpy.ok():
            rclpy.init()
        self.node = rclpy.create_node('rl_gym_bridge')

        # 2. Configurar Publisher (Acción) y Subscribers (Observación)
        self.pub_cmd_vel = self.node.create_publisher(Twist, '/robot/cmd_vel', 10)
        self.sub_scan = self.node.create_subscription(LaserScan, '/robot/lidar2d/scan', self.scan_callback, 10)
        self.sub_odom = self.node.create_subscription(Odometry, '/robot/odometry', self.odom_callback, 10)

        # Variables para guardar la última lectura
        self.scan_data = np.zeros(10) # Placeholder inicial
        self.current_pos = (0.0, 0.0)

        # 3. Definir Espacios (Manual Sec 7.1 y 7.2)
        # Acción Continua: [Velocidad Lineal (0 a 0.6), Velocidad Angular (-1.0 a 1.0)]
        self.action_space = spaces.Box(
            low=np.array([0.0, -1.0]), 
            high=np.array([0.6, 1.0]), 
            dtype=np.float32
        )
        
        # Observación: Ejemplo simple (10 rayos lidar + Distancia al objetivo)
        self.observation_space = spaces.Box(
            low=0.0, 
            high=10.0, 
            shape=(11,), 
            dtype=np.float32
        )

    def scan_callback(self, msg):
        # Simplificamos el lidar a 10 lecturas representativas
        # (El lidar real tiene cientos, aquí reducimos la resolución para la IA)
        ranges = np.array(msg.ranges)
        # Reemplazar infinitos con distancia max (10m)
        ranges = np.where(np.isinf(ranges), 10.0, ranges)
        # Tomar 10 muestras equidistantes
        step = len(ranges) // 10
        self.scan_data = ranges[::step][:10]

    def odom_callback(self, msg):
        self.current_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)

    def step(self, action):
        # A. Ejecutar Acción
        twist = Twist()
        twist.linear.x = float(action[0])
        twist.angular.z = float(action[1])
        self.pub_cmd_vel.publish(twist)

        # B. Esperar y actualizar sensores (Spin breve)
        rclpy.spin_once(self.node, timeout_sec=0.1)

        # C. Construir Observación
        # Aqui deberias calcular la distancia real a la meta. 
        # Por ahora simulamos una distancia dummy de 5.0m
        dist_to_goal = 5.0 
        obs = np.concatenate((self.scan_data, [dist_to_goal])).astype(np.float32)

        # D. Calcular Recompensa (Reward Shaping - Manual Sec 7.4)
        reward = 0.1 # Recompensa pequeña por sobrevivir
        
        # E. Verificar Choque
        min_dist = np.min(self.scan_data)
        terminated = False
        if min_dist < 0.3: # Si está muy cerca de algo
            reward = -100.0 # Castigo fuerte
            terminated = True # Fin del episodio

        return obs, reward, terminated, False, {}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Aquí deberías resetear la posición del robot si fuera posible
        # O simplemente detenerlo:
        stop_msg = Twist()
        self.pub_cmd_vel.publish(stop_msg)
        rclpy.spin_once(self.node, timeout_sec=0.1)
        
        # Retornar observación inicial
        dist_to_goal = 5.0
        obs = np.concatenate((self.scan_data, [dist_to_goal])).astype(np.float32)
        if len(obs) != 11: obs = np.zeros(11, dtype=np.float32) # Fallback por seguridad
        return obs, {}