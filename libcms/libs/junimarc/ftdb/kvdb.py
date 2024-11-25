from typing import Dict, Optional, Generic, TypeVar, BinaryIO, Callable, Tuple
from threading import Lock

Key = TypeVar('Key')
Value = TypeVar('Value')


class KvDb(Generic[Key, Value]):
    def __init__(self, path: str, key_type='str', value_type='str'):
        self.__path = path
        self.__lock = Lock()
        self.__key_type = key_type
        self.__value_type = value_type
        self.__values: Dict[Key, Value] = {}

    def get(self, key: Key) -> Optional[Value]:
        return self.__values.get(key)

    def set(self, key: Key, value: Value):
        if not value:
            return
        self.__values[key] = value

    def entities(self):
        for k, v in self.__values.items():
            yield k, v

    def save(self):
        encoder = self.__encode_str_str

        if self.__key_type == 'str' and self.__value_type == 'str':
            pass
        elif self.__key_type == 'str' and self.__value_type == 'int':
            encoder = self.__encode_str_int
        elif self.__key_type == 'int' and self.__value_type == 'int':
            encoder = self.__encode_int_int
        elif self.__key_type == 'int' and self.__value_type == 'str':
            encoder = self.__encode_int_str
        else:
            ValueError(f'Wrong key value types: {self.__key_type}-{self.__value_type}')

        with self.__lock:
            with open(self.__path, 'wb', buffering=16 * 1024) as f:
                for k, v in self.__values.items():
                    encoder(k, v, f)

    def load(self):
        decoder: Callable[[BinaryIO], Tuple[Key, Value]] = self.__decode_str_str
        if self.__key_type == 'str' and self.__value_type == 'str':
            pass
            # elif self.__key_type == 'str' and self.__value_type == 'int':
            #     encoder = self.__encode_str_int
        elif self.__key_type == 'int' and self.__value_type == 'int':
            decoder = self.__decode_int_int
        # elif self.__key_type == 'int' and self.__value_type == 'str':
        #     encoder = self.__encode_int_str
        # else:
            ValueError(f'Wrong key value types: {self.__key_type}-{self.__value_type}')

        with self.__lock:
            self.__values = {}
            with open(self.__path, 'rb', buffering=16 * 1024) as f:
                while True:
                    k, v = decoder(f)
                    if k is None:
                        break
                    self.set(k, v)

    def __encode_str_str(self, k: str, v: str, out: BinaryIO):
        k_bytes = k.encode('utf-8')
        v_bytes = v.encode('utf-8')
        k_len = len(k_bytes)
        v_len = len(v_bytes)

        self.__write_header(k_len=k_len, v_len=v_len, out=out)

        out.write(k_bytes)
        out.write(v_bytes)

    def __encode_str_int(self, k: str, v: int, out: BinaryIO):
        k_bytes = k.encode('utf-8')
        v_bytes = v.to_bytes(length=4, byteorder='big')
        k_len = len(k_bytes)
        v_len = len(v_bytes)

        self.__write_header(k_len=k_len, v_len=v_len, out=out)

        out.write(k_bytes)
        out.write(v_bytes)

    def __encode_int_str(self, k: int, v: str, out: BinaryIO):
        k_bytes = k.to_bytes(length=4, byteorder='big', signed=True)
        v_bytes = v.encode('utf-8')
        k_len = len(k_bytes)
        v_len = len(v_bytes)

        self.__write_header(k_len=k_len, v_len=v_len, out=out)

        out.write(k_bytes)
        out.write(v_bytes)

    def __encode_int_int(self, k: int, v: int, out: BinaryIO):
        k_len_need_bytes = get_need_bytes(k)
        v_len_need_bytes = get_need_bytes(v)
        kv_length_byte_size = encode(k_len_need_bytes, v_len_need_bytes)
        try:
            k_bytes = k.to_bytes(length=k_len_need_bytes, byteorder='big', signed=False)
            v_bytes = v.to_bytes(length=v_len_need_bytes, byteorder='big', signed=False)
        except Exception as e:
            raise e
        out.write(kv_length_byte_size.to_bytes(1, byteorder='big', signed=False))
        out.write(k_bytes)
        out.write(v_bytes)

    def __write_header(self, k_len: int, v_len: int, out: BinaryIO):
        k_len_need_bytes = get_need_bytes(k_len)
        v_len_need_bytes = get_need_bytes(v_len)
        kv_length_byte_size = encode(k_len_need_bytes, v_len_need_bytes)

        out.write(kv_length_byte_size.to_bytes(1, byteorder='big'))
        out.write(k_len.to_bytes(k_len_need_bytes, byteorder='big', signed=False))
        out.write(v_len.to_bytes(v_len_need_bytes, byteorder='big', signed=False))

    def __read_header(self, inp: BinaryIO):

        kv_length_byte_size = inp.read(1)
        if not kv_length_byte_size:
            return None, None

        k_len_need_bytes, v_len_need_bytes = decode(int(kv_length_byte_size[0]))

        k_len_bytes = inp.read(k_len_need_bytes)
        if not k_len_bytes:
            return None, None

        k_len = int.from_bytes(k_len_bytes, byteorder='big', signed=False)

        v_len_bytes = inp.read(v_len_need_bytes)

        if not v_len_bytes:
            return None, None


        v_len = int.from_bytes(v_len_bytes, byteorder='big', signed=False)

        return k_len, v_len

    def __decode_str_str(self, inp: BinaryIO):
        k_len, v_len = self.__read_header(inp)
        if k_len is None:
            return None, None

        k_bytes = inp.read(k_len)
        k = k_bytes.decode('utf-8')
        v_bytes = inp.read(v_len)
        v = v_bytes.decode('utf-8')
        return k, v

    def __decode_int_int(self, inp: BinaryIO):
        k_bytes = inp.read(4)
        if not k_bytes:
            return None, None

        k = int.from_bytes(k_bytes, byteorder='big', signed=True)
        v_bytes = inp.read(4)
        v = int.from_bytes(v_bytes, byteorder='big', signed=True)
        return k, v

def get_need_bytes(v: int):
    if v <= 256:
        return 1

    if v <= 65536:
        return 2



    return need_bytes


def encode(n1, n2) -> int:
    """Закодировать два 4-битных числа в один байт."""
    if n1 < 0 or n1 > 15 or n2 < 0 or n2 > 15:
        raise ValueError("Числа должны быть в диапазоне от 0 до 15.")

    # Упаковка чисел с помощью побитового сдвига и операции OR
    encoded = (n1 << 4) | n2
    return encoded


def decode(encoded: int):
    """Декодировать один байт в два 4-битных числа."""
    n1 = (encoded >> 4) & 0x0F  # Получаем первые 4 бита
    n2 = encoded & 0x0F  # Получаем последние 4 бита
    return n1, n2