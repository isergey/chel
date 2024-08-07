# encoding: utf-8
from .constants import SUBFIELD_INDICATOR, END_OF_FIELD


class Subfield(object):
    def __init__(self, code, data):
        self.code = str(code)
        self.data = str(data)

    def to_dict(self):
        return ( self.code, self.data )

    def as_marc(self, to_encoding='utf-8'):
        """
        used during conversion of a field to raw marc
        """
        return SUBFIELD_INDICATOR + str(self.code) + self.data.encode(to_encoding)

    def __unicode__(self):
        return '$' + self.code + self.data

    def __str__(self):
        return str(self).encode('utf-8')


class LinkedSubfield(object):
    def __init__(self, code, field=None):
        self.code = str(code)
        self.field = field

    def to_dict(self):
        return (self.code, self.field.to_dict())

    def as_marc(self, to_encoding='utf-8'):
        """
        used during conversion of a field to raw marc
        """
        # cut last END_OF_FIELD byte
        if isinstance(self.field, ControlField):
            return SUBFIELD_INDICATOR + str(self.code) + self.field.as_marc()[0:-1]
        else:
            return SUBFIELD_INDICATOR + str(self.code) + str(self.field.tag) + self.field.as_marc()[0:-1]

    def __unicode__(self):
        return '$' + self.code + ' ' + str(self.field)

    def __str__(self):
        return str(self).encode('utf-8')


class Field(object):
    def __init__(self, tag):
        self.tag = str(tag)

    def to_dict(self):
        datafield_dict = {
            'tag': self.tag,
            'ind1': self.ind1,
            'ind2': self.ind2,
            'subfields': {}
        }

        for key in  sorted(self.subfields.keys()):
            for subfield in self.subfields[key]:
                if subfield.code not in datafield_dict['subfields']:
                    datafield_dict['subfields'][subfield.code] = []
                datafield_dict['subfields'][subfield.code].append(subfield.to_dict())

        return datafield_dict

class ControlField(Field):
    def __init__(self, tag, data):
        super(ControlField, self).__init__(tag)
        self.data = str(data)

    def as_marc(self, to_encoding='utf-8'):
        """
        used during conversion of a field to raw marc
        """
        return self.data.encode(to_encoding) + END_OF_FIELD

    def to_dict(self):
        return ( self.tag, self.data )

    def __unicode__(self):
        return '%s %s' % (self.tag, self.data)

    def __str__(self):
        return str(self).encode('utf-8')


class DataField(Field):
    def __init__(self, tag, subfields=[], ind1=' ', ind2=' '):
        super(DataField, self).__init__(tag)
        self.ind1 = str(ind1)
        self.ind2 = str(ind2)
        self.subfields = {}

        for subfield in subfields:
            if subfield.code not in self.subfields:
                self.subfields[subfield.code] = []
            self.subfields[subfield.code].append(subfield)
    def __getitem__(self, item):
        return self.subfields[item]


    def add_subfield(self, subfield):
        if subfield.code not in self.subfields:
            self.subfields[subfield.code] = []
        self.subfields[subfield.code].append(subfield)



    def as_marc(self, to_encoding='utf-8'):
        """
        used during conversion of a field to raw marc
        """

        marc = [str(self.ind1) + str(self.ind2)]
        for key in sorted(self.subfields.keys()):
            for subfield in self.subfields[key]:
                marc.append(subfield.as_marc(to_encoding))
        marc.append(END_OF_FIELD)
        return ''.join(marc)

    def __unicode__(self):
        ind1 = ind2 = None
        if self.ind1 == ' ':
            ind1 = '#'
        else:
            ind1 = self.ind1

        if self.ind2 == ' ':
            ind2 = '#'
        else:
            ind2 = self.ind2

        strings = []
        for key in  sorted(self.subfields.keys()):
            for subfield in self.subfields[key]:
                if isinstance(subfield, LinkedSubfield):
                    strings.append('\n    ' + str(subfield))
                else:
                    strings.append(str(subfield))

        return '%s %s%s %s' % (self.tag, ind1, ind2, ' '.join(strings))


    def __str__(self):
        return str(self).encode('utf-8')

#class LinkedField(Field):
#    super(LinkedField, self).__init__(tag)
