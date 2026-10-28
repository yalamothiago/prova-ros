"""Questão 10 - Cliente que solicita o deslocamento e espera até o final.

Uso: ros2 run robo_explorador robo_deslocamento_cliente LAT LON VEL_LAT VEL_LON
(sem argumentos usa 5 5 1 1)
"""
import sys

import rclpy
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.node import Node

from robo_interfaces.action import Deslocamento


class DeslocamentoCliente(Node):
    def __init__(self):
        super().__init__('robo_deslocamento_cliente')
        self._client = ActionClient(self, Deslocamento, 'deslocamento')

    def feedback_cb(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(
            f'Posição atual: ({fb.latitude_atual:.3f}, {fb.longitude_atual:.3f})')

    def enviar_meta(self, lat, lon, vlat, vlon):
        meta = Deslocamento.Goal()
        meta.latitude = lat
        meta.longitude = lon
        meta.velocidade_latitude = vlat
        meta.velocidade_longitude = vlon

        self.get_logger().info('Aguardando servidor de deslocamento...')
        self._client.wait_for_server()
        self.get_logger().info(f'Enviando meta: ({lat}, {lon}) com velocidades ({vlat}, {vlon})')

        send_future = self._client.send_goal_async(meta, feedback_callback=self.feedback_cb)
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()

        if not goal_handle.accepted:
            self.get_logger().warn('Meta rejeitada pelo robô.')
            return

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        res = result_future.result()

        if res.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                f'Deslocamento concluído! Distância percorrida: {res.result.distancia_percorrida:.3f}')
        else:
            self.get_logger().info(
                f'Ação terminou com status {res.status}. '
                f'Distância percorrida: {res.result.distancia_percorrida:.3f}')


def _ler_args():
    valores = [float(v) for v in sys.argv[1:5]] if len(sys.argv) >= 5 else [5.0, 5.0, 1.0, 1.0]
    return valores


def main(args=None):
    rclpy.init(args=args)
    node = DeslocamentoCliente()
    node.enviar_meta(*_ler_args())
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
