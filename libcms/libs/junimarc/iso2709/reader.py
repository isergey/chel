import logging
import io
from . import constants
from .. import record

logger = logging.getLogger('junimarc.iso2709.reader')

DECODE_ERROR_MODE = 'replace'


class Reader(object):
    def __init__(self, path, extended_subfield_code='', encoding='utf=8'):
        self.path = path
        self.encoding = encoding
        self.extended_subfield_code = extended_subfield_code
        self.errors = []
        self.offset = 0
        self.index = 0

    def get_total_records(self):
        total_records = 0
        with io.open(self.path, 'rb', buffering=32 * 1024) as fl:
            while True:
                buff = fl.read(32 * 1024)
                if not buff:
                    break
                for b in buff:
                    if b == constants.RECORD_TERMINATOR:
                        total_records += 1

                if total_records % 1000 == 0:
                    print('tr', total_records)

        return total_records

    def read(self):
        with io.open(self.path, 'rb', buffering=8 * 1024) as fl:
            record_bytes = []
            while True:
                buff = fl.read(32 * 1024)
                if not buff:
                    break
                for b in buff:
                    if b == constants.RECORD_TERMINATOR:
                        record_bytes.append(b)
                        rb = bytes(record_bytes)
                        try:
                            record = self.decode_record(rb)
                        except Exception as e:
                            self._log_error(str(e))
                            record = None

                        if record is not None:
                            record.set_errors(self.errors)
                            yield record

                        if self.errors:
                            self.errors = []
                        self.offset += len(record_bytes)
                        self.index += 1

                        record_bytes = []
                    else:
                        record_bytes.append(b)

    # def read(self):
    #     with io.open(self.path, 'rb', buffering=8 * 1024) as fl:
    #         while True:
    #             record_length_bytes = fl.read(5)
    #             if not record_length_bytes:
    #                 break
    #             if len(record_length_bytes) < 5:
    #                 self._log_error(u'Wrong record length')
    #
    #             try:
    #                 record_length = int(record_length_bytes)
    #             except ValueError as e:
    #                 self._log_error(e)
    #                 break
    #             record_bytes = fl.read(record_length - 5)
    #             total_record_length = len(record_bytes) + 5
    #             if total_record_length < record_length:
    #                 self._log_error(u'Total record length %s less then declared record length %s' % (
    #                     str(total_record_length), str(record_length)))
    #                 break
    #
    #             record = self.decode_record(bytearray(record_length_bytes + record_bytes))
    #             if record is not None:
    #                 record.set_errors(self.errors)
    #                 yield record
    #
    #             if self.errors:
    #                 self.errors = []
    #             self.offset += total_record_length
    #             self.index += 1

    def decode_record(self, record_bytes):
        record_bytes_length = len(record_bytes)
        if record_bytes_length < constants.LEADER_LENGTH:
            self._log_error(u'record bytes length less then leader length')
            return None

        try:
            record_length = int(record_bytes[0:5])
        except ValueError as e:
            self._log_error(e)
            return None

        if record_bytes_length < record_length:
            self._log_error(
                u'record bytes length less then declared record length ' + str(record_bytes_length) + ' ' + str(
                    record_length))
            return None

        try:
            base_address = int(record_bytes[12:17])
        except ValueError as e:
            self._log_error(e)
            return None

        leader = record_bytes[0: constants.LEADER_LENGTH]
        offset = constants.LEADER_LENGTH

        fields = []
        while offset < base_address - 1:
            tag = record_bytes[offset: offset + 3]
            offset += 3
            field_length = int(record_bytes[offset: offset + 4])
            offset += 4
            field_starting_position = int(record_bytes[offset: offset + 5])
            offset += 5
            field_offset = base_address + field_starting_position
            fields.append(
                self.decode_field(
                    tag.decode(self.encoding, DECODE_ERROR_MODE),
                    record_bytes[field_offset: field_offset + field_length - 1]
                )
            )

        jrecord = record.Record(leader=leader.decode(self.encoding, DECODE_ERROR_MODE), fields=fields)

        return jrecord

    def decode_field(self, tag, field_bytes):
        if int(tag) < 10:
            return self.decode_control_field(tag, field_bytes)
        else:
            return self.decode_data_field(tag, field_bytes)

    def decode_control_field(self, tag, field_bytes):
        return record.ControlField(tag, data=field_bytes.decode(self.encoding, DECODE_ERROR_MODE))

    def decode_data_field(self, tag, field_bytes):
        field_length = len(field_bytes)
        if field_length > 0:
            ind1 = chr(field_bytes[0])
            if ind1 == '#':
                ind1 = ' '
        else:
            ind1 = u' '

        if field_length > 1:
            ind2 = chr(field_bytes[1]).replace('#', ' ')
            if ind2 == '#':
                ind2 = ' '
        else:
            ind2 = u' '

        subfields = []
        field = record.DataField(tag=tag, ind1=ind1, ind2=ind2, subfields=subfields)

        if field_length > 3:
            start_of_subfield_index = 3
            end_of_subfield_index = start_of_subfield_index
            while end_of_subfield_index < field_length:
                if field_bytes[end_of_subfield_index] == constants.SUBFIELD_DELIMITER:
                    subfield_bytes = field_bytes[start_of_subfield_index: end_of_subfield_index]
                    if subfield_bytes:
                        subfields.append(self.decode_data_subfield(subfield_bytes))
                    end_of_subfield_index += 1
                    start_of_subfield_index = end_of_subfield_index
                else:
                    end_of_subfield_index += 1
            if start_of_subfield_index != end_of_subfield_index:
                subfield_bytes = field_bytes[start_of_subfield_index: end_of_subfield_index]
                if subfield_bytes:
                    subfields.append(self.decode_data_subfield(subfield_bytes))

        if self.extended_subfield_code and field.get_subfields(self.extended_subfield_code):
            self.decode_extended_subfield(field)
        return field

    def decode_data_subfield(self, subfield_bytes):
        code = chr(subfield_bytes[0])
        return record.DataSubfield(
            code=code,
            data=subfield_bytes[1: len(subfield_bytes)].decode(self.encoding, DECODE_ERROR_MODE)
        )

    def decode_extended_subfield(self, field):
        extended_subfields = []
        next_field = None
        extended_code = ''
        for subfield in field.get_subfields():
            code = subfield.get_code()
            data = subfield.get_data()
            if code == self.extended_subfield_code:
                extended_code = code
                if next_field is not None:
                    extended_subfields.append(record.ExtendedSubfield(code=extended_code, fields=[next_field]))
                    next_field = None

                if len(data) < 5:
                    continue

                tag = data[0: 3]
                try:
                    int_tag = int(tag)
                except ValueError as e:
                    self._log_error(e)
                    continue

                if int_tag < 10:
                    extended_subfields.append(
                        record.ExtendedSubfield(code=extended_code, fields=[record.ControlField(tag, data[3:])]))
                else:
                    next_field = record.DataField(
                        tag=tag,
                        ind1=data[3:4] or ' ',
                        ind2=data[4:5] or ' '
                    )
            else:
                if next_field is not None:
                    next_field.append_subfield(record.DataSubfield(code=code, data=data))

        if next_field is not None:
            extended_subfields.append(record.ExtendedSubfield(code=extended_code, fields=[next_field]))
        if extended_subfields:
            field.set_subfields(extended_subfields)

    def _log_error(self, message):
        log_message = '%s Offset %s Index %s' % (message, str(self.offset), self.index)
        self.errors.append(log_message)
        logger.error(log_message)
