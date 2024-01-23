import asyncio
import logging
import websockets
import names
import datetime
import exchange
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from aiofile import AIOFile


logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    @staticmethod
    async def log_command(command, response):
        async with AIOFile('exchange_log.txt', 'a') as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await log_file.write(f"[{timestamp}] Команда: {command}, Відповідь: {response}\n")
            await log_file.fsync()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith("exchange"):

                _, days, currency = message.split()
                asyncio.create_task(self.process_exchange(ws, days, currency.upper()))

            else:
                await self.send_to_clients(f"{ws.name}: {message}")

    @staticmethod
    async def process_exchange (ws, days, currency):
        try:
            days = int(days)
            response = await exchange.main(days, currency.upper())
        except ValueError:
            response = "Некоректний формат команди exchange."

        await ws.send(f'server: {response}')
        await Server.log_command("exchange", response)


async def main():
    server = Server()
    asyncio.create_task(exchange.monitoring())
    async with websockets.serve(server.ws_handler, 'localhost', 8000):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
