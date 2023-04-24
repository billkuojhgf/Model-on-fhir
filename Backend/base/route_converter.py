import reprlib
import re
import json

from fhirpy import SyncFHIRClient

client = SyncFHIRClient('http://ming-desktop.ddns.net:8192/fhir')


def get_by_path(data, path, default=None):
    assert isinstance(path, list), "Path must be a list"

    rv = data
    try:
        for key in path:
            if rv is None:
                return default

            if isinstance(rv, list):
                if isinstance(key, int):
                    rv = rv[key]
                elif isinstance(key, dict):
                    matched_index = -1
                    for index, item in enumerate(rv):
                        check = True
                        for k, v in key.items():
                            # Add support for nested dicts and lists
                            if isinstance(v, list):
                                check = False if get_by_path(item.get(k, None), v) is None else True
                            elif isinstance(v, dict):
                                check = False if get_by_path(item.get(k, None), [v]) is None else True
                            elif item.get(k, None) != v:
                                check = False

                            if not check:
                                break

                        if check:
                            matched_index = index
                            break
                    if matched_index == -1:
                        rv = None
                    else:
                        rv = rv[matched_index]
                else:  # pragma: no cover
                    raise TypeError(
                        "Can not lookup by {0} in list. "
                        "Possible lookups are by int or by dict.".format(
                            reprlib.repr(key)
                        )
                    )
            else:
                rv = rv[key]

        return rv
    except (IndexError, KeyError, AttributeError):
        return default


def parse_route(route):
    """
    Parse a route string into a list of keys and/or dictionaries.
    """
    RE = r'("\w+"|\{.*\})|(\d+)(?=\.|$)'
    temp_result = []

    for key in re.findall(RE, route):
        if key[0] != '':
            key = key[0]
        elif key[1] != '':
            key = int(key[1])
            temp_result.append(key)
            continue
        else:
            raise ValueError("Invalid route: {}".format(route))

        if key.startswith("{"):
            temp_dict = {}
            if "." in re.sub(r'"[^"]*"', '', key):
                # if "." was in {}, means the value is in complex type.
                # e.g. {a:b.c.d} -> {"a": [b, c, {d: "e"}]}
                # Therefore, we need to parse the value recursively to get the actual route.
                temp_dict[key[1:-1].split(":")[0].strip()] = parse_route(":".join(key[1:-1].split(":")[1:]))
            else:
                value = ":".join(key[1:-1].split(":")[1:]).strip()
                temp_dict[key[1:-1].split(":")[0].strip()] = json.loads(value) if "{" in value else value
            temp_result.append(temp_dict)
        else:
            temp_result.append(key)
    result = []
    for temp in temp_result:
        if isinstance(temp, dict):
            temp_dict = {}
            for k, v in temp.items():
                temp_dict[k.replace('\"', "")] = v.replace('\"', "") if isinstance(v, str) else v
            result.append(temp_dict)

        elif isinstance(temp, str):
            result.append(temp.replace("\"", ""))
        else:
            result.append(temp)
    return result
