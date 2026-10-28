"""Questão 11 - Cliente que solicita o deslocamento e cancela a ação após 5 segundos.

Uso: ros2 run robo_explorador robo_deslocamento_cancela LAT LON VEL_LAT VEL_LON
(sem argumentos usa 20 20 1 1, que leva mais de 5 s para concluir)
"""
import sys
import time

import rclpy
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.node import Node

from robo_interfaces.action import Deslocamento

TEMPO_CANCELAMENTO = 5.0


class DeslocamentoCancela(Node):
    def __init__(self):
        super().__init__('robo_deslocamento_cancela')
        self._client = ActionClient(self, Deslocamento, 'deslocamento')

    def feedback_cb(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(
            f'Posição atual: ({fb.latitude_atual:.3f}, {fb.longitude_atual:.3f})')

    def executar(self, lat, lon, vlat, vlon):
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

        # Processa feedbacks por 5 segundos (ou até a ação terminar antes disso)
        inicio = time.monotonic()
        while rclpy.ok() and not result_future.done() \
                and time.monotonic() - inicio < TEMPO_CANCELAMENTO:
            rclpy.spin_once(self, timeout_sec=0.1)

        if not result_future.done():
            self.get_logger().info(f'{TEMPO_CANCELAMENTO:.0f} segundos se passaram, cancelando a ação...')
            cancel_future = goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel_future)
            if len(cancel_future.result().goals_canceling) > 0:
                self.get_logger().info('Cancelamento aceito pelo robô.')
            else:
                self.get_logger().warn('Cancelamento recusado.')

        rclpy.spin_until_future_complete(self, result_future)
        res = result_future.result()

        if res.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info(
                f'Ação cancelada. Distância percorrida: {res.result.distancia_percorrida:.3f}')
        else:
            self.get_logger().info(
                f'Ação terminou (status {res.status}) antes do cancelamento. '
                f'Distância percorrida: {res.result.distancia_percorrida:.3f}')


def _ler_args():
    return [float(v) for v in sys.argv[1:5]] if len(sys.argv) >= 5 else [20.0, 20.0, 1.0, 1.0]


def main(args=None):
    rclpy.init(args=args)
    node = DeslocamentoCancela()
    node.executar(*_ler_args())
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
