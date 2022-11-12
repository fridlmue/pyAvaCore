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

import avacore.processor
import avacore.processor_catalunya
import avacore.processor_cz
import avacore.processor_norway
import avacore.processor_uk


def new_processor(region_id: str) -> avacore.processor.Processor:
    if region_id.startswith("CZ"):
        return avacore.processor_cz.Processor()
    if (
        region_id.startswith("ES-CT")
        and not region_id.startswith("ES-CT-L")
        or region_id.startswith("ES-CT-L-04")
    ):
        return avacore.processor_catalunya.Processor()
    if region_id.startswith("GB"):
        return avacore.processor_uk.Processor()
    if region_id.startswith("NO"):
        return avacore.processor_norway.Processor()
    return None
