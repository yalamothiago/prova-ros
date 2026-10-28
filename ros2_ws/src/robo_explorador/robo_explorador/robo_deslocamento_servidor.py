"""Questão 9 - Servidor da action 'deslocamento' (o robô).

- Aceita a meta apenas se o destino for diferente da localização atual.
- A cada 1 segundo avança segundo as velocidades e publica o feedback (localização atual).
- Ao chegar (ou ao ser cancelado) retorna a distância percorrida.
"""
import math
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from robo_interfaces.action import Deslocamento


class DeslocamentoServidor(Node):
    def __init__(self):
        super().__init__('robo_deslocamento_servidor')
        self.latitude = 0.0
        self.longitude = 0.0
        self._action_server = ActionServer(
            self,
            Deslocamento,
            'deslocamento',
            execute_callback=self.executar,
            goal_callback=self.receber_meta,
            cancel_callback=self.receber_cancelamento,
            callback_group=ReentrantCallbackGroup(),
        )
        self.get_logger().info(
            f'Servidor de deslocamento pronto. Posição inicial: ({self.latitude}, {self.longitude})')

    def receber_meta(self, goal):
        if math.isclose(goal.latitude, self.latitude) and math.isclose(goal.longitude, self.longitude):
            self.get_logger().warn('Meta rejeitada: destino igual à localização atual.')
            return GoalResponse.REJECT
        if goal.velocidade_latitude <= 0.0 or goal.velocidade_longitude <= 0.0:
            self.get_logger().warn('Meta rejeitada: velocidades devem ser positivas.')
            return GoalResponse.REJECT
        self.get_logger().info(f'Meta aceita: ir para ({goal.latitude}, {goal.longitude})')
        return GoalResponse.ACCEPT

    def receber_cancelamento(self, goal_handle):
        self.get_logger().info('Pedido de cancelamento recebido.')
        return CancelResponse.ACCEPT

    @staticmethod
    def _passo(atual, destino, velocidade):
        """Avança no máximo 'velocidade' unidades em direção ao destino (sem ultrapassar)."""
        diferenca = destino - atual
        if abs(diferenca) <= velocidade:
            return destino
        return atual + math.copysign(velocidade, diferenca)

    def executar(self, goal_handle):
        meta = goal_handle.request
        distancia = 0.0
        feedback = Deslocamento.Feedback()
        resultado = Deslocamento.Result()

        while (self.latitude, self.longitude) != (meta.latitude, meta.longitude):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                resultado.distancia_percorrida = distancia
                self.get_logger().info(f'Ação cancelada. Distância percorrida: {distancia:.3f}')
                return resultado

            time.sleep(1.0)  # 1 segundo de deslocamento

            nova_lat = self._passo(self.latitude, meta.latitude, meta.velocidade_latitude)
            nova_lon = self._passo(self.longitude, meta.longitude, meta.velocidade_longitude)
            distancia += math.hypot(nova_lat - self.latitude, nova_lon - self.longitude)
            self.latitude, self.longitude = nova_lat, nova_lon

            feedback.latitude_atual = self.latitude
            feedback.longitude_atual = self.longitude
            goal_handle.publish_feedback(feedback)
            self.get_logger().info(
                f'Feedback -> posição atual: ({self.latitude:.3f}, {self.longitude:.3f})')

        goal_handle.succeed()
        resultado.distancia_percorrida = distancia
        self.get_logger().info(f'Destino alcançado. Distância percorrida: {distancia:.3f}')
        return resultado


def main(args=None):
    rclpy.init(args=args)
    node = DeslocamentoServidor()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
