# encoding: utf-8
import requests
import simplejson


class SolrError(Exception): pass


class IndexField(object):
    def __init__(self, name, type, count):
        pass


class IndexStatus(object):
    def __init__(self, reponse_dict):
        self.__reponse_dict = reponse_dict

    def get_docs_count(self):
        pass

    def get_fields_in_index(self):
        pass



class FacetParams(object):

    def __init__(self):
        self.__fields = []
        self.__query = None
        self.__limit = 7
        self.__offset = 0
        self.__mincount = 1
        self.__range_start = None
        self.__range_end = None

    def add_field(self, field):
        """
        field (unicode)
        """
        self.__fields.append(field)


    @property
    def fields(self):
        return self.__fields


    @fields.setter
    def fields(self, fields):
        """
        fields (list)
        """
        self.__fields = list(fields)


    @property
    def query(self):
        return self.__query


    @query.setter
    def query(self, query):
        """
        query (unicode)
        """
        self.__query = query


    @property
    def limit(self):
        return self.__limit


    @limit.setter
    def limit(self, limit):
        """
        limit (int)
        """
        self.__limit = limit

    @property
    def offset(self):
        return self.__offset


    @offset.setter
    def offset(self, offset):
        """
        offset (int)
        """
        self.__offset = offset

    @property
    def mincount(self):
        return self.__mincount


    @mincount.setter
    def mincount(self, mincount):
        self.__mincount = mincount

    @property
    def range_start(self):
        return self.__range_start

    @range_start.setter
    def range_start(self, range_start):
        """
        range_start (int)
        """
        self.__range_start = range_start


    @property
    def range_end(self):
        return self.__range_end

    @range_end.setter
    def range_end(self, range_end):
        """
        range_end (int)
        """
        self.__range_end = range_end

    def get_dicted_params(self):
        params = {}
        if self.fields or self.query:
            params['facet'] = 'on'

        if self.fields:
            params['facet.field'] = self.fields

        if self.query:
            params['facet.query'] = self.query

        if self.mincount:
            params['facet.mincount'] = self.mincount

        if self.limit:
            params['facet.limit'] = self.limit

        if self.offset:
            params['facet.offset'] = self.offset

        if self.range_start:
            params['facet.range.start'] = self.range_start

        if self.range_end:
            params['facet.range.end'] = self.range_end
        return params


class SearchResults(object):

    def __init__(self, address, params):
        self.__address = address
        self.__params = params
        self._make_request()


    def __getitem__(self, slice):
        start = slice.start
        rows = slice.stop - start
        self.__params['start'] = start
        self.__params['rows'] = rows
        self._make_request()


    def _make_request(self):
#        if hasattr(self, 'response_dict'):
#            return
        r = requests.get(self.__address,params=self.__params)

        if r.status_code != 400:
            r.raise_for_status()

        response_dict = simplejson.loads(r.text, encoding='utf-8')
        if 'responseHeader' not in response_dict:
            raise SolrError(u'Solr request is wrong')

        if 'error' in response_dict:
            raise SolrError(response_dict['error']['msg'])

        self.response_dict = response_dict


    def count(self):
        # для django Paginator
        try:
            return self.get_num_found()
        except KeyError:
            return 9999

    def get_docs(self):
        return  self.response_dict['response']['docs']


    def get_qtime(self):
        return self.response_dict['responseHeader']['QTime']


    def get_num_found(self):
        return  int(self.response_dict['response']['numFound'])


    def get_facets(self):
        facets = {}
        facet_fields = self.response_dict['facet_counts']['facet_fields']
        for facet_title in facet_fields.keys():
            facet = facet_fields[facet_title]
            facets[facet_title] = []
            for i in xrange(1,len(facet), 2):
                facets[facet_title].append((facet[i-1], facet[i]))
        return facets

    def get_highlighting(self):
        return []



class Collection(object):
    def __init__(self, solr, name):
        self.__solr = solr
        self.__name = name

    def add(self, docs):
        address = self.__solr.get_base_url() + self.__name + '/update/json'
        data = simplejson.dumps(docs)
        headers = {'content-type': 'application/json'}
        r = requests.post(address, data=data, headers=headers)
        r.raise_for_status()


    def delete(self, ids=list()):
        address = self.__solr.get_base_url() + self.__name + '/update/json'
        for id in ids:
            data = simplejson.dumps({'delete':{'id': unicode(id)}})
            headers = {'content-type': 'application/json'}
            r = requests.post(address, data=data, headers=headers)
            r.raise_for_status()

    def commit(self):
        address = self.__solr. get_base_url() + self.__name + '/update/json?commit=true'
        r = requests.get(address)
        r.raise_for_status()

    def rollback(self):
        address = self.__solr. get_base_url() + self.__name + '/update/json?rollback=true'
        r = requests.get(address)
        r.raise_for_status()

    def search(self, query, fields=list(), faset_params=None, hl=[], sort=[], start=0, rows=10):
        address = self.__solr. get_base_url() + self.__name + '/select/'
        params = {}
        params['q'] = query
        params['fl'] = u','.join(fields)
        params['wt'] = 'json'
        params['start'] = start
        params['rows'] = rows

        if sort:
            params['sort'] = u','.join(sort)

        if faset_params:
            params.update(faset_params.get_dicted_params())



        return SearchResults(address, params)

class Solr(object):

    """
    Класс для работы с Solr

    base_url - адрес solr.
    """
    def __init__(self, base_url):
        if base_url[-1] != '/':
            base_url+='/'
        self.__base_url = base_url

    def get_base_url(self):
        return self.__base_url

    def get_collection(self, name):
        return Collection(self, name)



def escape(string):
    special = [
        u'\\',
        u'+',
        u'-',
        u'&&',
        u'||',
        u'!',
        u'(',
        u')',
        u'{',
        u'}',
        u'[',
        u']',
        u'^',
        #u'"',
        u'~',
        u'?',
        u':'
    ]
    for s in special:
        string = string.replace(s,'\\'+s)
    return string