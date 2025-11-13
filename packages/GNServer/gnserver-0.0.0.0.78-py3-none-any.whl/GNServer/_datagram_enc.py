
import os
import time
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from typing import Optional, Callable
from .models import KDCObject

class DatagramEncryptor:
    def __init__(self, kdc: KDCObject, selfDomain: str, callback_domain: Optional[Callable[[str]]] = None):
        self.counter = 0 # 8B
        self.kdc = kdc
        self.domain = selfDomain
        self._callback_domain = callback_domain
        print(f'Создан DatagramEncryptor selfDomain: {selfDomain}, callback_domain: {callback_domain}')

    async def setKeyById(self, keyId: int):
        print(f"setKeyById: {keyId}")
        await self.kdc.checkKey(keyId)
        self.keyId = keyId

        key = self.kdc.getKey(keyId)
        
        DestDomain = self.kdc.getDomainById(keyId)

        self._key_in = HKDF(algorithm=hashes.SHA3_512(), length=32, salt=DestDomain.encode() + self.domain.encode(), info=b'gn:DgEncryptor').derive(key)
        self._key_out = HKDF(algorithm=hashes.SHA3_512(), length=32, salt=self.domain.encode() + DestDomain.encode(), info=b'gn:DgEncryptor').derive(key)

        if self._callback_domain is not None:
            self._callback_domain(DestDomain)


    def _make_nonce(self) -> bytes: # 15B
        now = int(time.time()) & 0xFFFFFFFFFF
        self.counter = (self.counter + 1) & 0xFFFFFFFFFFFFFFFF
        return now.to_bytes(5, "big") + self.counter.to_bytes(8, "big") + os.urandom(2)
    
    def encrypt(self, packet: bytes) -> bytes:
        nonce = self._make_nonce()
        cipher = AES.new(self._key_out, AES.MODE_OCB, nonce=nonce, mac_len=16)
        ciphertext, tag = cipher.encrypt_and_digest(packet)
        return nonce + ciphertext + tag

    def decrypt(self, packet: bytes) -> bytes:
        if len(packet) < 15 + 16:
            raise ValueError("Packet too short")
        nonce = packet[:15]
        tag = packet[-16:]
        ciphertext = packet[15:-16]
        cipher = AES.new(self._key_in, AES.MODE_OCB, nonce=nonce, mac_len=16)
        return cipher.decrypt_and_verify(ciphertext, tag)


import asyncio
from typing import Optional, Callable

from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.connection import QuicConnection, NetworkAddress




class EncryptedQuicProtocol(QuicConnectionProtocol):
    def __init__(
        self,
        quic: QuicConnection,
        dgEncryptor: DatagramEncryptor,
        stream_handler: Optional[
            Callable[[asyncio.StreamReader, asyncio.StreamWriter], None]
        ] = None,
    ) -> None:
        super().__init__(quic=quic, stream_handler=stream_handler)
        self._dgEncryptor = dgEncryptor

        self._is_initial = False
        self._upd_datagram_size = 1200

        self._gn_protocol_version = 0 # max 127 # 7b # encoding and ecryption info

        self.construct_initial()

    def construct_initial(self) -> None:
        data = bytearray()

        b0 = ((self._gn_protocol_version & 0x7F) << 1) | (True & 0x01)
        data.append(b0)


        body = bytearray()
        body.extend(int(0).to_bytes(8, 'big'))
        body.extend(self._dgEncryptor.keyId.to_bytes(8, 'big'))


        length_body = len(body)
        _b = ((length_body & 0x3FF) << 6) | (0 & 0x3F)
        b1_2 = _b.to_bytes(2, 'big')
        data.extend(b1_2)
        data.extend(body)

        self.__init_data = data

        all_length = len(data)

        
        self._quic._max_datagram_size = self._upd_datagram_size - all_length - 31

    def send_initial(self, quic_packet: bytes, addr: NetworkAddress) -> None:
        

        enc = self._dgEncryptor.encrypt(quic_packet) # upd_datagram_size - all_length

        data = self.__init_data + enc
        
        self._transport.sendto(data, addr)
        self._is_initial = True
        
        self._quic._max_datagram_size = self._upd_datagram_size - 32 # 1B + 15B + 16B

    def encodeDatagram(self, packet: bytes) -> bytes:
        # 7 - 1: version
        # 0: is sys packet
        b0 = ((self._gn_protocol_version & 0x7F) << 1) | (False & 0x01)
        dt = bytes([b0]) + packet
        enc = self._dgEncryptor.encrypt(dt)
        return enc

    def transmit(self) -> None:
        self._transmit_task = None

            
        for data, addr in self._quic.datagrams_to_send(now=self._loop.time()):
            if not self._is_initial:
                self.send_initial(data, addr)
            else:
                self._transport.sendto(self.encodeDatagram(data), addr)


        # re-arm timer
        timer_at = self._quic.get_timer()
        if self._timer is not None and self._timer_at != timer_at:
            self._timer.cancel()
            self._timer = None
        if self._timer is None and timer_at is not None:
            self._timer = self._loop.call_at(timer_at, self._handle_timer)
        self._timer_at = timer_at

    def datagram_received(self, data: bytes, addr: NetworkAddress) -> None:
        # обёртка — ставим задачу в event loop
        self._loop.create_task(self._handle_datagram(data, addr))


    async def _handle_datagram(self, data: bytes, addr: NetworkAddress) -> None:
        
        value = (data[0] >> 1) & 0x7F
        if value != self._gn_protocol_version:
            print(f"GN Prequic: UPD Version mismatch {value} != {self._gn_protocol_version}")
            return
        
        sysPacket = data[0] & 0x01
        if sysPacket: # если системный пакет.
            unpacked = int.from_bytes(data[1:3], 'big')
            length_body = (unpacked >> 6) & 0x3FF
            _ = unpacked & 0x3F
            body = data[3:length_body]
            data = data[3 + length_body:]

            commnd_id = int.from_bytes(body[:8], 'big')

            if commnd_id == 0: # initial

                key_id = int.from_bytes(body[8:16], 'big')
                await self._dgEncryptor.setKeyById(key_id)


        try:
            dec = self._dgEncryptor.decrypt(bytes(data)) # type: ignore
        except Exception:
            print("GN Prequic: UPD Decryption error")
            return

        self._quic.receive_datagram(dec, addr, now=self._loop.time())
        self._process_events()
        self.transmit()
