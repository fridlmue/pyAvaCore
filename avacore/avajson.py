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

    def is_empty(self, x):
        """Tests whether x is empty"""
        if x is None or x == {} or x == []:
            return True
        try:
            return self.is_empty(self.default(x))
        except:
            return False

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        try:
            return o.toJSON()
        except:
            as_dict = o.__dict__
            return {k: v for k, v in as_dict.items() if not self.is_empty(v)}
