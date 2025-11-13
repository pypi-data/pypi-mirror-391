import re
import os
import ast
from typing import Optional, Dict, Any, List, Union, Literal, Tuple, cast, overload, Type
import anyio
from KeyisBTools.models.serialization import serialize, deserialize, SerializableType

from .gnTransportProtocolParser import GNTransportProtocol, parse_gn_protocol


from .values import tablex_file_extension_to_inType
from ._data_pack import (
    pack_temp_data_object,
    pack_gnrequest,
    unpack_gnrequest,
    unpack_temp_data_object,
    pack_temp_data_group,
    unpack_temp_data_group,
    pack_gnresponse,
    unpack_gnresponse
    )






class Url:
    
    __slots__ = (
        "transport", "route", "scheme",
        "hostname", "port", "path", "params", "fragment"
    )

    _re_hostport = re.compile(r"""
        ^
        (?P<host>\[[^\]]+\]|[^:]+)
        (?::(?P<port>\d+))?
        $
    """, re.X)

    @overload
    def __init__(self): ...
    
    @overload
    def __init__(self, url: str): ...

    @overload
    def __init__(self, url: 'Url'): ...

    def __init__(self, url: Optional[Union[str, 'Url']] = None):
        self.transport: Optional[str] = None
        self.route: Optional[str] = None
        self.scheme: str = None # type: ignore
        self.hostname: str = None # type: ignore
        self.path: str = "/"
        self.params: Dict[str, Any] = {}
        self.fragment: Optional[str] = None

        if url:
            self.setUrl(url)

    def setUrl(self, url: Union[str, 'Url']):
        if isinstance(url, Url):
            self.transport = url.transport
            self.route = url.route
            self.scheme = url.scheme
            self.hostname = url.hostname
            self.path = url.path
            self.params = url.params
            self.fragment = url.fragment
            return
            
        proto, _, rest = url.partition("://")
        if not rest:
            raise ValueError(f"Invalid URL: {url}")

        if "~~" in proto:
            t, _, s = proto.partition("~~")
            self.transport, self.route, self.scheme = t, None, s or "gn"
        elif "~" in proto:
            parts = proto.split("~")
            if len(parts) == 3:
                self.transport, self.route, self.scheme = parts
            elif len(parts) == 2:
                self.transport, self.route, self.scheme = None, parts[0], parts[1]
            else:
                raise ValueError(f"Invalid protocol chain: {proto}")
        else:
            self.transport, self.route, self.scheme = None, None, proto or "gn"

        if not self.scheme:
            self.scheme = "gn"

        hostpath, _, frag = rest.partition("#")
        self.fragment = frag if frag != "" else None

        hostpath, _, query = hostpath.partition("?")
        if self.scheme == 'lib':
            host, self.path = 'libs.gn', hostpath
        elif "/" in hostpath:
            host, path = hostpath.split("/", 1)
            self.path = "/" + path
        else:
            host, self.path = hostpath, "/"

        if not host and self.scheme != "file":
            raise ValueError(f"Missing hostname in URL: {url}")

        if host:
            m = self._re_hostport.match(host)
            if not m:
                raise ValueError(f"Invalid hostname: {host}")
            self.hostname = m.group("host")
            if self.hostname.startswith("[") and self.hostname.endswith("]"):
                self.hostname = self.hostname[1:-1] # type: ignore
            p = m.group("port")
            if p is not None:
                self.hostname += ':' + p

        self.params = {}
        if query:
            for part in query.split("&"):
                if not part:
                    continue
                k, eq, v = part.partition("=")
                if not eq:
                    self.params[k] = None
                    continue
                try:
                    val = ast.literal_eval(v)
                except Exception:
                    val = v
                self.params[k] = val

    def _build_query(self) -> str:
        if not self.params:
            return ""
        out = []
        for k, v in self.params.items():
            if v is None:
                out.append(k)
            elif isinstance(v, str):
                out.append(f"{k}={v}")
            else:
                out.append(f"{k}={repr(v)}")
        return "&".join(out)

    def build(self, parts: List[str]) -> str:
        url = ""

        if "scheme" in parts or "transport" in parts or "route" in parts:
            if self.transport and self.route:
                proto = f"{self.transport}~{self.route}~{self.scheme}"
            elif self.transport and not self.route:
                proto = f"{self.transport}~~{self.scheme}"
            elif self.route and not self.transport:
                proto = f"{self.route}~{self.scheme}"
            else:
                proto = self.scheme or "gn"
            url += proto + "://"

        if "hostname" in parts and self.hostname:
            if ":" in self.hostname:
                host = f"[{self.hostname}]"
            else:
                host = self.hostname
            url += host

        if "path" in parts and self.path:
            url += self.path

        if "params" in parts and self.params:
            q = self._build_query()
            if q:
                url += f"?{q}"

        if "fragment" in parts and self.fragment is not None:
            url += f"#{self.fragment}"

        return url

    def toString(self) -> str:
        return self.build(["transport", "route", "scheme", "hostname", "path", "params", "fragment"])

    def __str__(self):
        return self.toString()




