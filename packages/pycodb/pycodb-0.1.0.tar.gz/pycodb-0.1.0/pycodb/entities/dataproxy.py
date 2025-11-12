class DataProxy:
    def __init__(self, data_list):
        self._objects = [self._dict_to_obj(item) for item in data_list]

    def _dict_to_obj(self, data):
        cls = type('DataItem', (), {})
        obj = cls()
        for key, value in data.items():
            setattr(obj, key, value)

        def repr_str(self):
            attrs = ', '.join(f'{k}={v}' for k, v in self.__dict__.items())
            return f"<DataItem {attrs}>"

        cls.__repr__ = repr_str

        return obj

    def __iter__(self):
        return iter(self._objects)

    def __getitem__(self, index):
        return self._objects[index]

    def __len__(self):
        return len(self._objects)

    def __repr__(self):
        return f'DataProxy({self._objects})'