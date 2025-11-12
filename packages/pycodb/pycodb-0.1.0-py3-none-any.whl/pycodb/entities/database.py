from .dataproxy import DataProxy

class DataBase:
    DOMAIN = ''
    NOCODB_API_KEY = ''

    def __init__(self, table_name: str):
        table = getattr(self.__class__, table_name)

        self._objects = table(
            domain=DataBase.DOMAIN,
            headers={
                'xc-token': DataBase.NOCODB_API_KEY,
                'accept': 'application/json'
            },
            view_id=table.view_id,
            table_id=table.table_id
        )
        self._data_cache = None

    @property
    def data(self):
        if self._data_cache is None:
            raw_data = self._objects._get()
            self._data_cache = DataProxy(raw_data)
        return self._data_cache

    def values(self, fields=None):
        if fields is not None:
            raw_data = self._objects._get(fields=fields)
            self._data_cache = DataProxy(raw_data)
            return self._data_cache
        return self.data

    def filter(self, **kwargs):
        if kwargs:
            raw_data = self._objects._get(**kwargs)
            self._data_cache = DataProxy(raw_data)
            return self._data_cache
        return self.data

    def append(self, target: dict):
        return self._objects._append(target)