import asyncio
import argparse
import sys

try:
    from .ws_server import WebSocketServer
    ws_control = True
except ImportError:
    ws_control = False

from geodrive.logging import get_logger


logger = get_logger("ws-control")

missing_depens_message = """
Не установлены зависимости для ws-control. Установите:

pip install 'geodrive[ws-control]'
или 
uv add geodrive[ws-control]
"""
if not ws_control:
    logger.error(missing_depens_message)
    sys.exit(1)


async def run(rover_num: int, local: bool, arena: int, video: bool):
    """Функция запуска сервера"""
    server = WebSocketServer(rover_num, local, arena, video)
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Остановка сервера...")
    finally:
        await server.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Websocket сервер для ручного управления роботом")
    parser.add_argument("num", type=int, nargs='?', default=160)
    parser.add_argument("-l", "--local", action="store_true",
                        help="Подключение к локальному серверу (localhost) вместо реального ровера")
    parser.add_argument("-v", "--video", action="store_true",
                        help="Панель управления с видео (использует RC каналы)")
    parser.add_argument("-a", "--arena", type=int, default=11,
                        help="Размер арены (по умолчанию: 11)")

    args = parser.parse_args()

    if not (0 <= args.num <= 255):
        logger.error("Ошибка: номер ровера должен быть в диапазоне 0-255")
        sys.exit(1)

    if not ws_control:
        logger.error(missing_depens_message)
        sys.exit(1)

    try:
        asyncio.run(run(args.num, args.local, args.arena, args.video))
    except KeyboardInterrupt:
        logger.info("Сервер остановлен")
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {e}")


if __name__ == "__main__":
    main()