import unittest
from datetime import datetime

from influxdb import InfluxDBClient


class TestInfluxDB(unittest.TestCase):
    def test_add_row(self):
        influxdb_client = InfluxDBClient('jslee.me', 8086, 'jslee', 'bep0sitive', 'ns_stock')
        influx_body = [{
            'measurement': 'stock',
            'tags': {
                'mall': 'coupang',
                'name': '닌텐도 스위치 동물의 숲 에디션',
                'color': '동물의 숲'
            },
            'time': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'fields': {
                'in_stock': True
            }
        }]
        expected = [
            {'time': d['time'], 'in_stock': d['fields']['in_stock'], 'color': d['tags']['color'],
             'mall': d['tags']['mall'], 'name': d['tags']['name']} for d in influx_body]

        influxdb_client.drop_database('ns_stock')
        influxdb_client.create_database('ns_stock')
        influxdb_client.write_points(influx_body)
        result = list(influxdb_client.query('SELECT * FROM stock').get_points())

        self.assertEqual(1, len(result))
        for i in range(len(expected)):
            result[i]['time'] = result[i]['time'][:-3] + 'Z'
            self.assertTrue(expected[i], result[i])
        influxdb_client.delete_series(tags={'mall': 'coupang',
                                            'type': '닌텐도 스위치 동물의 숲 에디션',
                                            'color': '동물의 숲'})
        influxdb_client.close()

    def test_get(self):
        influxdb_client = InfluxDBClient('jslee.me', 8086, 'jslee', 'bep0sitive', 'ns_stock')
        result = list(influxdb_client.query('SELECT * FROM stock').get_points())
        print(result)
        influxdb_client.close()

    def test_drop(self):
        influxdb_client = InfluxDBClient('jslee.me', 8086, 'jslee', 'bep0sitive', 'ns_stock')
        influxdb_client.drop_database('stocker')
        influxdb_client.create_database('stocker')
        influxdb_client.close()
