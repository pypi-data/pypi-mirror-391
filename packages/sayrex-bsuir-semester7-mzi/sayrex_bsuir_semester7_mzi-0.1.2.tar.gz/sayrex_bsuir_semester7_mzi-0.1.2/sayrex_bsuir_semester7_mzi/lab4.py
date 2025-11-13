import numpy as np
import random
from typing import Tuple


class McElieceCryptosystem:
    def __init__(self, n: int = 7, k: int = 4, t: int = 1):
        self.n = n
        self.k = k
        self.t = t
        self.G = np.array(
            [
                [1, 1, 0, 1],
                [1, 0, 1, 1],
                [1, 0, 0, 0],
                [0, 1, 1, 1],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ],
            dtype=int,
        )
        self.H = np.array(
            [[1, 0, 1, 0, 1, 0, 1], [0, 1, 1, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1]],
            dtype=int,
        )
        self.R = np.array(
            [
                [0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 1],
            ],
            dtype=int,
        )
        print("— Генерация ключей (S, P, G_pub)...")
        self.S, self.S_inv, self.P, self.P_inv, self.G_public = self._generate_keys()
        print("   Готово\n")

    def _generate_non_singular_matrix(self, size: int) -> np.ndarray:
        while True:
            matrix = np.random.randint(0, 2, size=(size, size))
            if np.linalg.det(matrix) % 2 != 0:
                return matrix % 2

    def _generate_permutation_matrix(self, size: int) -> np.ndarray:
        indices = np.random.permutation(size)
        P = np.zeros((size, size), dtype=int)
        for i, j in enumerate(indices):
            P[i, j] = 1
        return P

    def _generate_keys(
        self,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        S = self._generate_non_singular_matrix(self.k)
        S_inv = np.linalg.inv(S).astype(int) % 2
        P = self._generate_permutation_matrix(self.n)
        P_inv = np.linalg.inv(P).astype(int) % 2
        G_public = (S @ self.G.T @ P) % 2
        return S, S_inv, P, P_inv, G_public.T

    def _add_errors(self, codeword: np.ndarray, num_errors: int) -> np.ndarray:
        error_positions = random.sample(range(self.n), num_errors)
        corrupted = codeword.copy()
        for pos in error_positions:
            corrupted[pos] = (corrupted[pos] + 1) % 2
        return corrupted

    def _decode_hamming(self, received: np.ndarray) -> np.ndarray:
        syndrome = (self.H @ received) % 2
        error_pos = int("".join(map(str, syndrome[::-1])), 2) - 1
        if error_pos >= 0:
            received[error_pos] = (received[error_pos] + 1) % 2
        return (self.R @ received) % 2

    def encrypt(self, message: np.ndarray) -> np.ndarray:
        if len(message) != self.k:
            raise ValueError(f"Сообщение должно быть длины {self.k}")
        codeword = (message @ self.G_public.T) % 2
        encrypted = self._add_errors(codeword, self.t)
        return encrypted

    def decrypt(self, ciphertext: np.ndarray) -> np.ndarray:
        if len(ciphertext) != self.n:
            raise ValueError(f"Шифротекст должен быть длины {self.n}")
        c_hat = (ciphertext @ self.P_inv) % 2
        m_hat = self._decode_hamming(c_hat)
        message = (m_hat @ self.S_inv) % 2
        return message

    def encrypt_bytes(self, data: bytes) -> bytes:
        print("— Шифрование данных...")
        print(f"   Размер исходных данных: {len(data)} байт")
        binary_str = "".join(f"{byte:08b}" for byte in data)
        original_length = len(binary_str)
        chunks = [binary_str[i : i + self.k] for i in range(0, len(binary_str), self.k)]
        print(f"   Параметры кода: n={self.n}, k={self.k}, t={self.t}")
        print(f"   Кол-во блоков: {len(chunks)}")
        encrypted_bits = []
        for chunk in chunks:
            if len(chunk) < self.k:
                chunk = chunk.ljust(self.k, "0")
            message = np.array([int(bit) for bit in chunk])
            encrypted = self.encrypt(message)
            encrypted_bits.extend(encrypted.astype(str))
        length_info = f"{original_length:032b}"
        encrypted_bits = list(length_info) + encrypted_bits
        encrypted_str = "".join(encrypted_bits)
        padding = (8 - len(encrypted_str) % 8) % 8
        encrypted_str += "0" * padding
        byte_chunks = [
            encrypted_str[i : i + 8] for i in range(0, len(encrypted_str), 8)
        ]
        out = bytes(int(chunk, 2) for chunk in byte_chunks)
        print(f"   Размер шифротекста: {len(out)} байт\n")
        return out

    def decrypt_bytes(self, data: bytes) -> bytes:
        print("— Дешифрование данных...")
        print(f"   Размер шифротекста: {len(data)} байт")
        binary_str = "".join(f"{byte:08b}" for byte in data)
        length_info = binary_str[:32]
        original_length = int(length_info, 2)
        binary_str = binary_str[32:]
        total_bits = len(binary_str)
        chunks_count = (total_bits + self.n - 1) // self.n
        print(f"   Ожидаемая длина (бит): {original_length}")
        print(f"   Кол-во блоков: {chunks_count}")
        actual_bits = chunks_count * self.n
        if len(binary_str) > actual_bits:
            binary_str = binary_str[:actual_bits]
        chunks = [binary_str[i : i + self.n] for i in range(0, len(binary_str), self.n)]
        decrypted_bits = []
        for chunk in chunks:
            if len(chunk) < self.n:
                chunk = chunk.ljust(self.n, "0")
            ciphertext = np.array([int(bit) for bit in chunk])
            decrypted = self.decrypt(ciphertext)
            decrypted_bits.extend(decrypted.astype(str))
        decrypted_str = "".join(decrypted_bits)[:original_length]
        byte_chunks = [
            decrypted_str[i : i + 8] for i in range(0, len(decrypted_str), 8)
        ]
        out = bytes(int(chunk, 2) for chunk in byte_chunks)
        print(f"   Размер расшифрованных данных: {len(out)} байт\n")
        return out


def encrypt_file(input_file: str, output_file: str, mc_eliece: McElieceCryptosystem):
    print(f"— Шифрование файла '{input_file}'")
    with open(input_file, "rb") as f:
        plaintext = f.read()
    print(f"   Размер: {len(plaintext)} байт")
    ciphertext = mc_eliece.encrypt_bytes(plaintext)
    with open(output_file, "wb") as f:
        f.write(ciphertext)
    print(f"   Файл зашифрован в '{output_file}' ({len(ciphertext)} байт)")


def decrypt_file(input_file: str, output_file: str, mc_eliece: McElieceCryptosystem):
    print(f"— Дешифрование файла '{input_file}'")
    with open(input_file, "rb") as f:
        ciphertext = f.read()
    print(f"   Размер: {len(ciphertext)} байт")
    plaintext = mc_eliece.decrypt_bytes(ciphertext)
    with open(output_file, "wb") as f:
        f.write(plaintext)
    print(f"   Файл расшифрован в '{output_file}' ({len(plaintext)} байт)")
    return plaintext


def create_test_file(filename: str, content: str = None):
    if content is None:
        content = "Пустой файл !№;%:?*()"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"— Создан файл '{filename}' (символов: {len(content)})")


