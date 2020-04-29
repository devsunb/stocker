class StockData:
    def __init__(self, mall=None, number=None, name=None, time=None, in_stock=None):
        self.data = {
            'mall': mall,
            'number': number,
            'name': name,
            'time': time,
            'in_stock': in_stock
        }

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
