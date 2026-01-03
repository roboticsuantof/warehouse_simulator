import rclpy
from rclpy.node import Node
from tf_transformations import euler_from_quaternion
# Importamos los mensajes de sensores y de navegación (Odometría)
from sensor_msgs.msg import LaserScan, Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist

class WarehouseEnvNode(Node):

    def __init__(self):
        super().__init__('warehouse_env_node')

        self.state = {}

        # Publisher de velocidades
        self.cmd_vel_pub_ = self.create_publisher(
            Twist,
            "/robot/cmd_vel",
            10
        )

        # 1. Suscripción al Lidar 2D
        self.lidar_subscription = self.create_subscription(
            LaserScan,
            '/robot/lidar2d/scan',
            self.lidar_callback,
            10
        )

        # 2. Suscripción a la IMU
        # self.imu_subscription = self.create_subscription(
        #     Imu,
        #     '/robot/imu',
        #     self.imu_callback,
        #     10
        # )

        # 3. NUEVO: Suscripción a la Odometría
        # Tópico según tu lista: /robot/odometry
        self.odom_subscription = self.create_subscription(
            Odometry,
            '/robot/odometry',
            self.odom_callback,
            10
        )

        self.get_logger().info('¡Nodo WarehouseEnvNode iniciado!')

    def lidar_callback(self, msg):
        # Leemos el punto central del láser
        self.state['lidar'] = [float(v) for v in msg.ranges]
        # distancia_frente = msg.ranges[len(msg.ranges) // 2]
        # Imprimimos solo a veces para no saturar la consola
        # self.get_logger().info(f'[LIDAR] Frente: {distancia_frente:.2f} m')

    def imu_callback(self, msg):
        # accel_x = msg.linear_acceleration.x
        self.state['imu'] = [
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ]
        # self.get_logger().info(f'[IMU] Accel X: {accel_x:.2f}')

    def odom_callback(self, msg):
        # --- NUEVA FUNCIÓN DE CALLBACK ---
        q = msg.pose.pose.orientation
        orientation_list = [q.x, q.y, q.z, q.w]
        (roll, pitch, yaw) = euler_from_quaternion(orientation_list)    
        
        self.state['odometry'] = [
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            yaw,
            msg.twist.twist.linear.x,
            msg.twist.twist.angular.z
        ]
        
        # 1. Posición (Dónde está en el mapa)
        pos_x = msg.pose.pose.position.x
        pos_y = msg.pose.pose.position.y
        
        # 2. Velocidad (Qué tan rápido se mueve)
        vel_linear = msg.twist.twist.linear.x
        vel_angular = msg.twist.twist.angular.z

        # Imprimimos la información
        # self.get_logger().info(
        #     f'[ODOM] Pos: ({pos_x:.2f}, {pos_y:.2f}) | Vel Lin: {vel_linear:.2f} m/s | Vel Ang: {vel_angular:.2f} rad/s'
        # )
    
    def send_velocity_command(self, linear=0.0, angular=0.0):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.cmd_vel_pub_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = WarehouseEnvNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()