# def _pack(mode: int, flag: bool, number: int) -> bytes:
#     if not (1 <= mode <= 4): raise ValueError("mode должен быть 1..4")
#     if number >= (1 << 61): raise ValueError("number должен быть < 2^61")
#     value = ((mode - 1) & 0b11) << 62
#     value |= (1 << 61) if flag else 0
#     value |= number & ((1 << 61) - 1)
#     return value.to_bytes(8, "big")

# def _unpack(data: bytes):
#     if len(data) < 8: raise Exception('len < 8')
#     value = int.from_bytes(data[:8], "big")
#     mode = ((value >> 62) & 0b11) + 1
#     flag = bool((value >> 61) & 1)
#     number = value & ((1 << 61) - 1)
#     return mode, flag, number


class CORSObject:
    def __init__(self,
                 allow_origins: Optional[List[str]] = None,
                 allow_methods: Optional[List[str]] = None,
                 allow_client_types: List[Literal['net', 'client', 'server']] = ['net'],
                 allow_transport_protocols: Optional[List[str]] = None,
                 allow_route_protocols: Optional[List[str]] = None,
                 allow_request_protocols: Optional[List[str]] = None
                 ) -> None:
        """
        # Механизм контроля доступа


        :allow_origins: Список доменов, с которых разрешен запрос.
        :allow_methods: Разрешенные методы для запроса.
        :allow_client_types: Какие типы клиентов могут использовать.

        - `net` - Пользователи и другие службы сети `GN`

        - `client` - (TBD) Пользователи напрямую. Без использования прокси серверов сети `GN`

        - `server` - Другие `origin` сервера сети `GN`

        :allow_transport_protocols: (TBD)
        :allow_route_protocols: (TBD)
        :allow_request_protocols: (TBD)
        """
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_client_types = allow_client_types
        self.allow_transport_protocols = allow_transport_protocols
        self.allow_route_protocols = allow_route_protocols
        self.allow_request_protocols = allow_request_protocols

            


    
    def serialize(self) -> Optional[bytes]:
        a = {}
        if self.allow_origins is not None:
            a[0] = self.allow_origins
        if self.allow_methods is not None:
            a[1] = self.allow_methods
        if self.allow_client_types is not None and self.allow_client_types != ['net']:
            a[2] = self.allow_client_types
        if self.allow_transport_protocols is not None:
            a[3] = self.allow_transport_protocols
        if self.allow_route_protocols is not None:
            a[4] = self.allow_route_protocols
        if self.allow_request_protocols is not None:
            a[5] = self.allow_request_protocols
        if not a:
            return None
        else:
            return serialize(a)
        

    @staticmethod
    def deserialize(data: Dict[int, Any]) -> 'CORSObject':
        return CORSObject(
            allow_origins=data.get(0, None),
            allow_methods=data.get(1, None),
            allow_client_types=data.get(2, ['net']),

            allow_transport_protocols=data.get(3, None),
            allow_route_protocols=data.get(4, None),
            allow_request_protocols=data.get(5, None)
        )

