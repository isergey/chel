# encode: utf-8


class DataSubfield(object):
    def __init__(self, code, data):
        self.__code = code
        self.__data = data

    def get_code(self):
        return self.__code

    def get_data(self):
        return self.__data

    def __str__(self):
        return u'$%s%s' % (self.__code, self.__data)

    def to_html(self):
        return u'<span class="subfield_code">$%s</span>%s' % (self.__code, self.__data)


class ExtendedSubfield(object):
    def __init__(self, code, fields=None):
        if fields is None:
            fields = list()
        self.__code = code
        self.__fields = fields

    def get_code(self):
        return self.__code

    def get_fields(self, tag=None):
        if not tag:
            return self.__fields
        return [field for field in self.__fields if field.get_tag() == tag]

    def __str__(self):
        lines = ['$' + self.__code]
        for field in self.__fields:
            lines.append(u"\t" + str(field))
        return u"\n".join(lines)

    def to_html(self):
        lines = [u'<br/>&nbsp;&nbsp;&nbsp;&nbsp;<span class="subfield_code">$%s</span>' % self.__code]
        for field in self.__fields:
            lines.append(u"&nbsp;&nbsp;&nbsp;&nbsp;" + field.to_html())
        return u"".join(lines)

    def __getitem__(self, item):
        uitem = str(item)
        fields = []
        for field in self.__fields:
            if field.get_tag() == uitem:
                fields.append(field)
        return fields


class ControlField(object):
    def __init__(self, tag, data):
        self.__tag = tag
        self.__data = data

    def get_tag(self):
        return self.__tag

    def get_data(self):
        return self.__data

    def __str__(self):
        return u'%s %s' % (self.__tag, self.__data)

    def to_html(self):
        return u'<span class="field_tag">%s</span> %s' % (self.__tag, self.__data)


class DataField(object):
    def __init__(self, tag, ind1=' ', ind2=' ', subfields=None):
        if subfields is None:
            subfields = []
        self.__tag = tag
        self.__ind1 = ind1
        self.__ind2 = ind2
        self.__subfields = subfields

    def get_tag(self):
        return self.__tag

    def get_ind1(self):
        return self.__ind1

    def get_ind2(self):
        return self.__ind2

    def get_subfields(self, code=None):
        if not code:
            return self.__subfields
        return [subfield for subfield in self.__subfields if subfield.get_code() == code]

    def set_subfields(self, subfields):
        self.__subfields = subfields

    def get_record(self):
        fields = []
        for subfield in self.__subfields:
            if isinstance(subfield, ExtendedSubfield):
                fields += subfield.get_fields()
        return Record(fields=fields)

    def append_subfield(self, subfield):
        self.__subfields.append(subfield)

    def __str__(self):
        lines = [u'%s %s%s' % (self.__tag, self.__ind1.replace(u' ', u'#'), self.__ind2.replace(u' ', u'#'))]
        for subfield in self.__subfields:
            lines.append(str(subfield))
        return ' '.join(lines)

    def to_html(self):
        lines = [u'<span class="field_tag">%s</span> <span class="indicators">%s%s<span>' % (
            self.__tag, self.__ind1.replace(u' ', u'#'), self.__ind2.replace(u' ', u'#'))]
        for subfield in self.__subfields:
            lines.append(subfield.to_html())
        return ' '.join(lines)

    def __getitem__(self, item):
        uitem = item
        subfields = []
        for subfield in self.__subfields:
            if subfield.get_code() == uitem:
                subfields.append(subfield)
        return subfields


class Record(object):
    def __init__(self, leader=u'00000       00000       ', fields=None):
        if fields is None:
            fields = []
        self.__errors = []
        self.__leader = leader
        self.__fields = fields

    def get_leader(self):
        return self.__leader

    def get_fields(self, tag=None):
        if not tag:
            return self.__fields
        return [field for field in self.__fields if field.get_tag() == tag]

    def add_fields(self, fields=None):
        if fields is None:
            fields = list()
        self.__fields += fields

    def __str__(self):
        lines = [self.__leader]
        for field in self.__fields:
            lines.append(str(field))
        return u"\n".join(lines)

    def to_html(self):
        lines = [u'<div class="leader">%s</div>' % self.__leader.replace(u' ', u'&nbsp;')]
        for field in self.__fields:
            lines.append(u"<div class='field'>%s</div>" % field.to_html())
        return u"".join(lines)

    def set_errors(self, errors):
        self.__errors = errors

    def get_errors(self):
        return self.__errors

    def __getitem__(self, item):
        attr = getattr(self, item, None)
        if attr:
            return attr
        uitem = item
        fields = []
        for field in self.__fields:
            if field.get_tag() == uitem:
                fields.append(field)
        return fields
