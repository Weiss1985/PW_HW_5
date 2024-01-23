import asyncio
import websockets
import exchange
from aiofile import AIOFile


async def log_command(command, response):
    async with AIOFile('exchange_log.txt', 'a') as log_file:
        await log_file.write(f"Команда: {command}, Відповідь: {response}\n")
        await log_file.fsync()


async def hello(websocket):
    message = await websocket.recv()
    print(f'<<< {message}')

    # Розбиваємо рядок на частини
    parts = message.split()
    if len(parts) != 3 or parts[0].lower() != 'exchange':
        await websocket.send("Некоректний формат команди.")
        return
    command, days, currency = parts

    try:
        days = int(days)
    except ValueError:
        await websocket.send("Дні повинні бути числом.")
        return

    response = await exchange.main(days, currency.upper())
    await log_command(message, response)

    await websocket.send(response)
    print(f">>> {response}")


async def main():
    async with websockets.serve(hello, "localhost", 8000):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
