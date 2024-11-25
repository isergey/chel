from typing import List, BinaryIO, Iterator

from ..record import Record, DataField, DataSubfield


class ReaderOptions:
    def __init__(self, encoding='utf-8', sort_fields=False, ignore_fields: List[str] = None, unknown_field_code='*'):
        self.encoding = encoding
        self.sort_fields = sort_fields
        self.ignore_fields = set(ignore_fields) if ignore_fields is not None else {'113', '907', '998'}
        self.unknown_field_code = unknown_field_code


class Reader:
    def __init__(self, options: ReaderOptions = ReaderOptions()):
        self.__encoding = options.encoding
        self.__sort_fields = options.sort_fields
        self.__ignore_fields = options.ignore_fields
        self.__unknown_field_code = '^' + options.unknown_field_code if options.unknown_field_code else ''

    @staticmethod
    def read_stream(stream: BinaryIO, options: ReaderOptions = ReaderOptions()) -> Iterator[Record]:
        return Reader(options=options).read(stream)

    def read(self, io: BinaryIO) -> Iterator[Record]:
        offset = 0
        while True:
            length_data = io.read(5)
            if len(length_data) < 5:
                break

            try:
                record_length = int(length_data)
            except ValueError as e:
                raise e

            record_data = io.read(record_length - 5)
            yield self.__read_record(length_data + record_data), offset
            offset += (5 + len(record_data))

    def __read_record(self, buff: bytes) -> Record:
        leader = self.__read_leader(buff)
        base_address = int(leader[12:17])

        offset = 24

        fields: List[DataField] = []

        while offset < base_address - 1:
            tag = buff[offset: offset + 3].decode(self.__encoding, 'replace')

            if self.__ignore_fields is not None and tag in self.__ignore_fields:
                offset += 12
                continue

            offset += 3
            field_length = int(buff[offset: offset + 4])
            offset += 4
            field_starting_position = int(buff[offset: offset + 5])
            offset += 5
            field_offset = base_address + field_starting_position

            fields.append(self.__decode_field(buff, offset=field_offset, length=field_length, tag=tag))

        return Record(
            leader=leader,
            fields=fields if not self.__sort_fields else sorted(fields, key=lambda f: int(f.get_tag()))
        )

    def __decode_field(self, buff: bytes, offset: int, length: int, tag: str) -> DataField:

        data = buff[offset: offset + length - 1].decode(self.__encoding, 'replace')

        if not data:
            return DataField(tag=tag, subfields=[])

        if data[0] == ' ':
            data = data.lstrip()

        if not data:
            return DataField(tag=tag, subfields=[])

        if data[0] != '^':
            data = self.__unknown_field_code + data

        return self.__decode_data_field(field_data=data, tag=tag)

    def __read_leader(self, buff: bytes) -> str:
        return str(buff[0:24], encoding=self.__encoding, errors='replace')

    # @staticmethod
    # def __decode_control_field(field_data: str, tag: str):
    #     return ControlField(tag=tag, data=field_data)
    #
    # @staticmethod
    # def __decode_default_field(field_data: str, tag: str):
    #     return DataField(tag=tag, subfields=[DataSubfield(code='a', data=field_data)])

    @staticmethod
    def __decode_data_field(field_data: str, tag: str):
        subfields: List[DataSubfield] = []
        for subfield_data in field_data.split('^'):
            if not subfield_data:
                continue

            code = subfield_data[0].lower()
            data = subfield_data[1:]

            subfields.append(DataSubfield(code=code, data=data))

        return DataField(tag=tag, subfields=subfields)