class FileObject:

    @overload
    def __init__(
        self,
        path: str
    ) -> None: ...

    @overload
    def __init__(
        self,
        path: str,
        inType: Union[Literal['html', 'css', 'js', 'svg', 'png', 'py'], str]
    ) -> None: ...

    @overload
    def __init__(
        self,
        data: bytes,
        inType: Union[Literal['html', 'css', 'js', 'svg', 'png', 'py'], str],
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        path_or_data: Union[str, bytes],
        inType: Optional[str] = None
    ) -> None:
        self._path: Optional[str] = None
        self._data: Optional[bytes] = None
        self._inType: Optional[str] = None
        self._is_assembly: Optional[Tuple[bytes, str]] = None

        if isinstance(path_or_data, str):
            self._path = path_or_data

            if inType is None:
                ext = os.path.splitext(path_or_data)[1].lower()
                if ext.startswith('.'):
                    ext = ext[1:]
                guessed = tablex_file_extension_to_inType.get(ext)
                self._inType = guessed or 'bin'
            else:
                self._inType = inType

        elif isinstance(path_or_data, bytes):
            if inType is None:
                raise ValueError('Для данных bytes требуется указать inType')
            self._data = path_or_data
            self._inType = inType

        else:
            raise TypeError(f"path_or_data: ожидается str или bytes, получено {type(path_or_data)!r}")


    async def assembly(self) -> Tuple[bytes, str]:
        if self._is_assembly is not None:
            return self._is_assembly

        if self._data is None:
            if not isinstance(self._path, str):
                raise Exception('Ошибка сборки файла -> Путь к файлу не str')
            
            if not os.path.exists(self._path):
                raise Exception(f'Ошибка сборки файла -> Файл не найден {self._path}')

            try:
                async with await anyio.open_file(self._path, mode="rb") as file:
                    self._data = await file.read()
            except Exception as e:
                raise Exception(f'Ошибка сборки файла -> Ошиибка при чтении файла: {e}')

        self._is_assembly = (self._data, self._inType) # type: ignore

        return self._is_assembly # type: ignore


_ = {
    'cache': bool,
    'origin': {
        'cache': bool,
        'clear_time': int,
        'lazy_clear': bool,
        'lazy_clear_max_time': int,
        'dedupe_window_us': int, # min 100
    },
    'nexus': {
        'cache': bool,
        'clear_time': int,
        'lazy_clear': bool,
        'lazy_clear_max_time': int,
        'dedupe_window_us': int, # min 100

    },
    'shield': {
        'cache': bool,
        'clear_time': int,
        'lazy_clear': bool,
        'lazy_clear_max_time': int,
        'dedupe_window_us': int, # min 100

    },
    'client': {
        'cache': bool,
        'clear_time': int,
        'lazy_clear': bool,
        'lazy_clear_max_time': int,
        'dedupe_window_us': int, # min 100

    }
}

cacheDefaultConfig = {
    'cache': True,
    'origin': {
        'cache': False,
        'clear_time': 60 * 10,
        'lazy_clear': True,
        'lazy_clear_max_time': 60 * 5,
        'dedupe_window_us': 100,
    },
    'nexus': {
        'cache': True,
        'clear_time': 60 * 10,
        'lazy_clear': True,
        'lazy_clear_max_time': 60 * 5,
        'dedupe_window_us': 100,

    },
    'shield': {
        'cache': True,
        'clear_time': 60 * 10,
        'lazy_clear': True,
        'lazy_clear_max_time': 60 * 5,
        'dedupe_window_us': 100,

    },
    'client': {
        'cache': True,
        'clear_time': 60 * 10,
        'lazy_clear': True,
        'lazy_clear_max_time': 60 * 5,
        'dedupe_window_us': 100,

    }
}

