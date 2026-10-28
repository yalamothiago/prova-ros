# Robô Explorador — 1ª Avaliação Prática (Tópicos Especiais em Redes de Computadores 2026.2)

Alunos: Yalamo Thiago de Araújo Souza e Vitória Eloise de Assis Rocha

Workspace ROS 2 (testado para Humble/Jazzy) com dois pacotes:

| Pacote | Build type | Conteúdo |
|---|---|---|
| `robo_interfaces` | `ament_cmake` (C++) | `msg/Monitoramento.msg`, `srv/ColetaMaterial.srv`, `action/Deslocamento.action` |
| `robo_explorador` | `ament_python` | os 7 nós Python |

```
ros2_ws/
└── src/
    ├── robo_interfaces/
    │   ├── action/Deslocamento.action
    │   ├── msg/Monitoramento.msg
    │   ├── srv/ColetaMaterial.srv
    │   ├── CMakeLists.txt
    │   └── package.xml
    └── robo_explorador/
        ├── robo_explorador/
        │   ├── robo_topico_publish.py
        │   ├── robo_topico_subscriber.py
        │   ├── robo_coleta_cliente.py
        │   ├── robo_coleta_servidor.py
        │   ├── robo_deslocamento_servidor.py
        │   ├── robo_deslocamento_cliente.py
        │   └── robo_deslocamento_cancela.py
        ├── package.xml
        ├── setup.cfg
        └── setup.py
```

> Em todo terminal novo: `source /opt/ros/<distro>/setup.bash` e, depois do build, `source ~/ros2_ws/install/setup.bash`.

---

## Questão 1 — Criação dos pacotes

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake robo_interfaces
ros2 pkg create --build-type ament_python robo_explorador --dependencies rclpy robo_interfaces
```

Depois de criar, substitua/adicione os arquivos deste repositório e compile:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## Questão 2 — Interface do tópico

`robo_interfaces/msg/Monitoramento.msg`

```
float64 oxigenio
float64 temperatura
```

Verificação:

```bash
ros2 interface show robo_interfaces/msg/Monitoramento
```

## Questão 3 — Publisher (robô)

Publica no tópico `monitoramento`, a cada 1 s, oxigênio e temperatura aleatórios entre 1 e 100.

```bash
ros2 run robo_explorador robo_topico_publish
```

Opcional (outro terminal): `ros2 topic echo /monitoramento`

## Questão 4 — Subscriber (estação base)

Imprime **Safe** se 10 ≤ temperatura ≤ 40 **e** oxigênio > 80; caso contrário **Not Safe**.

```bash
# terminal 1
ros2 run robo_explorador robo_topico_publish
# terminal 2
ros2 run robo_explorador robo_topico_subscriber
```

## Questão 5 — Interface do serviço

`robo_interfaces/srv/ColetaMaterial.srv`

```
float64 profundidade
---
bool sucesso
```

```bash
ros2 interface show robo_interfaces/srv/ColetaMaterial
```

## Questão 6 — Cliente do serviço `coleta_material`

Envia profundidade aleatória entre 0,1 e 0,5 e informa se a coleta foi bem sucedida.

```bash
ros2 run robo_explorador robo_coleta_cliente
```

## Questão 7 — Servidor do serviço `coleta_material`

Sorteia um número entre 0 e 1; retorna `true` se ≤ 0,7 (70% de chance).

```bash
# terminal 1
ros2 run robo_explorador robo_coleta_servidor
# terminal 2 (rode algumas vezes para ver sucessos e falhas)
ros2 run robo_explorador robo_coleta_cliente
```

## Questão 8 — Interface da action

`robo_interfaces/action/Deslocamento.action`

```
# meta
float64 latitude
float64 longitude
float64 velocidade_latitude
float64 velocidade_longitude
---
# resultado
float64 distancia_percorrida
---
# feedback
float64 latitude_atual
float64 longitude_atual
```

```bash
ros2 interface show robo_interfaces/action/Deslocamento
```

## Questão 9 — Servidor da action `deslocamento` (robô)

- Posição inicial do robô: (0, 0). A posição é mantida entre metas.
- **Rejeita** a meta se o destino for igual à posição atual (ou se alguma velocidade for ≤ 0); aceita caso contrário.
- A cada 1 s avança `velocidade_latitude` em latitude e `velocidade_longitude` em longitude (sem ultrapassar o destino), publica o feedback com a posição atual e acumula a distância euclidiana percorrida.
- Ao chegar, retorna `distancia_percorrida`. Se cancelado, retorna a distância percorrida até o cancelamento.
- Usa `MultiThreadedExecutor` + `ReentrantCallbackGroup` para conseguir processar o cancelamento enquanto a ação executa.

```bash
ros2 run robo_explorador robo_deslocamento_servidor
```

## Questão 10 — Cliente que espera até o fim

```bash
# terminal 1
ros2 run robo_explorador robo_deslocamento_servidor
# terminal 2  (argumentos: LAT LON VEL_LAT VEL_LON — padrão 5 5 1 1)
ros2 run robo_explorador robo_deslocamento_cliente 5 3 1 1
```

Saída esperada no final (partindo de (0,0)): `Distância percorrida: 6.243`.

Teste da rejeição: rode o mesmo comando de novo — o robô já está em (5, 3), então a meta é rejeitada.

Alternativa pela CLI:

```bash
ros2 action send_goal --feedback /deslocamento robo_interfaces/action/Deslocamento \
  "{latitude: 5.0, longitude: 3.0, velocidade_latitude: 1.0, velocidade_longitude: 1.0}"
```

## Questão 11 — Cliente que cancela após 5 s

```bash
# terminal 1
ros2 run robo_explorador robo_deslocamento_servidor
# terminal 2  (padrão 20 20 1 1, que leva mais de 5 s)
ros2 run robo_explorador robo_deslocamento_cancela
```

Após ~5 feedbacks o cliente cancela e mostra a distância percorrida até ali (partindo de (0,0), cada passo anda √2 ≈ 1.414, então algo como 7.07 ou 8.49, dependendo de o cancelamento chegar antes ou depois do 6º passo).

> Dica: reinicie o servidor entre a Q10 e a Q11 se quiser que o robô parta de (0, 0).
