import asyncio
import json

import websockets

from geodrive import AsyncRover
from geodrive.logging import get_logger
from .app import WebApp

logger = get_logger("ws-control")


class WebSocketServer:
    """WebSocket сервер для управления роботом"""

    def __init__(self, rover_number: int, local: bool, arena: int, video: bool):
        self.rover_number = rover_number
        self.local = local
        self.arena = arena
        self.video = video
        self.rover = None
        self.web_app = WebApp(video)

    async def connect_to_rover(self) -> bool:
        """Подключение к роверу"""
        if self.local:
            rover_ip = "localhost"
            logger.info("Подключение к локальному gRPC серверу")
        else:
            rover_ip = f"10.1.100.{self.rover_number}"

        self.rover = AsyncRover(rover_ip)

        if not await self.rover.connect():
            logger.error("Не удалось подключиться к роверу")
            return False

        logger.info("Успешное подключение к роверу")
        return True

    async def send_telemetry_data(self, websocket):
        """Отправка телеметрии через WebSocket"""
        while True:
            try:
                async for telemetry in self.rover.stream_telemetry():
                    battery_data = await self.rover.get_battery_status()
                    robot_data = {
                        "type": "telemetry",
                        "posX": telemetry.position[0],
                        "posY": telemetry.position[1],
                        "velX": telemetry.velocity[0],
                        "velY": telemetry.velocity[1],
                        "yaw": telemetry.attitude[2],
                        "battery": battery_data.percentage
                    }

                    await websocket.send(json.dumps(robot_data))
                    await asyncio.sleep(0.02)

            except Exception as e:
                logger.error(f"Ошибка при отправке телеметрии: {e}")
                break

    async def handle_rc_commands(self, websocket, rc_control):
        """Обработка RC команд"""
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type", "rc_channels") == "navigate_to_point":
                    await asyncio.create_task(
                        self.rover.goto(data.get("target_x"), data.get("target_y"))
                    )
                else:
                    rc_control.channel1 = data.get('channel1', 1500)
                    rc_control.channel2 = data.get('channel2', 1500)
                    rc_control.channel3 = data.get('channel3', 1500)
                    rc_control.channel4 = data.get('channel4', 1500)

                    if rc_control.channel2 == 1000:
                        await self.rover.moo()
                    if rc_control.channel4 == 1000:
                        await self.rover.beep()

                    logger.debug(f"RC каналы: {data}")

            except json.JSONDecodeError:
                logger.warning(f"Невалидный JSON: {message}")
            except Exception as e:
                logger.error(f"Ошибка обработки RC команды: {e}")

    async def handle_direct_commands(self, websocket):
        """Обработка прямых команд (без RC)"""
        async for message in websocket:
            try:
                data = json.loads(message)
                command_type = data.get("type")

                if command_type == "navigate_to_point":
                    await asyncio.create_task(
                        self.rover.goto(data.get("target_x"), data.get("target_y"))
                    )
                elif command_type == "moo":
                    await self.rover.moo()
                elif command_type == "beep":
                    await self.rover.beep()
                elif command_type == "stop":
                    await self.rover.stop()

                logger.debug(f"Команда: {data}")

            except json.JSONDecodeError:
                logger.warning(f"Невалидный JSON: {message}")
            except Exception as e:
                logger.error(f"Ошибка обработки команды: {e}")

    async def handle_websocket_with_rc(self, websocket):
        """Обработка WebSocket с RC контекстом"""
        initial_data = {
            "type": "config",
            "rover_id": self.rover_number,
            "arena_size": self.arena
        }
        await websocket.send(json.dumps(initial_data))

        telemetry_task = asyncio.create_task(self.send_telemetry_data(websocket))

        try:
            async with self.rover.rc_stream_context() as rc_control:
                await self.handle_rc_commands(websocket, rc_control)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket клиент отключился")
        finally:
            telemetry_task.cancel()
            try:
                await telemetry_task
            except asyncio.CancelledError:
                pass

    async def handle_websocket_without_rc(self, websocket):
        """Обработка WebSocket без RC контекста"""
        initial_data = {
            "type": "config",
            "rover_id": self.rover_number,
            "arena_size": self.arena
        }
        await websocket.send(json.dumps(initial_data))

        telemetry_task = asyncio.create_task(self.send_telemetry_data(websocket))

        try:
            await self.handle_direct_commands(websocket)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket клиент отключился")
        finally:
            telemetry_task.cancel()
            try:
                await telemetry_task
            except asyncio.CancelledError:
                pass

    async def handle_websocket_connection(self, websocket):
        """Основной обработчик WebSocket соединения"""
        logger.info(f"Новое WebSocket соединение")

        if self.video:
            await self.handle_websocket_with_rc(websocket)
        else:
            await self.handle_websocket_without_rc(websocket)

    async def start_web_server(self):
        """Запуск HTTP сервера"""
        await self.web_app.run()

    async def start_websocket_server(self):
        """Запуск WebSocket сервера"""
        async with websockets.serve(self.handle_websocket_connection, "0.0.0.0", 8765):
            logger.info("WebSocket сервер запущен на порту 8765")
            await asyncio.Future()  # Бесконечное ожидание

    async def run(self):
        """Основной метод запуска сервера"""
        if not await self.connect_to_rover():
            return

        await asyncio.gather(
            self.start_web_server(),
            self.start_websocket_server()
        )

    async def shutdown(self):
        """Корректное завершение работы"""
        if self.rover:
            await self.rover.disconnect()


