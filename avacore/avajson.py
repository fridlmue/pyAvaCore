"""
    Copyright (C) 2022 Friedrich Mütschele and other contributors
    This file is part of pyAvaCore.
    pyAvaCore is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    pyAvaCore is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with pyAvaCore. If not, see <http://www.gnu.org/licenses/>.
"""
import json
from datetime import datetime


class JSONEncoder(json.JSONEncoder):
    """JSON serialization for pyAvaCore"""

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        try:
            return o.toJSON()
        except:  # pylint: disable=bare-except
            return o.__dict__


def remove_empty_elements(d):
    """
    # Source: https://gist.github.com/nlohmann/c899442d8126917946580e7f84bf7ee7
    recursively remove empty lists, empty dicts, or None elements from a dictionary
    """

    def empty(x):
        return x is None or x == {} or x == []

    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    return {
        k: v
        for k, v in ((k, remove_empty_elements(v)) for k, v in d.items())
        if not empty(v)
    }
