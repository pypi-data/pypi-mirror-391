import struct
import binascii
from typing import List


class GOST3411:
    S_BOX = [
        [4, 10, 9, 2, 13, 8, 0, 14, 6, 11, 1, 12, 7, 15, 5, 3],
        [14, 11, 4, 12, 6, 13, 15, 10, 2, 3, 8, 1, 0, 7, 5, 9],
        [5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11],
        [7, 13, 10, 1, 0, 8, 9, 15, 14, 4, 6, 12, 11, 2, 5, 3],
        [6, 12, 7, 1, 5, 15, 13, 8, 4, 10, 9, 14, 0, 3, 11, 2],
        [4, 11, 10, 0, 7, 2, 1, 13, 3, 6, 8, 5, 9, 12, 15, 14],
        [13, 11, 4, 1, 3, 15, 5, 9, 0, 10, 14, 7, 6, 8, 2, 12],
        [1, 15, 13, 0, 5, 7, 10, 4, 9, 2, 3, 14, 6, 11, 8, 12],
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        self.h = [0] * 8
        self.s = [0] * 8
        self.n = [0] * 8
        self.buffer = bytearray()
        self.total_length = 0

    def _f(self, h: List[int], m: List[int]) -> List[int]:
        keys = self._generate_keys(h)
        state = m[:]
        for i in range(32):
            state = self._encrypt_round(state, keys[i])
        result = []
        for i in range(8):
            result.append((state[i] ^ h[i] ^ m[i]) & 0xFFFFFFFF)
        return result

    def _generate_keys(self, key: List[int]) -> List[int]:
        keys = []
        for i in range(8):
            keys.append(key[i])
        all_keys = []
        for i in range(32):
            if i < 24:
                all_keys.append(keys[i % 8])
            else:
                all_keys.append(keys[7 - (i % 8)])
        return all_keys

    def _encrypt_round(self, data: List[int], key: int) -> List[int]:
        temp = (data[0] + key) & 0xFFFFFFFF
        result = 0
        for i in range(8):
            s_box_input = (temp >> (4 * i)) & 0xF
            s_box_output = self.S_BOX[7 - i][s_box_input]
            result |= s_box_output << (4 * i)
        result = ((result << 11) | (result >> (32 - 11))) & 0xFFFFFFFF
        return [result ^ data[7]] + data[:7]

    def _add_modulo_2_32(self, a: List[int], b: List[int]) -> List[int]:
        result = []
        carry = 0
        for i in range(7, -1, -1):
            total = a[i] + b[i] + carry
            result.insert(0, total & 0xFFFFFFFF)
            carry = total >> 32
        return result

    def _process_block(self, block: bytes):
        m = []
        for i in range(0, 32, 4):
            m.append(struct.unpack("<I", block[i : i + 4])[0])
        h_prev = self.h[:]
        self.h = self._f(self.h, m)
        self.s = self._add_modulo_2_32(self.s, m)
        carry = 256
        for i in range(7, -1, -1):
            total = self.n[i] + carry
            self.n[i] = total & 0xFFFFFFFF
            carry = total >> 32

    def update(self, data: bytes):
        self.buffer.extend(data)
        self.total_length += len(data)
        while len(self.buffer) >= 32:
            block = self.buffer[:32]
            self.buffer = self.buffer[32:]
            self._process_block(block)

    def digest(self) -> bytes:
        padding_length = 32 - (len(self.buffer) % 32)
        if padding_length == 0:
            padding_length = 32
        padding = bytes([0x80] + [0] * (padding_length - 1))
        self.update(padding)
        length_bits = self.total_length * 8
        length_bytes = struct.pack("<Q", length_bits)
        self.update(length_bytes)
        result = bytearray()
        for i in range(8):
            final_val = (self.h[i] ^ self.s[i] ^ self.n[i]) & 0xFFFFFFFF
            result.extend(struct.pack("<I", final_val))
        self.reset()
        return bytes(result)

    def hexdigest(self) -> str:
        return binascii.hexlify(self.digest()).decode()


class SHA1:
    def __init__(self):
        self.reset()

    def reset(self):
        self.h0 = 0x67452301
        self.h1 = 0xEFCDAB89
        self.h2 = 0x98BADCFE
        self.h3 = 0x10325476
        self.h4 = 0xC3D2E1F0
        self.buffer = bytearray()
        self.total_length = 0

    def _left_rotate(self, n: int, b: int) -> int:
        return ((n << b) | (n >> (32 - b))) & 0xFFFFFFFF

    def update(self, data: bytes):
        self.buffer.extend(data)
        self.total_length += len(data)
        while len(self.buffer) >= 64:
            block = self.buffer[:64]
            self.buffer = self.buffer[64:]
            self._process_block(block)

    def _process_block(self, block: bytes):
        w = [0] * 80
        for i in range(16):
            w[i] = struct.unpack(">I", block[i * 4 : i * 4 + 4])[0]
        for i in range(16, 80):
            w[i] = self._left_rotate(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1)
        a = self.h0
        b = self.h1
        c = self.h2
        d = self.h3
        e = self.h4
        for i in range(80):
            if 0 <= i <= 19:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= i <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= i <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            else:
                f = b ^ c ^ d
                k = 0xCA62C1D6
            temp = (self._left_rotate(a, 5) + f + e + k + w[i]) & 0xFFFFFFFF
            e = d
            d = c
            c = self._left_rotate(b, 30)
            b = a
            a = temp
        self.h0 = (self.h0 + a) & 0xFFFFFFFF
        self.h1 = (self.h1 + b) & 0xFFFFFFFF
        self.h2 = (self.h2 + c) & 0xFFFFFFFF
        self.h3 = (self.h3 + d) & 0xFFFFFFFF
        self.h4 = (self.h4 + e) & 0xFFFFFFFF

    def digest(self) -> bytes:
        original_length = self.total_length * 8
        padding = bytes([0x80])
        while (len(self.buffer) + len(padding)) % 64 != 56:
            padding += bytes([0x00])
        padding += struct.pack(">Q", original_length)
        self.update(padding)
        result = struct.pack(">IIIII", self.h0, self.h1, self.h2, self.h3, self.h4)
        self.reset()
        return result

    def hexdigest(self) -> str:
        return binascii.hexlify(self.digest()).decode()


class HashChecker:
    def compute_hashes(self, data: bytes) -> dict:
        gost_hash = GOST3411()
        sha1_hash = SHA1()
        gost_hash.update(data)
        sha1_hash.update(data)
        return {"gost": gost_hash.hexdigest(), "sha1": sha1_hash.hexdigest()}

    def verify_integrity(self, original_data: bytes, stored_hashes: dict) -> bool:
        current_hashes = self.compute_hashes(original_data)
        integrity_ok = True
        results = {}
        for algo in ["gost", "sha1"]:
            if algo in stored_hashes:
                results[algo] = current_hashes[algo] == stored_hashes[algo]
                integrity_ok &= results[algo]
        return integrity_ok, results


def lab5():
    checker = HashChecker()
    test_messages = ["hello", "привет", "world", "мир"]

    for i, message in enumerate(test_messages, 1):
        print(f"\nТестовое сообщение № {i}: '{message}'")
        data = message.encode("utf-8")
        hashes = checker.compute_hashes(data)
        print(f"ГОСТ 34.11: {hashes['gost']}")
        print(f"SHA-1:      {hashes['sha1']}")
        integrity_ok, results = checker.verify_integrity(data, hashes)
    print(f"\nЛавинный эффект:")
    message1 = b"Hello World"
    message2 = b"Hello World!"
    hashes1 = checker.compute_hashes(message1)
    hashes2 = checker.compute_hashes(message2)
    print(f"Сообщение 1: {message1.decode()}")
    print(f"Сообщение 2: {message2.decode()}")
    print(f"Разница: 1 байт")
    gost_diff = sum(1 for a, b in zip(hashes1["gost"], hashes2["gost"]) if a != b) * 4
    sha1_diff = sum(1 for a, b in zip(hashes1["sha1"], hashes2["sha1"]) if a != b) * 4
    print(f"ГОСТ 34.11: {hashes1['gost']}")
    print(f"           {hashes2['gost']}")
    print(f"Изменение: {gost_diff} бит")
    print(f"SHA-1:      {hashes1['sha1']}")
    print(f"           {hashes2['sha1']}")
    print(f"Изменение: {sha1_diff} бит")