class CacheObject:
    def __init__(self,
                 cache: bool = True,
                 clear_time_s: int = 60 * 10,
                 lazy_clear_s: bool = True,
                 lazy_clear_max_time_s: int = 60 * 5,
                 dedupe_window_us: int = 100,
               ) -> None:
        self.cache = cache
        self.clear_time_s = clear_time_s
        self.lazy_clear_s = lazy_clear_s
        self.lazy_clear_max_time_s = lazy_clear_max_time_s
        self.dedupe_window_us = dedupe_window_us
    
    def assemble(self) -> Dict[str, Any]:
        return {
            'cache': self.cache,
            'clear_time': self.clear_time_s,
            'lazy_clear': self.lazy_clear_s,
            'lazy_clear_max_time': self.lazy_clear_max_time_s,
            'dedupe_window_us': self.dedupe_window_us,
        }

class CacheConfig:
    def __init__(self,
                 origin: Optional[CacheObject] = CacheObject(),
                 nexus: Optional[CacheObject] = CacheObject(),
                 shield: Optional[CacheObject] = CacheObject(),
                 client: Optional[CacheObject] = CacheObject(),
                 cache: Optional[bool] = None,
                 cache_config: Optional[Dict[str, Any]] = None
                 ) -> None:
        if cache_config is not None:
            self.cache_config = cache_config
        else:
            self.cache_config = cacheDefaultConfig

            if cache is not None:
                self.cache_config['cache'] = cache

            if origin is not None:
                self.cache_config['origin'] = origin.assemble()
            if nexus is not None:
                self.cache_config['nexus'] = nexus.assemble()
            if shield is not None:
                self.cache_config['shield'] = shield.assemble()
            if client is not None:
                self.cache_config['client'] = client.assemble()

    def assemble(self) -> Dict[str, Any]:
        return self.cache_config

    def serialize(self) -> bytes:
        return serialize(self.cache_config)


class TempDataObject:
    def __init__(self,
                 dataType: Literal['api', 'static', 'images', 'bigdata'],
                 path: str,
                 payload: Union[SerializableType, FileObject],
                 cache: Optional[Union[CacheConfig, Dict[str, Any]]] = None,
                 cors: Optional[CORSObject] = None,
                 method: Union[Literal['get', 'post', 'put', 'delete'], str] = 'get',
                 inType: Optional[Union[Literal['html', 'css', 'js', 'svg', 'png', 'py'], str]] = None
                 ) -> None:
        """
        # Временный объект данных

        :param method: Метод запроса (GET, POST, PUT, DELETE и т.д.)
        :param type: Тип данных (api, static, images, bigdata)

            - `api` - Обычно некешируемые, уникальные для пользователя и ситуации данные
            - `static` - Кешируемые данные, которые редко меняются (например, html, css, js коды страниц, конфигурационные файлы и другие статические ресурсы <32MB)
            - `images` - Изображения и необязательные элементы интерфейса (например, иконки, аватары, фоны и другие изображения)
            - `bigdata` - Большие данные (например, видео, аудио, большие файлы. >32MB)

        :param path: Путь к данным
        :param payload: Полезная нагрузка (данные)

            любой сериализуемый тип данных или объект FileObject

        :param cache: Конфигурация кэширования или dict с конфигурацией кэширования


        """
        self.method = method
        self.dataType = dataType
        self.inType = inType
        self.path = path
        self.payload = payload
        self.cache: Optional[Union[CacheConfig, Dict[str, Any]]] = cache
        self.cors = cors

        self._cache_data: Optional[bytes] = None
        self._cors_data: Optional[bytes] = None

        self.assemble()

    def assemble(self):
        if self.cache is not None:
            if isinstance(self.cache, CacheConfig):
                self._cache_data = self.cache.serialize()
            else:
                self._cache_data = CacheConfig(cache_config=self.cache).serialize()
        else:
            self._cache_data = None

        if self.cors is not None:
            self._cors_data = self.cors.serialize()
        else:
            self._cors_data = None

    async def serialize(self) -> bytes:
        if isinstance(self.payload, FileObject):
            data, inType = await self.payload.assembly()
            self.payload = data
            self._inType = inType
        else:
            self.payload = serialize(self.payload)
        
        s = pack_temp_data_object(
            version=0,
            dataType=self.dataType,
            inType=self.inType,
            method=self.method,
            path=self.path,
            payload=self.payload,
            cache=self._cache_data,
            cors=self._cors_data
        )

        return s
    
    @staticmethod
    def deserialize(data: bytes) -> 'TempDataObject':
        d = unpack_temp_data_object(data)
        return TempDataObject(
            dataType=d['dataType'],
            inType=d['inType'],
            method=d['method'],
            path=d['path'],
            payload=d['payload'],
            cache=d['cache'],
            cors=d['cors']
        )


