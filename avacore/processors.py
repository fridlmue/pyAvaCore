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
import avacore.processor_ad
import avacore.processor_caamlv5
import avacore.processor_catalunya
import avacore.processor_ch
import avacore.processor_cz
import avacore.processor_es
import avacore.processor_fr
import avacore.processor_is
import avacore.processor_norway
import avacore.processor_pl
import avacore.processor_sk
import avacore.processor_uk


def new_processor(region_id: str) -> avacore.processor.Processor:
    # pylint: disable=too-many-return-statements
    if region_id.startswith("AD"):
        return avacore.processor_ad.Processor()
    if region_id.startswith("CH"):
        return avacore.processor_ch.Processor()
    if region_id.startswith("CZ"):
        return avacore.processor_cz.Processor()
    if region_id.startswith("ES") and not region_id.startswith("ES-CT"):
        return avacore.processor_es.Processor()
    if (
        region_id.startswith("ES-CT")
        and not region_id.startswith("ES-CT-L")
        or region_id.startswith("ES-CT-L-04")
    ):
        return avacore.processor_catalunya.Processor()
    if region_id.startswith("FR"):
        return avacore.processor_fr.Processor()
    if region_id.startswith("GB"):
        return avacore.processor_uk.Processor()
    if region_id.startswith("IS"):
        return avacore.processor_is.Processor()
    if region_id.startswith("NO"):
        return avacore.processor_norway.Processor()
    if region_id.startswith("PL"):
        return avacore.processor_pl.Processor()
    if region_id.startswith("SI"):
        return avacore.processor_caamlv5.SloveniaProcessor()
    if region_id.startswith("SK"):
        return avacore.processor_sk.Processor()
    return avacore.processor_caamlv5.Processor()
