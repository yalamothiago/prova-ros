"""Questão 7 - Robô que atende o serviço 'coleta_material' (sucesso com 70% de probabilidade)."""
import random

import rclpy
from rclpy.node import Node

from robo_interfaces.srv import ColetaMaterial


class ColetaServidor(Node):
    def __init__(self):
        super().__init__('robo_coleta_servidor')
        self.servico = self.create_service(ColetaMaterial, 'coleta_material', self.coletar)
        self.get_logger().info('Serviço coleta_material pronto.')

    def coletar(self, request, response):
        sorteio = random.random()  # número entre 0 e 1
        response.sucesso = sorteio <= 0.7
        self.get_logger().info(
            f'Coleta na profundidade {request.profundidade:.3f} | '
            f'sorteio = {sorteio:.3f} -> sucesso = {response.sucesso}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = ColetaServidor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
