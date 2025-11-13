


import os
import sys
import asyncio
import inspect
import traceback
import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, AsyncGenerator, Awaitable
from aioquic.asyncio.server import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from typing import Any, AsyncGenerator, Union
from aioquic.quic.events import (
    QuicEvent,
    ConnectionTerminated,
    StreamDataReceived,
)


from gnobjects.net.objects import GNRequest, GNResponse, FileObject, CORSObject, TempDataGroup, TempDataObject, CacheConfig
from gnobjects.net.fastcommands import AllGNFastCommands, GNFastCommand, AllGNFastCommands as responses

from KeyisBTools.cryptography.bytes import userFriendly
from KeyisBTools.models.serialization import serialize, deserialize


from ._func_params_validation import register_schema_by_key, validate_params_by_key
from ._cors_resolver import resolve_cors
from ._routes import Route, _compile_path, _ensure_async, _convert_value
from .models import KDCObject
from ._client import AsyncClient

from ._datagram_enc import DatagramEncryptor, EncryptedQuicProtocol

from pathlib import Path

try:
    if not sys.platform.startswith("win"):
        import uvloop # type: ignore
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    print("uvloop не установлен")


import logging

logger = logging.getLogger("GNServer")
logger.setLevel(logging.DEBUG)
logger.propagate = False
# --- Удаляем все старые хендлеры, чтобы не было дублей ---
if logger.hasHandlers():
    logger.handlers.clear()

# --- Добавляем новый консольный хендлер ---
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.DEBUG)