class TempDataGroup:
    def __init__(self,
                 path: str,
                 payload: List[TempDataObject],
                 auto_include: bool = True
                 ) -> None:
        """
        # Временная группа данных

        :param path: Путь к группе данных
        :param payload: Список временных объектов данных
        :param auto_include: При запросе любого объекта из группы, возвращать всю группу
        """
        self.path = path
        self.payload = payload
        self.auto_include = auto_include
    

    async def assemble(self):
        a = []
        for i in self.payload:
            s = await i.serialize()
            a.append(s)
        self.payload = a

    def serialize(self) -> bytes:
        if isinstance(self.payload[0], TempDataObject):
            raise ValueError('TempDataGroup is not assembled')
        
        return pack_temp_data_group(
            version=0,
            path=self.path,
            payload=self.payload # type: ignore
        )

    @staticmethod
    def deserialize(data: bytes) -> 'TempDataGroup':
        d = unpack_temp_data_group(data)
        return TempDataGroup(
            path=d['path'],
            payload=d['payload']
        )


class GNRequest:
    """
    # Запрос для сети `GN`
    """
    def __init__(
        self,
        method: str,
        url: Url,
        payload: Optional[SerializableType] = None,
        cookies: Optional[dict] = None,
        transport: Optional[str] = None,
        route: Optional[str] = None,
        origin: Optional[str] = None
    ):
        self._method: str = method
        self._url = url
        self._payload = payload
        self._cookies: dict = cookies
        self._transport: str = transport
        self._route: str = route
        self._origin = origin

        if self._cookies is None:
            self._cookies = {}

        if transport is None:
            self.setTransport()
        
        if route is None:
            self.setRoute()


        self.user = self.__user(self)
        """
        # Информация о пользователе

        Доступена только на сервере
        """

        self.client = self.__client(self)
        """
        # Информация о клиенте

        Доступена только на сервере
        """

    class __user:
        def __init__(self, request: 'GNRequest') -> None:
            self.__request = request
            self._data = self.__request._cookies.setdefault('gwis', {}).setdefault('o', {})
            
        
        @property
        def gwisid(self) -> int:
            """
            # ID объекта

            Возвращает уникальный идентификатор объекта в системе `GW`

            Этот идентификатор используется для управления объектами в системе.

            Может использоваться для идентификации пользователя.
            
            :return: int
            """
            return self._data.get("gwisid", 0)
        
        @property
        def sessionId(self) -> int:
            """
            # ID сессии

            Возвращает уникальный идентификатор сессии пользователя в сети `GN`
            
            Этот идентификатор используется для отслеживания состояния сессии пользователя в системе.

            Может использоваться для идентификации пользователя.
            
            :return: int
            """
            return self._data.get("session_id", 0)
        
        @property
        def nickname(self) -> str:
            """
            # Никнейм объекта

            Возвращает никнейм объекта в системе `GW`

            Никнейм используется для идентификации объекта в системе пользователями.

            Может использоваться для идентификации пользователя.

            :return: str
            """
            return self._data.get("nickname", "")

        @property
        def objectType(self) -> int:
            """
            # Тип объекта

            Возвращает тип объекта в системе `GW`
            
            Тип объекта используется для определения роли и функциональности объекта в системе.

            Возможные значения:
            - `0`: `GBN`
            - `2`: `Пользователь`
            - `3`: `Компания`
            - `4`: `Проект`
            - `5`: `Продукт`

            :return: int
            """
            return self._data.get("object_type", 0)
        
        @property
        def viewingType(self) -> int:
            """
            # Тип просмотра

            Возвращает тип просмотра объекта в системе `GW`

            Тип просмотра может быть установлен объекту для определения уровня доступа к объекту.

            Возможные значения:
            - `0`: Просмотр доступен только владельцу объекта
            - `1`: Просмотр не ограничен
            - `2`: Просмотр только авторизованным пользователям
            - `3`: Просмотр только для официально подтвержденных пользователей 

            :return: int
            """
            return self._data.get("viewing_type", 0)

        @property
        def description(self) -> str:
            """
            # Описание объекта

            Возвращает описание объекта в системе `GW`

            Описание может содержать дополнительную информацию о объекте.

            :return: str
            """
            return self._data.get("description", "")

        @property
        def name(self) -> str:
            """
            # Имя объекта

            Возвращает имя объекта в системе `GW`

            ```python
            Имя НЕ может быть использовано для идентификации объекта в системе пользователями.
            ```

            Может использоваться для определения объекта ТОЛЬКО пользователями.

            :return: str
            """
            return self._data.get("name", "")
        
        @property
        def owner(self) -> Optional[int]:
            """
            # `gwisid` владельца объекта

            Возвращает уникальный идентификатор `gwisid` владельца объекта в системе `GW`

            Этот идентификатор используется для определения владельца объекта.

            :return: Optional[int]
            Если владелец не установлен, возвращает None.
            """
            return self._data.get("owner", None)
        
        @property
        def officiallyConfirmed(self) -> bool:
            """
            # Официально подтвержденный объект

            Возвращает `True`, если объект официально подтвержден в системе `GW`

            Официально подтвержденные объекты могут иметь дополнительные права и возможности.

            :return: bool
            """
            return self._data.get("of_conf", False)

    class __client:
        model_client_types: Dict[int, str] = {
                1: 'net',
                2: 'server',
                4: 'client'
            }
        
        def __init__(self, request: 'GNRequest') -> None:
            self.__request = request
            self._data = self.__request._cookies.setdefault('client', {})

        @property
        def remote_addr(self) -> Tuple[str, int]:
            """
            # `Tuple(IP, port)` клиента
            
            :return: Tuple[str, int]
            """
            return self._data.get("remote_addr", ())
        
        @property
        def ip(self) -> str:
            """
            # IP клиента
            
            :return: str
            """
            return self._data.get("remote_addr", ())[0]
        
        @property
        def port(self) -> int:
            """
            # Port клиента
            
            :return: int
            """
            return self._data.get("remote_addr", ())[1]
        
        @property
        def type(self) -> Literal['net', 'client', 'server']:
            """
            # Тип клиента

            - `net` - Пользователи и другие службы сети `GN`

            - `client` - Пользователи напрямую. Без использования прокси серверов сети `GN`

            - `server` - Другие `origin` сервера сети `GN`
                
            :return: Literal['net', 'client', 'server']
            """
            return self.model_client_types[self._data['client-type']]
        
        @property
        def type_int(self) -> Literal[1, 4, 2]:
            """
            # Тип клиента (int)

            - `1` - net - Пользователи и другие службы сети `GN`

            - `4` - client - Пользователи напрямую. Без использования прокси серверов сети `GN`

            - `2` - server - Другие `origin` сервера сети `GN`
            
            :return: int
            """
            return self._data['client-type']

        @property
        def domain(self) -> Optional[str]:
            """
            # Домен объекта

            Для пользователей домен строится `<{gwisid}>~gwis`

            `None`, если запрос не поддерживает подпись домена
            
            :return: Optional[str]
            """
            return self._data.get("domain", None)

    def serialize(self, version: int = 0) -> bytes:
        if self._transport is None: self.setTransport()
        if self._route is None: self.setRoute()

        if self._payload is not None:
            payload = serialize(self._payload)
        else:
            payload = None
        
        cookies = {}
        
        if self._cookies is not None:
            cookies.update(self._cookies)

        if cookies != {}:
            raw_cookies = serialize(cookies)
        else:
            raw_cookies = None

        return pack_gnrequest(
            version,
            self._transport,
            self._route,
            self._method,
            self.url.toString().encode(),
            payload,
            raw_cookies
        )

    @staticmethod
    def deserialize(data: bytes) -> 'GNRequest':
        d = unpack_gnrequest(data)

        version =  d['version']

        if version == 0:
            transport =  d['transport']
            method =  d['method']
            route =  d['route']
            url =  d['url']
            cookies =  d['cookies']
            payload =  d['payload']


            r = GNRequest(
                transport=transport,
                route=route,
                method=method,
                url=Url(url.decode()),
                payload=deserialize(payload) if payload is not None else None,
                cookies=deserialize(cookies) if cookies is not None else None
            )
            return r
        else:
            raise Exception(f'Unsupported GNRequest version: {version}')

    @property
    def method(self) -> str:
        """
        # Метод запроса

        GET, POST, PUT, DELETE и т.д.
        """
        return self._method
    
    def setMethod(self, method: str):
        """
        # Метод запроса
        
        :param method: Метод запроса (GET, POST, PUT, DELETE и т.д.)
        """
        self._method = method
    
    @property
    def url(self) -> Url:
        """
        # URL запроса.
        """
        return self._url

    def setUrl(self, url: Url):
        """
        # URL запроса
        
        :param url: `URL` запроса в виде объекта `Url`.
        """
        self._url = url

    @property
    def payload(self) -> Optional[SerializableType]:
        """
        # Полезная нагрузка запроса

        `Dict`, `List`, `bytes`, `int`, `str` и другие типы с поддержкой байтов.

        Все поддерживаемые типа описанны в `KeyisBTools.models.serialization.SerializableType`
        
        Если полезная нагрузка не установлена, возвращает None.
        """
        return self._payload

    def setPayload(self, payload: Optional[dict]):
        """
        # Полезная нагрузка запроса

        `Dict`, `List`, `bytes`, `int`, `str` и другие типы с поддержкой байтов.

        Все поддерживаемые типа описанны в `KeyisBTools.models.serialization.SerializableType`

        :param payload: Dict с поддержкой байтов.
        """
        self._payload = payload

    @property
    def cookies(self) -> Optional[dict]:
        return self._cookies

    def setCookies(self, cookies: dict):
        self._cookies = cookies
        
    @property
    def transportObject(self) -> GNTransportProtocol:
        """
        # Транспортный протокол (объект)

        `GN` протокол используется для подключения к сети `GN`.
        """
        return parse_gn_protocol(self._transport)

    @property
    def transport(self) -> str:
        """
        # Транспортный протокол.

        """
        return self._transport
    
    def setTransport(self, transport: Optional[str] = None):
        """
        Устанавливает `GN` протокол.

        :param transport: `GN` протокол (например, '`gn:tcp:quik`', '`gn:quik:real`',..).

        Если не указан, используется `gn:quik:real`.
        """
        if transport is None:
            transport = 'gn:quik:real'
        self._transport = transport

    @property
    def route(self) -> Optional[str]:
        """
        # Маршрут запроса.

        Маршрут используется для определения пути запроса в сети `GN`.

        Если маршрут не установлен, возвращает `None`.
        """
        return self._route
    
    def setRoute(self, route: Optional[str] = None):
        """
        # Маршрут запроса.

        :param route: Маршрут запроса (например, `gn:net`).

        Если не указан, используется `gn:net`.
        """
        if route is None:
            route = 'gn:net'
        self._route = route


    def __repr__(self):
        return f"<GNRequest [{self._method} {self._url}] [{self._transport}]>"

