from typing import List, Optional, Dict, Union, Set
import asyncio, os, time
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, constant_time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import hashlib

from KeyisBTools.cryptography.sign import s2          # как у тебя
from KeyisBTools.cryptography import m1               # как у тебя

# from ._app import GNRequest
from gnobjects.net.objects import Url, GNRequest
from KeyisBTools.cryptography.bytes import hash3

# ----- Fast helpers -----
import random
from typing import List, Optional, Dict, Union, Set, Deque, Tuple
from collections import deque







def _pack(parse_ver: int, enc_ver: int) -> bytes:
    if not (0 <= parse_ver <= 0xF):
        raise ValueError("parse_ver должен быть 0..15 (4 бита)")
    if not (0 <= enc_ver <= 0xF):
        raise ValueError("enc_ver должен быть 0..15 (4 бита)")

    value = ((parse_ver & 0xF) << 4) | (enc_ver & 0xF)
    return value.to_bytes(1, "big")


def _unpack(data: bytes):
    if len(data) < 1:
        raise Exception('len < 1')

    value = data[0]
    parse_ver = (value >> 4) & 0xF
    enc_ver = value & 0xF
    return parse_ver, enc_ver



class KDCObject:
    """
    Две схемы:
      Stable (legacy, для доменов из set_stable_domains): h(8)|sig(164)|dom_h(64)|m1.encrypt(...)
      Fast (по умолчанию для остальных):
        init: h(8)|0xA1|sig(164)|dom_h(64)|nonce(12)|CT|tag(16)
        data: h(8)|0xA0|dom_h(64)|nonce(12)|CT|tag(16)
    """
    def __init__(self, domain: str, kdc_domain: str, kdc_key: bytes,
                 requested_domains: List[str], active_key_synchronization: bool = True):
        self._domain = domain
        self._kdc_domain = kdc_domain
        self._requested_domains = requested_domains
        self._active_key_synchronization = active_key_synchronization

        from ._client import AsyncClient
        #from GNServer import AsyncClient
        self._client = AsyncClient(domain)
        self._client.setKDC(self)

        self._datax_domain_keyId = {}
        self._datax_keyId_key = {}

        self._encryption_type: Dict[str, int] = {}
        self._domain_hkdf_cache: Dict[Tuple[int, str], bytes] = {}


        self._datax_domain_keyId[kdc_domain] = 0
        self._datax_keyId_key[0] = kdc_key

    def setDomainEcryptionType(self, domains: Dict[str, int]) -> None:
        self._encryption_type = domains

    def addDomainEcryptionType(self, domain: str, version: int) -> None:
        self._encryption_type[domain] = version

    # ---- Инициализация/обновление KDC ----
    async def addServers(self, servers_keys: Optional[Dict[str, bytes]] = None,
                   requested_domains: Optional[List[str]] = None): # type: ignore
        if requested_domains is not None:
            self._requested_domains += requested_domains

        if servers_keys is not None:
            for i in list(self._requested_domains):
                if i in servers_keys:
                    self._requested_domains.remove(i)
        else:
            servers_keys = {}

        self._datax_domain_keyId.update(servers_keys)

        if len(self._requested_domains) > 0:
            await self.requestKDC(self._requested_domains) # type: ignore


    async def requestKDC(self, domain_or_hash: Union[str, int, List[Union[str, int]]]):

        if not isinstance(domain_or_hash, list):
            domain_or_hash = [domain_or_hash]

        r = await self._client.request(GNRequest('GET', Url(f'gn://{self._kdc_domain}/api/sys/server/keys'),
                                                payload=domain_or_hash))
        if not r.command.ok:
            print(f'ERROR: {r.command} {r.payload}')
            raise r
        
        if not isinstance(r.payload, dict):
            raise Exception('r.payload is not dict')

        self._datax_domain_keyId.update(r.payload)



    def getKey(self, domain_or_id: Union[str, int]) -> bytes:
        if isinstance(domain_or_id, str):
            return self._datax_keyId_key[self._datax_domain_keyId[domain_or_id]]
        else:
            return self._datax_keyId_key[domain_or_id]

    def getDomainById(self, keyId: int) -> Optional[str]:
        for d, k in self._datax_domain_keyId.items():
            if k == keyId:
                return d
        return None
        

    async def checkKey(self, domain_or_id: Union[str, int]):
        if domain_or_id not in self._datax_domain_keyId:
            await self.requestKDC(domain_or_id)