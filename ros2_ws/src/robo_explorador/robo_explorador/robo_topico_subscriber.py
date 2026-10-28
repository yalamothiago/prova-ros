"""Questão 4 - Estação base que lê o tópico 'monitoramento' e classifica como Safe / Not Safe."""
import rclpy
from rclpy.node import Node

from robo_interfaces.msg import Monitoramento


class EstacaoBase(Node):
    def __init__(self):
        super().__init__('robo_topico_subscriber')
        self.subscription = self.create_subscription(
            Monitoramento, 'monitoramento', self.callback, 10)

    def callback(self, msg):
        seguro = 10.0 <= msg.temperatura <= 40.0 and msg.oxigenio > 80.0
        status = 'Safe' if seguro else 'Not Safe'
        self.get_logger().info(
            f'Oxigênio: {msg.oxigenio:.2f} | Temperatura: {msg.temperatura:.2f} °C -> {status}')


def main(args=None):
    rclpy.init(args=args)
    node = EstacaoBase()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