class GNResponse(Exception):
    """
    # Ответ на запрос для сети `GN`
    """
    def __init__(self,
                 command: Union[str, int, bool, bytes],
                 payload: Optional[Union[SerializableType, TempDataGroup, TempDataObject]] = None,
                 cookies: Optional[dict] = None
                 ):
        
        """
        # Ответ на запрос для сети `GN`
        """
        self._command = command
        self._payload = payload
        self._cookies = cookies

        self.command = CommandObject(command)
        """
        # Команда запроса `CommandObject`
        """

    async def assembly(self):
        if self._payload is not None:
            if isinstance(self._payload, TempDataObject):
                self._payload = await self._payload.serialize()
            elif isinstance(self._payload, TempDataGroup):
                await self._payload.assemble()
                self._payload = self._payload.serialize()
            else:
                self._payload = serialize(self._payload)

    def serialize(self) -> bytes:
        if self._cookies is not None:
            cookies = serialize(self._cookies)
        else:
            cookies = None
        
        if not isinstance(self._payload, bytes):
            raise ValueError('GNResponse is not assembled')

        return pack_gnresponse(
            version=0,
            command=self._command,
            payload=self._payload,
            cookies=cookies
        )
    
    @staticmethod
    def deserialize(data: bytes) -> 'GNResponse':
        return GNResponse(*unpack_gnresponse(data))
    
    @property
    def payload(self) -> Optional[Union[SerializableType, TempDataGroup, TempDataObject]]:
        return self._payload
    
    @property
    def cookies(self) -> Optional[dict]:
        return self._cookies
    
    def __repr__(self):
        return f"<GNResponse [{self._command}]>"
    
    def __str__(self) -> str:
        return f"[GNResponse]: {self._command} {self._payload}"


