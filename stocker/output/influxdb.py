from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

from stocker.output.output import Output


class InfluxDBError(RuntimeError):
    pass


class InfluxDB(Output):
    output_name = 'INFLUXDB'

    def __init__(self, config):
        super().__init__(config)
        self.influxdb_config = self.output_config['INFLUXDB']
        self.host = self.influxdb_config['HOST']
        self.port = self.influxdb_config['PORT']
        self.user = self.influxdb_config['USER']
        self.pw = self.influxdb_config['PASSWORD']
        self.db = self.influxdb_config['DB']
        try:
            self.influxdb_client = InfluxDBClient(self.host, self.port, self.user, self.pw, self.db)
            self.influxdb_client.create_database(self.db)
            self.logger.info('Connected to InfluxDB ({}@{}:{}/{})'.format(self.user, self.host, self.port, self.db))
        except InfluxDBClientError as e:
            raise InfluxDBError(str(e).strip())

    def insert(self, stock_data):
        influxdb_data = [{
            'measurement': 'stocker',
            'tags': {
                'mall': stock_data['mall'],
                'number': stock_data['number'],
                'name': stock_data['name']
            },
            'time': stock_data['time'],
            'fields': {
                'in_stock': stock_data['in_stock']
            }
        }]
        return self.influxdb_client.write_points(influxdb_data)

    def close(self):
        self.influxdb_client.close()