def compare_files(file1: str, file2: str):
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        content1 = f1.read()
        content2 = f2.read()
    if content1 == content2:
        print("— Сравнение: файлы идентичны ✅")
        return True
    else:
        print("— Сравнение: файлы различны ❌")
        print(f"   Размер {file1}: {len(content1)} байт")
        print(f"   Размер {file2}: {len(content2)} байт")
        min_len = min(len(content1), len(content2))
        for i in range(min_len):
            if content1[i] != content2[i]:
                print(f"   Первое различие в байте {i}:")
                print(f"   {file1}: {content1[i]} (0x{content1[i]:02x})")
                print(f"   {file2}: {content2[i]} (0x{content2[i]:02x})")
                break
        else:
            if len(content1) != len(content2):
                print(f"   Файлы имеют разную длину")
        return False


def lab4(
        input_file: str,
        output_encrypted_file: str,
        output_decrypted_file: str,
):
    SOURCE_FILE = input_file
    ENCRYPTED_FILE = output_encrypted_file
    DECRYPTED_FILE = output_decrypted_file
    mc_eliece = McElieceCryptosystem(n=7, k=4, t=1)
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        input_text = f.read()
    create_test_file(SOURCE_FILE, input_text)
    encrypt_file(SOURCE_FILE, ENCRYPTED_FILE, mc_eliece)
    decrypt_file(ENCRYPTED_FILE, DECRYPTED_FILE, mc_eliece)
    files_match = compare_files(SOURCE_FILE, DECRYPTED_FILE)
    if files_match:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            original_text = f.read()
        with open(DECRYPTED_FILE, "r", encoding="utf-8") as f:
            decrypted_text = f.read()
        print(f"— Итог: файлы совпали. Пример текста: {repr(decrypted_text[:64])}")
    else:
        print("— Итог: файлы не совпадают")
