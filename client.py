import asyncio
import websockets


async def exchange():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        # Отримуємо команду від користувача
        command = input("Введіть команду (наприклад, 'exchange 2 USD'): ")

        # Відправляємо команду на сервер
        await websocket.send(command)
        print(f"Відправлено: {command}")

        # Очікуємо відповідь від сервера
        response = await websocket.recv()
        print(f"Отримано відповідь:\n{response}")


if __name__ == "__main__":
    asyncio.run(exchange())