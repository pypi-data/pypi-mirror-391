from pygeist_client import _adapter
from pygeist_client.response import Response
from pygeist_client.abstract.methods_handler import AsyncMethodHandler
from pygeist_client.unrequested import Unrequested
import asyncio


class PygeistClient(AsyncMethodHandler):
    def __init__(self,
                 response_timeout=5, # seconds
                 ) -> None:
        self.c = _adapter._create_client(1, 1)
        self.response_timeout = response_timeout

    async def link(self,
                   url: str,
                   port: int,
                   ) -> None:
        """
        Stablish a link to a server that utilizes the Zeitgeist protocol
        This needs to be done before making any request to the server
        """
        if url == 'localhost':
            url = '127.0.0.1'
        await asyncio.to_thread(_adapter._connect_client,
                                self.c,
                                url,
                                port,)

    async def _handle(self,
                      method: int,
                      target: str,
                      headers: dict = {},
                      body = '',
                      ) -> Response:
        headers_str = "\r\n".join(f"{k}: {v}" for k, v in headers.items()) + "\r\n\r\n"
        req_id = await asyncio.to_thread(
            _adapter._make_client_request,
            self.c,
            method,
            target,
            headers_str,
            body,
        )

        await asyncio.wait_for(
            asyncio.to_thread(_adapter._listen_client_input,
                              self.c),
            timeout=self.response_timeout,
        )
        await asyncio.to_thread(_adapter._process_client_input,
                                self.c)

        return await asyncio.to_thread(_adapter._get_client_response,
                                       self.c,
                                       req_id)

    async def unlink(self) -> None:
        await asyncio.to_thread(_adapter._disconnect_client,
                                self.c)

    def __del__(self) -> None:
        _adapter._destroy_client(self.c)

    async def pop_msg(self,
                      timeout=5, # seconds
                      ) -> Unrequested | None:
        await asyncio.wait_for(
            asyncio.to_thread(_adapter._listen_client_input,
                              self.c),
            timeout=timeout,
        )
        await asyncio.to_thread(_adapter._process_client_input,
                                self.c)
        return await asyncio.to_thread(_adapter._pop_client_message, self.c)
