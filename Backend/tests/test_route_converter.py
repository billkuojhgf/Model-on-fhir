from unittest import TestCase
from base.route_converter import get_by_path
from base.route_converter import parse_route


class Test(TestCase):
    def test_get_by_path(self):
        self.assertEqual(get_by_path({'key': 'value'}, ['key']), 'value')
        self.assertEqual(get_by_path({'key': [{'nkey': 'nvalue'}]}, ['key', 0, 'nkey']), 'nvalue')
        self.assertEqual(get_by_path({
            'key': [
                {'test': 'test0', 'nkey': 'zero'},
                {'test': 'test1', 'nkey': 'one'}
            ]
        }, ['key', {'test': 'test1'}, 'nkey']), "one")
        self.assertEqual(get_by_path({'a': 1}, ['b'], 0), 0)
        self.assertEqual(get_by_path({'a': {'b': None}}, ['a', 'b'], 0) is None, True)
        self.assertEqual(get_by_path({'a': {'b': None}}, ['a', 'b', 'c'], 0), 0)
        self.assertEqual(get_by_path({"test2": [
            {
                'a': {
                    "b": [
                        {"c": "test1"}
                    ]
                },
                "result": {
                    "number": "one"
                }
            }, {
                'a': {
                    "b": [
                        {"c": "test2"}
                    ]
                },
                "result": {
                    "number": "two"
                }
            }]}, ["test2", {"a": ["b", {"c": 'test2'}]}, "result", 'number']
        ), "two")

    def test_parse_route(self):
        self.assertEqual(parse_route('"b".{"c":"test2"}'),
                         ['b', {'c': 'test2'}])
        self.assertEqual(parse_route('"test2".{"a":"b".{"c":"test2"}}."result"."number"'),
                         ['test2', {'a': ['b', {'c': 'test2'}]}, 'result', 'number'])
        self.assertEqual(parse_route('"class"."code"'),
                         ['class', 'code'])
        self.assertEqual(parse_route('"component"."coding".{"code": "4323-3"}."display"'),
                         ['component', 'coding', {'code': '4323-3'}, 'display'])
        self.assertEqual(parse_route('"component"."coding".{"code": "4323-3"}.0."display"'),
                         ['component', 'coding', {'code': '4323-3'}, 0, 'display'])

    def test_regression(self):
        resources = {
            "resourceType": "Procedure",
            "id": "example",
            "status": "completed",
            "statusReason": {
                "coding": [
                    {
                        "system": "https://www.hpa.gov.tw/",
                        "code": "1",
                        "display": "原發部位未手術原因"
                    }
                ],
                "text": "原發部位未手術原因"
            },
            "category": {
                "coding": [
                    {
                        "system": "https://www.hpa.gov.tw/",
                        "code": "2",
                        "display": "微創手術"
                    }
                ],
                "text": "微創手術"
            },
            "code": {
                "coding": [
                    {
                        "system": "https://www.hpa.gov.tw/",
                        "code": "50",
                        "display": "申報醫院原發部位手術方式"
                    }
                ],
                "text": "申報醫院原發部位手術方式"
            },
            "subject": {
                "reference": "Patient/example"
            },
            "performedDateTime": "2018-02-23",
            "bodySite": [
                {
                    "coding": [
                        {
                            "system": "https://www.hpa.gov.tw/",
                            "code": "0",
                            "display": "原發部位手術邊緣"
                        }
                    ]
                },
                {
                    "coding": [
                        {
                            "system": "https://www.hpa.gov.tw/",
                            "code": "999",
                            "display": "原發部位手術切緣距離"
                        }
                    ]
                }
            ]
        }
        route = parse_route(
            '"bodySite".{"coding":{"system": "https://www.hpa.gov.tw/","code":"999"}}."coding".0."display"')
        self.assertEqual(get_by_path(resources, route), "原發部位手術切緣距離")
