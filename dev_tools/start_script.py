import sys

import json
import threading
import urllib.parse
import websocket
from module.logger import logger


def start_websocket(config_name, command: str = "start"):
    logger.info(f"[{config_name}] 尝试连接到WebSocket")
    config_name = urllib.parse.quote(config_name)
    url = f"ws://127.0.0.1:22288/ws/{config_name}"
    logger.info(f"[{config_name}] WebSocket URL: {url}")
    ws = websocket.WebSocketApp(url)

    # 处理 WebSocket 连接打开事件
    def on_open(ws):
        logger.info(f"[{config_name}] WebSocket连接成功!")
        ws.send(command)
        logger.info(f"[{config_name}] 已发送: {command}")

    # 处理接收到的消息
    def on_message(ws, response):
        print(f"收到响应: {response}")

        if 'schedule' in response:
            data = json.loads(response)
            schedule = data['schedule']
            if 'running' in schedule and schedule['running']:
                running_task = schedule['running']
                logger.info(f"[{config_name}] 当前运行任务: {running_task['name']}")
            else:
                logger.info(f"[{config_name}] 当前无运行任务")
        if 'state' in response:
            data = json.loads(response)
            state = data['state']
            if state == 1:
                logger.info(f"[{config_name}] 当前运行中")
            elif state == 0:
                logger.info(f"[{config_name}] 当前已停止")

    # 设置 WebSocket 回调函数
    ws.on_open = on_open
    ws.on_message = on_message

    # 设置超时退出
    def exit_timer():
        logger.info(f"[{config_name}] 超时关闭连接...")
        ws.close()
        sys.exit(0)

    timer = threading.Timer(5, exit_timer)  # 5秒后自动关闭
    timer.start()

    ws.run_forever()
    timer.cancel()  # 如果连接正常关闭，取消定时器


if __name__ == "__main__":
    # 保证通过命令行运行时传入参数，例如：python script.py MI

    config_name = sys.argv[1]
    # config_name = "DU"
    # command = "get_state"
    # command = "get_schedule"
    command = "start"
    # command = "stop"
    logger.info(f'[{config_name}] 开始启动...')
    start_websocket(config_name, command)