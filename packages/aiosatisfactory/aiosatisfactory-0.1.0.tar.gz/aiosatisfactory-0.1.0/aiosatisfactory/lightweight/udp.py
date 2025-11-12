import asyncio

async def udp_query(host: str, port: int, data: bytes, timeout: float = 2.0) -> bytes | None:

    async_loop = asyncio.get_running_loop()
    future = async_loop.create_future()
        
    class UdpProtocol(asyncio.DatagramProtocol):
        def datagram_received(self, data: bytes, addr: tuple[str, int]):
            future.set_result(data)

    transport, _ = await async_loop.create_datagram_endpoint(UdpProtocol, remote_addr=(host, port))

    transport.sendto(data)

    try:
        return await asyncio.wait_for(future, timeout)
    except TimeoutError:
        return None
    finally:
        transport.close()