"""Questão 6 - Cliente que requisita o serviço 'coleta_material' com profundidade aleatória."""
import random

import rclpy
from rclpy.node import Node

from robo_interfaces.srv import ColetaMaterial


class ColetaCliente(Node):
    def __init__(self):
        super().__init__('robo_coleta_cliente')
        self.cliente = self.create_client(ColetaMaterial, 'coleta_material')
        while not self.cliente.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Aguardando o serviço coleta_material...')

    def enviar_requisicao(self):
        req = ColetaMaterial.Request()
        req.profundidade = random.uniform(0.1, 0.5)
        self.get_logger().info(f'Solicitando coleta na profundidade {req.profundidade:.3f}')
        return self.cliente.call_async(req)


def main(args=None):
    rclpy.init(args=args)
    node = ColetaCliente()
    future = node.enviar_requisicao()
    rclpy.spin_until_future_complete(node, future)

    resposta = future.result()
    if resposta is None:
        node.get_logger().error('Falha ao chamar o serviço')
    elif resposta.sucesso:
        node.get_logger().info('Coleta bem sucedida!')
    else:
        node.get_logger().info('Coleta NÃO foi bem sucedida.')

    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