# Формат с временем
formatter = logging.Formatter(
    "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console.setFormatter(formatter)

logger.addHandler(console)



def guess_type(filename: str) -> str:
    """
    Возвращает актуальный MIME-тип по расширению файла.
    Только современные и часто используемые типы.
    """
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

    mime_map = {
        # 🔹 Текст и данные
        "txt": "text/plain",
        "html": "text/html",
        "css": "text/css",
        "csv": "text/csv",
        "xml": "application/xml",
        "json": "application/json",
        "js": "application/javascript",

        # 🔹 Изображения (актуальные для веба)
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
        "avif": "image/avif",
        "ico": "image/x-icon",

        # 🔹 Видео (современные форматы)
        "mp4": "video/mp4",
        "webm": "video/webm",

        # 🔹 Аудио (современные форматы)
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "oga": "audio/ogg",
        "m4a": "audio/mp4",
        "flac": "audio/flac",

        # 🔹 Архивы
        "zip": "application/zip",
        "gz": "application/gzip",
        "tar": "application/x-tar",
        "7z": "application/x-7z-compressed",
        "rar": "application/vnd.rar",

        # 🔹 Документы (актуальные офисные)
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",

        # 🔹 Шрифты
        "woff": "font/woff",
        "woff2": "font/woff2",
        "ttf": "font/ttf",
        "otf": "font/otf",
    }

    return mime_map.get(ext, "application/octet-stream")





class App:
    def __init__(self):
        self._routes: List[Route] = []
        self._cors: Optional[CORSObject] = None
        self._events: Dict[str, List[Dict[str, Union[Any, Callable]]]] = {}

        self.domain: str = None # type: ignore

        self.__allowed_modes = (1, 2, 4)

        self._kdc: Optional[KDCObject] = None
        
        self.client = AsyncClient()


    def setKDC(self, kdc: KDCObject):
        self._kdc = kdc
        self.client.setKDC(kdc)


    def route(self, method: str, path: str, cors: Optional[CORSObject] = None):
        if path == '/':
            path = ''
        def decorator(fn: Callable[..., Any]):
            regex, param_types = _compile_path(path)
            self._routes.append(
                Route(
                    method.upper(),
                    path,
                    regex,
                    param_types,
                    _ensure_async(fn),
                    fn.__name__,
                    cors
                )
            )
            register_schema_by_key(fn)
            return fn
        return decorator

    def get(self, path: str, *, cors: Optional[CORSObject] = None):
        return self.route("GET", path, cors)

    def post(self, path: str, *, cors: Optional[CORSObject] = None):
        return self.route("POST", path, cors)

    def put(self, path: str, *, cors: Optional[CORSObject] = None):
        return self.route("PUT", path, cors)

    def delete(self, path: str, *, cors: Optional[CORSObject] = None):
        return self.route("DELETE", path, cors)

    
    def setRouteCors(self, cors: Optional[CORSObject] = None):
        self._cors = cors


    def addEventListener(self, name: str, * , move_to_start: bool = False):
        def decorator(fn: Callable[[Callable[[dict | None], Awaitable[Any]]], None]):
            events = self._events.get(name, [])
            events.append({
                'func': fn,
                'async': inspect.iscoroutinefunction(fn),
                'parameters': inspect.signature(fn).parameters
                })
            if move_to_start:
                events = [events[-1]] + events[:-1]
            self._events[name] = events
            
            return fn
        return decorator
    async def dispatchEvent(self, name: str, *args, **kwargs) -> None:
        handlers = self._events.get(name)
        if not handlers:
            return

        for h in handlers:
            func: Callable = h['func']
            is_async = h['async']
            params = h['parameters']

            # фильтрация kwargs по сигнатуре функции
            if kwargs:
                call_kwargs = {k: v for k, v in kwargs.items() if k in params} # type: ignore
            else:
                call_kwargs = {}

            if is_async:
                await func(*args, **call_kwargs)
            else:
                func(*args, **call_kwargs)



    async def dispatchRequest(
        self, request: GNRequest
    ) -> Union[GNResponse, AsyncGenerator[GNResponse, None]]:
        path    = request.url.path
        method  = request.method.upper()
        cand    = {path, path.rstrip("/") or "/", f"{path}/"}
        allowed = set()

        for r in self._routes:
            m = next((r.regex.fullmatch(p) for p in cand if r.regex.fullmatch(p)), None)
            if not m:
                continue

            allowed.add(r.method)
            if r.method != method:
                continue

            resolve_cors(request, r.cors)

            sig = inspect.signature(r.handler)
            def _ann(name: str):
                param = sig.parameters.get(name)
                return param.annotation if param else inspect._empty

            kw: dict[str, Any] = {
                name: _convert_value(val, _ann(name), r.param_types.get(name, str))
                for name, val in m.groupdict().items()
            }

            for qn, qvals in request.url.params.items():
                if qn in kw:
                    continue
                if isinstance(qvals, int):
                    kw[qn] = qvals
                else:
                    raw = qvals if len(qvals) > 1 else qvals[0]
                    kw[qn] = _convert_value(raw, _ann(qn), str)

            
            params = set(sig.parameters.keys())
            kw = {k: v for k, v in kw.items() if k in params}

            
            rv = validate_params_by_key(kw, r.handler)
            if rv is not None:
                raise AllGNFastCommands.UnprocessableEntity({'dev_error': rv, 'user_error': f'Server request error {self.domain}'})

            if "request" in sig.parameters:
                kw["request"] = request

            if inspect.isasyncgenfunction(r.handler):
                return r.handler(**kw)

            result = await r.handler(**kw)
            if result is None:
                result = AllGNFastCommands.ok()
            if isinstance(result, GNResponse):
                if r.cors is None:
                    if result._cors is None:
                        result._cors = self._cors
                else:
                    result._cors = r.cors

                resolve_cors(request, result._cors)

                return result
            else:
                raise TypeError(
                    f"{r.handler.__name__} returned {type(result)}; GNResponse expected"
                )

        if allowed:
            raise AllGNFastCommands.MethodNotAllowed()
        raise AllGNFastCommands.NotFound()


    def fastFile(self, path: str, file_path: str, cache: Optional[CacheConfig] = None, cors: Optional[CORSObject] = None, inType: Optional[str] = None):
        @self.get(path)
        async def r_static():
            nonlocal file_path
            if file_path.endswith('/'):
                file_path = file_path[:-1]
                
            if not os.path.isfile(file_path):
                raise AllGNFastCommands.NotFound()

            fileObject = FileObject(file_path)
            return responses.ok(TempDataObject('static', path=path, payload=fileObject, cache=cache, cors=cors, inType=inType))


    def staticDir(self, path: str, dir_path: str, cache: Optional[CacheConfig] = None, cors: Optional[CORSObject] = None, inType: Optional[str] = None):
        @self.get(f"{path}/{{_path:path}}")
        async def r_static(_path: str):
            file_path = os.path.join(dir_path, _path)
            
            if file_path.endswith('/'):
                file_path = file_path[:-1]
                
            if not os.path.isfile(file_path):
                raise AllGNFastCommands.NotFound()
            
            fileObject = FileObject(file_path)
            return responses.ok(TempDataObject('static', path=f'{path}/{_path}', payload=fileObject, cache=cache, cors=cors, inType=inType))




    def _init_sys_routes(self):
        @self.post('/!gn-vm-host/ping', cors=CORSObject(allow_client_types=['server']))
        async def r_ping(request: GNRequest):
            if request.client.ip != '127.0.0.1':
                raise AllGNFastCommands.Forbidden()
            return responses.ok({'time': datetime.datetime.now(datetime.timezone.utc).isoformat()})



    class _ServerProto(EncryptedQuicProtocol):
        def __init__(self, *a, api: "App", **kw):
            self._api = api

            dgEncryptor = DatagramEncryptor(self._api._kdc, self._api.domain, callback_domain=self._set_domain)
            super().__init__(*a, dgEncryptor=dgEncryptor, **kw)
            self._buffer: Dict[int, bytearray] = {}
            self._streams: Dict[int, Tuple[asyncio.Queue[Optional[GNRequest]], bool]] = {}

            self._domain: Optional[str] = None
            self._disconnected = False
        def quic_event_received(self, event: QuicEvent):
            if isinstance(event, StreamDataReceived):
                buf = self._buffer.setdefault(event.stream_id, bytearray())
                buf.extend(event.data)

                stream_id = event.stream_id

                if event.end_stream:
                    asyncio.create_task(self._resolve_raw_request(stream_id, buf))
            

            elif isinstance(event, ConnectionTerminated):
                reason = event.reason_phrase or f"code={event.error_code}"
                self._trigger_disconnect(f"ConnectionTerminated: {reason}")
            
            
        def connection_lost(self, exc):
            self._trigger_disconnect(f"Transport closed: {exc!r}")

        def _trigger_disconnect(self, reason: str):
            if self._disconnected:
                return
            self._disconnected = True

            logger.info(f"[DISCONNECT]  — {reason}")

            
            asyncio.create_task(self._api.dispatchEvent('disconnect', domain=self._domain, L5_reason=reason))


        def _set_domain(self, domain: str):
            self._domain = domain

        async def _resolve_raw_request(self, stream_id: int, data: bytes):
    
            request = GNRequest.deserialize(data)
                
            await self._resolve_dev_transport_request(request)

            # if not proto._init_domain:
            #     proto._domain = request.client.domain
            #     asyncio.create_task(self._api.dispatchEvent('connect', proto=proto, domain=proto._domain, request=request))
            
            
            if self._domain is None:
                asyncio.create_task(self.sendRawResponse(stream_id, GNResponse('error', {'error': 'domain not set'}).serialize()))
                return
            
            
            request.client._data['domain'] = self._domain
            
            request.client._data['remote_addr'] = self._quic._network_paths[0].addr
            request.stream_id = stream_id   # type: ignore

            self._buffer.pop(stream_id, None)
            await self._handle_request(request)

        async def _resolve_dev_transport_request(self, request: GNRequest):
            if not request.transportObject.routeProtocol.dev:
                return
            
            if request.cookies is not None:
                data: Optional[dict] = request.cookies.get('gn', {}).get('request', {}).get('transport', {}).get('::dev')
                if data is not None:
                    if 'netstat' in data:
                        if 'way' in data['netstat']:
                            data['netstat']['way']['data'].append({
                                'object': f'{self._domain}',
                                'step': '4',
                                'type': 'L6',
                                'action': 'rosolve',
                                'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                'route': str(request.route),
                                'method': request.method,
                                'url': str(request.url),
                            })

        async def _resolve_dev_transport_response(self, response: GNResponse, request: GNRequest):
            
            if request.cookies is None:
                return
            
            gn_ = request.cookies.get('gn')
            if gn_ is not None:
                if response._cookies is None:
                    response._cookies = {}
                response._cookies['gn'] = gn_



            gn_ = request.cookies.get('gn')
            if gn_ is not None:
                if response._cookies is None:
                    response._cookies = {}
                response._cookies['gn'] = gn_










            if not request.transportObject.routeProtocol.dev:
                return

            data: Optional[dict] = response.cookies.get('gn', {}).get('request', {}).get('transport', {}).get('::dev')
            if data is None:
                return
            
            if 'netstat' in data:
                if 'way' in data['netstat']:
                    data['netstat']['way']['data'].append({
                        'object': f'{self._domain}',
                        'type': 'L6',
                        'action': 'rosolve',
                        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        'route': str(request.route),
                        'method': request.method,
                        'url': str(request.url),
                    })


        async def _handle_request(self, request: GNRequest):

            try:
                response = await self._api.dispatchRequest(request)

                if inspect.isasyncgen(response):
                    async for chunk in response:  # type: ignore[misc]
                        chunk._stream = True
                        await self.sendResponse(request, chunk, False)
                        
                    resp = GNResponse('gn:end-stream')
                    resp._stream = True

                    await self.sendResponse(request, resp)
                    return

                if not isinstance(response, GNResponse):
                    await self.sendResponse(request, AllGNFastCommands.InternalServerError())
                    return

                await self.sendResponse(request, response)
            except Exception as e:
                if isinstance(e, (GNRequest, GNFastCommand)):
                    await self.sendResponse(request, e)
                else:
                    logger.error('InternalServerError:\n'  + traceback.format_exc())

                    await self.sendResponse(request, AllGNFastCommands.InternalServerError())
            

        
        async def sendResponse(self, request: GNRequest, response: GNResponse, end_stream: bool = True):
            await self._resolve_dev_transport_response(response, request)
            await response.assembly()

            
            logger.debug(f'[>] [{request.client.domain}] Response: {request.method} {request.url} -> {response.command} {response.payload if len(str(response.payload)) < 256 else ''}')
            
            blob = response.serialize()


            await self.sendRawResponse(request.stream_id, blob=blob, end_stream=end_stream)

        async def sendRawResponse(self, stream_id: int, blob: bytes, end_stream: bool = True):
            self._quic.send_stream_data(stream_id, blob, end_stream=end_stream) # type: ignore
            self.transmit()

    def run(
        self,
        domain: str,
        port: int,
        tls_certfile: Union[bytes, str],
        tls_keyfile: Union[bytes, str],
        *,
        host: str = '0.0.0.0',
        idle_timeout: float = 20.0,
        wait: bool = True,
        run: Optional[Callable] = None
    ):
        """
        # Запустить сервер

        Запускает сервер в главном процессе asyncio.run()

        """

        self.domain = domain


        if self.client._domain is None:
            self.client._domain = domain




        self._init_sys_routes()

        cfg = QuicConfiguration(
            alpn_protocols=["gn:backend"], is_client=False, idle_timeout=idle_timeout
        )


        
        from aioquic.tls import (
            load_pem_private_key,
            load_pem_x509_certificates,
        )
        from re import split


        if os.path.isfile(tls_certfile):
            with open(tls_certfile, "rb") as fp:
                boundary = b"-----BEGIN PRIVATE KEY-----\n"
                chunks = split(b"\n" + boundary, fp.read())
                certificates = load_pem_x509_certificates(chunks[0])
                if len(chunks) == 2:
                    private_key = boundary + chunks[1]
                    cfg.private_key = load_pem_private_key(private_key)
            cfg.certificate = certificates[0]
            cfg.certificate_chain = certificates[1:]
        else:
            if isinstance(tls_certfile, str):
                tls_certfile = tls_certfile.encode()
                
            boundary = b"-----BEGIN PRIVATE KEY-----\n"
            chunks = split(b"\n" + boundary, tls_certfile)
            certificates = load_pem_x509_certificates(chunks[0])
            if len(chunks) == 2:
                private_key = boundary + chunks[1]
                cfg.private_key = load_pem_private_key(private_key)
            cfg.certificate = certificates[0]
            cfg.certificate_chain = certificates[1:]

        
        if os.path.isfile(tls_keyfile):
            
            with open(tls_keyfile, "rb") as fp:
                cfg.private_key = load_pem_private_key(
                    fp.read()
                )
        else:
            if isinstance(tls_keyfile, str):
                tls_keyfile = tls_keyfile.encode()
            cfg.private_key = load_pem_private_key(
                tls_keyfile
            )

        if cfg.certificate is None or cfg.private_key is None:
            raise Exception('Не удалось загрузить TLS сертификат или ключ')

        async def _main():
            
            await self.dispatchEvent('start')

            await serve(
                host,
                port,
                configuration=cfg,
                create_protocol=lambda *a, **kw: App._ServerProto(*a, api=self, **kw),
                retry=False,
            )
            
            if run is not None:
                await run()

            logger.debug('Server startup completed')
            if wait:
                await asyncio.Event().wait()

        asyncio.run(_main())


    def runByVMHost(self):
        """
        # Запусить через VM-host

        Заупскает сервер через процесс vm-host
        """
        argv = sys.argv[1:]
        data_enc = argv[0]

        data: dict = deserialize(userFriendly.decode(data_enc)) # type: ignore

        if data['command'] == 'gn:vm-host:start':
            self.run(
                domain=data['domain'],
                port=data['port'],
                tls_certfile=data.get('cert_path'),
                tls_keyfile=data.get('key_path'),
                host=data.get('host', '0.0.0.0')
            )