from .fastcommands import AllGNFastCommands

class CommandObject(AllGNFastCommands):
    def __init__(self, value: Union[str, int, bool, bytes]):
        if not isinstance(value, (str, int, bool, bytes)):
            raise TypeError("Command must be str, int or bool")
        
        self.value = value
        """
        # Значение команды
        """

    def __getattribute__(self, name: str):
        if name == 'ok':
            return self.__bool__()
        if name in AllGNFastCommands.__dict__.keys():
            a: Type[AllGNFastCommands.ok] = getattr(AllGNFastCommands, name)
            return self.value == a.cls_command
        return super().__getattribute__(name)

    def __eq__(self, other):
        if isinstance(other, CommandObject):
            return self.value == other.value
        return self.value == other
    

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        
        if isinstance(self.value, bool):
            return self.value
        elif isinstance(self.value, int):
            return self.value == 200
        elif isinstance(self.value, str):
            return self.value == 'ok' or self.value.endswith((':ok', ':200'))
        else:
            return True
        
    def __str__(self) -> str:
        if isinstance(self.value, str):
            return self.value
        elif isinstance(self.value, bool):
            if self.value:
                return 'ok'
            else:
                return 'gn:error:false'
        elif isinstance(self.value, int):
            if self.value == 200:
                return 'ok'
            else:
                return f'gn:error:{self.value}'
        else:
            return self.value.decode('utf-8')
            
    def __repr__(self):
        return f"CommandObject({self.value!r})"

    def _serializebleType(self):
        if isinstance(self.value, str):
            if self.value == 'ok':
                return True
            return self.value
        else:
            return self.value