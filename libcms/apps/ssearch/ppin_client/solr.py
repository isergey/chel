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
        # if self.fields or self.query:
        #     params['facet'] = 'on'

        if self.fields:
            params['facet'] = self.fields

        # if self.query:
        #     params['facet.query'] = self.query
        #
        # if self.mincount:
        #     params['facet.mincount'] = self.mincount
        #
        if self.limit:
            params['limit'] = self.limit

        if self.offset:
            params['offset'] = self.offset
        #
        # if self.range_start:
        #     params['facet.range.start'] = self.range_start
        #
        # if self.range_end:
        #     params['facet.range.end'] = self.range_end
        return params


class SearchResults(object):
    def __init__(self, address, params):
        self.__address = address
        self.__params = params
        self._make_request()


    def __getitem__(self, slice):
        start = slice.start
        rows = slice.stop - start
        self.__params['offset'] = start
        self.__params['limit'] = rows
        self._make_request()

    def _make_request(self):
#        if hasattr(self, 'response_dict'):
#            return
        r = requests.get(self.__address, params=self.__params)

        if r.status_code != 400:
            r.raise_for_status()
        response_dict = simplejson.loads(r.text, encoding='utf-8')
        # if 'responseHeader' not in response_dict:
        #     raise SolrError(u'Solr request is wrong')

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
        try:
            return  self.response_dict['ids']
        except KeyError:
            return None

    def get_qtime(self):
        return None
        #return self.response_dict['responseHeader']['QTime']

    def get_num_found(self):
        return int(self.response_dict['hits'])

    def get_facets(self):
        try:
            facets = {}
            if 'facets' in self.response_dict:
                facet_fields = self.response_dict['facets']
                for facet in facet_fields:
                    facets[facet['name']] = []
                    for fvalue in facet['values']:
                        facets[facet['name']].append((fvalue['title'], fvalue['count']))

                # facet = facet_fields[facet_title]
                # facets[facet_title] = []
                # for i in xrange(1,len(facet), 2):
                #     facets[facet_title].append((facet[i-1], facet[i]))
            if 'values' in self.response_dict and 'name' in self.response_dict:
                facets[self.response_dict['name']] = []
                for fvalue in self.response_dict['values']:
                    facets[self.response_dict['name']].append((fvalue['title'], fvalue['count']))

            return facets
        except KeyError:
            return {}

    def get_highlighting(self):
        try:
            return self.response_dict['highlighting']
        except KeyError:
            return {}


class Collection(object):
    def __init__(self, solr, name):
        self.__solr = solr
        self.__name = name

    def add(self, docs):
        address = self.__solr.get_base_url() + self.__name + '/update/json'
        data=simplejson.dumps(docs)
        headers = {'content-type': 'application/json'}
        r = requests.post(address, data=data, headers=headers)
        r.raise_for_status()


    def delete(self, collection, ids=list()):
        pass

    def commit(self):
        address = self.__solr. get_base_url() + self.__name + '/update/json?commit=true'
        r = requests.get(address)
        r.raise_for_status()

    def rollback(self):
        address = self.__solr. get_base_url() + self.__name + '/update/json?rollback=true'
        r = requests.get(address)
        r.raise_for_status()

    def search(self, query=None, sc=None, fields=list(), faset_params=None, start=0, hl=list(), sort=list(), rows=10):
        address = self.__solr. get_base_url() + self.__name + '/'
        params = {}
        if query:
            params['q'] = query
        if sc:
            params['sc'] = sc
        # params['fl'] = u','.join(fields)
        # params['wt'] = 'json'
        params['offset'] = start
        params['limit'] = rows

        if sort:
            params['sort'] = sort
        #
        if hl:
            #params['hl'] = 'true'
            params['highlight'] = hl
            #params['hl.simple.pre'] = u"<em>"
            #params['hl.simple.post'] = u"</em>"

        if faset_params:
            params.update(faset_params.get_dicted_params())


        return SearchResults(address, params)

    def load_more_facets(self, query=None, sc=None, faset_params=None, rows=0):
        address = self.__solr. get_base_url() + self.__name + '/facet'
        params = {}
        if query:
            params['q'] = query
        if sc:
            params['sc'] = sc

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
        u'"',
        u'~',
        u'?',
        u':'
    ]
    for s in special:
        string = string.replace(s,'\\'+s)
    return string


class SearchCriteria:

    def __init__(self, operator):
        """
        Init
        :param operator: String AND|OR
        :return:
        """
        self.operator = operator
        self.query = []
        self.boost = 0
    def add_attr(self, key, value):
        """
        :param criteria_part: CriteriaPart object
        :return:
        """
        self.query.append({
            'key': key,
            'value': value
        })

    def add_search_criteria(self, search_criteria):
        """
        :param search_criteria: SearchCriteria object
        :return:
        """
        self.query.append(search_criteria)

    def to_lucene_query(self):
        query_string_parts = [u"("]

        for i, query_part in enumerate(self.query):
            if isinstance(query_part, dict):
                query_string_parts.append(u'%s:%s' % (query_part['key'], query_part['value']))
            elif isinstance(query_part, SearchCriteria):
                query_string_parts.append(query_part.to_lucene_query())
            if i < len(self.query) - 1:
                query_string_parts.append(u' ' + self.operator + u' ')
        query_string_parts.append(u')')
        if self.boost:
            query_string_parts.append(u'^' + str(self.boost))
        return u''.join(query_string_parts)

    def to_dict(self):
        dict_criteria = {
            'operator': self.operator,
            'query': []
        }
        for i, query_part in enumerate(self.query):
            if isinstance(query_part, dict):
                dict_criteria['query'].append(query_part)
            elif isinstance(query_part, SearchCriteria):
                dict_criteria['query'].append(query_part.to_dict())

        return dict_criteria

    @staticmethod
    def from_dict(dict_criteria):
        try:
            sc = SearchCriteria(dict_criteria['operator'])
            for query_part in dict_criteria['query']:
                if 'key' in query_part and 'value' in query_part:
                    sc.add_attr(query_part['key'], query_part['value'])
                else:
                    sc.add_search_criteria(SearchCriteria.from_dict(query_part))
            return sc
        except KeyError as e:
            raise ValueError(u'Wrong dict_criteria %s. Error:' % (unicode(dict_criteria), unicode(e)))

    def to_human_read(self, parent=None, lang=u'ru'):
        operators_title = {
            u'AND': {
                u'ru': u'И'
            },
            u'OR': {
                u'ru': u'ИЛИ'
            },
            u'NOT': {
                u'ru': u'НЕ'
            },
        }
        query_string_parts = []
        if parent:
            query_string_parts.append(u'(')

        for i, query_part in enumerate(self.query):
            if isinstance(query_part, dict):
                query_string_parts.append(u'%s:"%s"' % (query_part['k'], query_part['v']))
            elif isinstance(query_part, SearchCriteria):
                query_string_parts.append(query_part.to_human_read(parent=True, lang=lang))
            if i < len(self.query) - 1:

                try:
                    operator_title = operators_title[self.operator][lang]
                except KeyError:
                    operator_title = self.operator

                query_string_parts.append(u' ' + operator_title + u' ')
        if parent:
            query_string_parts.append(u')')
        return u''.join(query_string_parts)