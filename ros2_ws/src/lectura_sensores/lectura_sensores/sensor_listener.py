import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile

# Imports de Mensajes de Sensores
from sensor_msgs.msg import LaserScan, Imu
from nav_msgs.msg import Odometry

# Imports de Mensajes de Geometría (Para Goal e Initial Pose)
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped

class WarehouseListener(Node):

    def __init__(self):
        super().__init__('warehouse_listener')
        
        # Configuración de Calidad de Servicio (QoS) estándar
        qos = QoSProfile(depth=10)

        # --- 1. VARIABLES LOCALES (Memoria del Robot) ---
        # Aquí se guardarán los datos. Inicializamos con None o valores por defecto.
        self.current_goal = None
        self.initial_pose = None

        # --- 2. SUSCRIPTORES DE SENSORES (Imprimen en terminal) ---
        
        # Lidar 2D (/robot/lidar2d/scan)
        self.lidar_sub = self.create_subscription(
            LaserScan, 
            '/robot/lidar2d/scan', 
            self.lidar_callback, 
            qos)

        # IMU (/robot/imu)
        self.imu_sub = self.create_subscription(
            Imu, 
            '/robot/imu', 
            self.imu_callback, 
            qos)

        # Odometría (/robot/odometry)
        self.odom_sub = self.create_subscription(
            Odometry, 
            '/robot/odometry', 
            self.odom_callback, 
            qos)

        # --- 3. SUSCRIPTORES DE CONFIGURACIÓN (Guardar en variable, sin spam) ---
        
        # Escuchar Meta (/goal_pose) - Típico si usas RViz para marcar destino
        self.goal_sub = self.create_subscription(
            PoseStamped, 
            '/goal_pose', 
            self.goal_callback, 
            qos)

        # Escuchar Posición Inicial (/initialpose)
        self.initial_sub = self.create_subscription(
            PoseWithCovarianceStamped, 
            '/initialpose', 
            self.initial_callback, 
            qos)

        self.get_logger().info('--- NODO LISTO: Imprimiendo sensores y guardando poses en memoria ---')

    # --- CALLBACKS QUE IMPRIMEN (LOGGING) ---

    def lidar_callback(self, msg):
        # Tomamos la distancia justo al frente (índice central)
        distancia_centro = msg.ranges[len(msg.ranges) // 2]
        # Imprimimos en terminal
        self.get_logger().info(f'[LIDAR] Obstáculo frontal a: {distancia_centro:.2f} m')

    def imu_callback(self, msg):
        accel_x = msg.linear_acceleration.x
        accel_y = msg.linear_acceleration.y
        # Imprimimos datos de aceleración
        self.get_logger().info(f'[IMU] Accel: X={accel_x:.2f}, Y={accel_y:.2f}')

    def odom_callback(self, msg):
        pos_x = msg.pose.pose.position.x
        pos_y = msg.pose.pose.position.y
        vel_x = msg.twist.twist.linear.x
        vel_z = msg.twist.twist.angular.z
        
        self.get_logger().info(
            f'[ODOM] Pos: ({pos_x:.2f}, {pos_y:.2f}) | Vel: Lin={vel_x:.2f}, Ang={vel_z:.2f}'
        )

    # --- CALLBACKS SILENCIOSOS (GUARDAR EN VARIABLE) ---

    def goal_callback(self, msg):
        # Solo guardamos el dato en la variable local self.current_goal
        self.current_goal = msg
        # Opcional: Avisar SOLO UNA VEZ cuando cambia, no constantemente
        self.get_logger().info(f'>>> NUEVA META RECIBIDA Y GUARDADA: X={msg.pose.position.x:.2f}')

    def initial_callback(self, msg):
        # Solo guardamos el dato en la variable local self.initial_pose
        self.initial_pose = msg
        self.get_logger().info(f'>>> POSICIÓN INICIAL RECIBIDA Y GUARDADA: X={msg.pose.pose.position.x:.2f}')

def main(args=None):
    rclpy.init(args=args)
    node = WarehouseListener()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()