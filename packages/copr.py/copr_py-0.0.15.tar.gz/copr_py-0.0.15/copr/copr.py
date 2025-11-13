import importlib.resources
import jmespath
import json
import requests

## COPR CLASS

class API:

  ## CONSTRUCTOR

  def __init__(self):
    self._scheme = None
    self.__initialized = False

  ## FACTORY

  @staticmethod
  def init(endpoint='production'):
    # create api instance
    copr = API()
    # save the chosen endpoint
    copr.__endpoint = endpoint
    # load scheme
    with importlib.resources.open_text('copr', 'scheme.json') as file:
      API._scheme = json.load(file)
    # load files
    for key, value in requests.get(API._scheme['urls']['endpoints'][endpoint] + '/' + API._scheme['urls']['file']).json().items():
      setattr(copr, key, value)
    # proceed initializing
    copr._initialize()
    # return instance
    return copr

  ## INITIALIZE

  def _initialize(self):
    # only initialize if this has not yet been done
    if self.__initialized:
      return
    # init constants
    # init info functions
    for key, value in self._info.items():
      setattr(self, key, (lambda v: (lambda: v))(value))
    # init base function
    for key, value in API._scheme['functions'].items():
      setattr(self, key, (lambda v: (lambda: self.__baseFunction(v)))(value))
    # init base class: is done at the end of this file
    # init elements
    for elementType in API._scheme['elementTypes']:
      # init element functions
      if 'query' in elementType:
        # the next line looks overly complicated but basically defines
        # self.{name}s = lambda **kwargs: self.__elements(elementType, **kwargs)
        # However, the wrong value would be passed on to the lambda function if it were not chained in another lambda function.
        setattr(self, elementType['functionName'] if 'functionName' in elementType else elementType['name'] if elementType['name'].endswith('s') else elementType['name'][0:-1] + 'ies' if elementType['name'].endswith('y') else elementType['name'] + 's', (lambda et: (lambda **kwargs: self.__elements(et, **kwargs)))(elementType))
      # init element classes
      classname = self.__classnameForElement(elementType)
      baseclassname = elementType['baseclass'] if 'baseclass' in elementType else 'element'
      globals()[classname] = type(classname, (self.__classForName(baseclassname),), {})
      # save parameters to the element classes
      currentClass = self.__classForElement(elementType)
      currentClass._parameters = elementType['parameters'] if 'parameters' in elementType else {}
      currentClass._data = elementType['data'] if 'data' in elementType else {}
      currentClass._dataSelf = elementType['dataSelf'] if 'dataSelf' in elementType else {}
      while baseclassname != 'element':
        ets = [et for et in API._scheme['elementTypes'] if et['name'] == baseclassname]
        if len(ets) == 0:
          break
        et = ets[0]
        baseclassname = et['baseclass'] if 'baseclass' in et else 'element'
        if 'parameters' in et:
          currentClass._parameters = {**currentClass._parameters, **et['parameters']}
        if 'data' in et:
          currentClass._data = {**currentClass._data, **et['data']}
        if 'dataSelf' in et:
          currentClass._dataSelf = {**currentClass._dataSelf, **et['dataSelf']}
    # indicate that the initialization has been done
    self.__initialized = True

  ## CLASS HANDLING

  def __classForElement(self, elementType):
    return globals()[self.__classnameForElement(elementType)]
  def __classForName(self, name):
    return globals()[self.___classnameForName(name)]
  def __classnameForElement(self, elementType):
    return self.___classnameForName(elementType['name'])
  def ___classnameForName(self, name):
    return 'COPR' + name[0].upper() + name[1:]

  ## QUERYING

  def _query(self, query, _d=None, **kwargs):
    # normalize list of queries
    query = self.__normalizeQuery(query)
    queries = list(reversed(query['queries'])) if 'queries' in query else [query]
    # loop through the queries
    last = None
    results = None
    while len(queries):
      q = queries.pop()
      # build the query
      compiledQuery = self.__buildSingleQuery(q, {
        '__last': last,
        '__endpointUrl': API._scheme['urls']['endpoints'][self.__endpoint],
      }, **kwargs)
      # execute the query
      results = jmespath.search(compiledQuery, _d if _d and ('global' not in q or not q['global']) else self._data)
      last = results
    # use default value
    if results is None and 'default' in query:
      results = query['default']
    # return if vanishing
    if results is None:
      return results
    # apply the vocabulary
    def objectForId(values, id):
      return next((value for value in values if value['id'] == id), None)
    def applyVocabulary(x):
      return _applyVocabulary(x, self._vocabulary[query['vocabulary']]) if 'vocabulary' in query and query['vocabulary'] in self._vocabulary else x
    def _applyVocabulary(x, vocabulary):
      return objectForId(vocabulary, x) or next((y for value in vocabulary if 'children' in value and (y := _applyVocabulary(x, value['children'])) is not None), None)
    results = [applyVocabulary(result) for result in results] if isinstance(results, list) else applyVocabulary(results)
    # create corresponding objects if requested
    def packIntoObject(x):
      # return if not object
      if not isinstance(query, dict) or 'class' not in query:
        return x
      # prepare object
      name = query['class']
      if name in API._scheme['macros']['classes']:
        name = API._scheme['macros']['classes'][name]
      if isinstance(name, dict):
        if x['class'] not in name:
          return x
        name = name[x['class']]
      # add additional data to the object
      currentClass = self.__classForName(name)
      for dataKey, dataQuery in currentClass._data.items():
        x[dataKey] = self._query(dataQuery, _d)
      for dataKey, dataQuery in currentClass._dataSelf.items():
        x[dataKey] = self._query(dataQuery, x)
      # build and return object
      return currentClass(self, x, self._info)
    return [packIntoObject(result) for result in results] if isinstance(results, list) else packIntoObject(results)
  def __validParametersForQuery(self, query):
    parameters = []
    # collect all valid parameters for the query
    if 'parameter' in query:
      parameters.append(query['parameter'])
    elif 'query' in query:
      if isinstance(query['query'], list):
        for q in query['query']:
          parameters += self.__validParametersForQuery(q)
      else:
        parameters += self.__validParametersForQuery(query['query'])
    elif 'queries' in query:
      for q in query['queries']:
        parameters += self.__validParametersForQuery(q)
    return parameters
  def __normalizeQuery(self, query, extendBy={}):
    # make a dict if query is a string or a list
    if isinstance(query, str) or isinstance(query, list):
      query = {'query': query}
    return {**query, **extendBy}
  def __buildSingleQuery(self, qs, meta={}, **kwargs):
    # test for unused parameters
    validParameters = self.__validParametersForQuery(qs)
    invalidParameters = [key for key in kwargs if key not in validParameters]
    if len(invalidParameters) > 0:
      print('WARNING: Some parameters have not been used ({parameters})'.format(parameters=', '.join(invalidParameters)))
    # return the query
    return ''.join(self.__buildSingleQueryArray(qs, **kwargs)).format(**dict((k, json.dumps(v)) for k, v in meta.items()))
  def __buildSingleQueryArray(self, qs, **kwargs):
    query = []
    # append string
    if isinstance(qs, str):
      return [qs]
    # expand list
    if isinstance(qs, list):
      for q in qs:
        query += self.__buildSingleQueryArray(q, **kwargs)
      return query
    # use macros in object
    if 'macro' in qs and qs['macro'] in API._scheme['macros']['queries']:
      qs = {**API._scheme['macros']['queries'][qs['macro']], **qs}
    # append object
    if 'concat' in qs and 'query' in qs:
      qs2 = self.__buildSingleQueryArray(qs['query'], **kwargs)
      if len(qs2) > 0:
        query.append((qs['prefix'] if 'prefix' in qs else '') + (' ' + qs['concat'] + ' ').join(qs2) + (qs['suffix'] if 'suffix' in qs else ''))
      return query
    # use parameter if it is also provided as a keyword
    if 'parameter' in qs and qs['parameter'] in kwargs:
      parameter = qs['parameter']
      if 'removeParameterPrefix' in qs:
        parameter = parameter.lstrip(qs['removeParameterPrefix'])
      if 'removeParameterPostfix' in qs:
        parameter = parameter.rstrip(qs['removeParameterPostfix'])
      if 'startParameterLower' in qs and qs['startParameterLower'] is True:
        parameter = parameter[0].lower() + parameter[1:]
      key = qs['key'] if 'key' in qs else qs['parameter']
      valueRaw = kwargs[key]
      value = json.dumps(valueRaw['id'] if 'valueToId' in qs and qs['valueToId'] and valueRaw and isinstance(valueRaw, object) and 'id' in valueRaw else valueRaw)
      not_value = '' if kwargs[key] else '!'
      query.append(qs['query'].format(parameter=parameter, value=value, not_value=not_value))
    elif 'parameter' in qs and qs['parameter'] not in kwargs and 'nullQuery' in qs:
      query.append(qs['nullQuery'])
    # use query if no parameter is included
    elif 'query' in qs and 'parameter' not in qs:
      query += self.__buildSingleQueryArray(qs['query'], **kwargs)
    return query

  ## FUNCTIONS

  def __elements(self, elementType, **kwargs):
    return self._query(self.__normalizeQuery(elementType['query'], extendBy={'class': elementType['name']}), **kwargs)
  def __baseFunction(self, resultDescription):
    if resultDescription['resultType'] == 'dict':
      result = {}
      for key, query in resultDescription['query'].items():
        result[key] = self._query(query)
      return result
    elif resultDescription['resultType'] == 'expression':
      return self._query(resultDescription['query'])

## BASE CLASS

class COPRElement:
  def __init__(self, api, d, info):
    self._api = api
    self._d = d
    self._info = info
  def howToCite(self):
    return self._info['howToCite']
  def __getParameter(self, name):
    # if the parameter was not defined, raise an exception
    if name not in self._parameters:
      raise Exception('AttributeError: \'{classname}\' object has no attribute \'{name}\''.format(classname=type(self).__name__, name=name))
    # query the parameter
    query = self._parameters[name]
    return self._api._query(query, self._d)
  def __getattr__(self, name):
    return lambda: self.__getParameter(name)
