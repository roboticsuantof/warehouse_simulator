import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist # Importamos el mensaje de velocidad

class RobotController(Node):

    def __init__(self):
        super().__init__('robot_controller')
        
        # Creamos el Publisher
        # Tópico: /robot/cmd_vel (Según manual LACORO Sec 4.2)
        # Tipo de mensaje: Twist
        self.publisher_ = self.create_publisher(Twist, '/robot/cmd_vel', 10)
        
        # Definimos un timer para enviar comandos cada 0.5 segundos
        timer_period = 0.5  
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.get_logger().info('Nodo de Control Iniciado - ¡Cuidado con los choques!')

    def timer_callback(self):
        msg = Twist()
        
        # --- CONFIGURACIÓN DE MOVIMIENTO ---
        
        # Velocidad Lineal (Adelante/Atrás) - Eje X
        # Manual Sec 6.2: Máximo aprox 0.6 m/s
        msg.linear.x = 0.2  # Avanzamos lento para probar
        msg.linear.y = 0.0  # Un robot diferencial no se mueve lateralmente
        msg.linear.z = 0.0
        
        # Velocidad Angular (Giro) - Eje Z
        # Manual Sec 6.2: Máximo aprox 1.0 rad/s
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.1 # Giro suave a la izquierda
        
        # --- PUBLICAR ---
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publicando Vel -> Lineal: {msg.linear.x}, Angular: {msg.angular.z}')

def main(args=None):
    rclpy.init(args=args)
    node = RobotController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Es buena práctica enviar un mensaje de parada (0,0) al cerrar, 
        # pero por simplicidad aquí solo cerramos el nodo.
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()