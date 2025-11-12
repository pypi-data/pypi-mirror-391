import requests

class BaseTable:
    def __init__(self, domain, headers, view_id, table_id):
        self.view_id = view_id
        self.headers = headers
        self.endpoint = f'http://{domain}/api/v2/tables/{table_id}/records'

    def _get(self, fields=None, **kwargs):
        url_query = f'{self.endpoint}?viewId={self.view_id}&limit=1000&shuffle=0'

        if fields is not None:
            fields = ','.join(fields)
            url_query += f'&fields={fields}'

        if kwargs:
            expressions = '&'.join([f'{operator}={kwargs[operator]}' for operator in kwargs.keys()])
            url_query += f'&{expressions}'
        try:
            response = requests.get(url_query, headers=self.headers)
            data = response.json()
            if isinstance(data, dict):
                return data.get('list', [])
            elif isinstance(data, list):
                return data
            else:
                raise Exception(f'Unexpected response structure: {data}')
        except Exception as e:
            raise Exception(f'_Get is broken: {e}')

    def _append(self, target: dict):
        try:
            response = requests.post(self.endpoint, headers=self.headers, json=target)
            data = response.json()
            return data
        except Exception as e:
            raise Exception(f'_Append is broken: {e}')