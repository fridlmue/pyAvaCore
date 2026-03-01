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
import avacore.processor_AD
import avacore.processor_caamlv6
import avacore.processor_ES_CT
import avacore.processor_CZ
import avacore.processor_ES
import avacore.processor_FI
import avacore.processor_FR
import avacore.processor_IS
import avacore.processor_IT_Livigno
import avacore.processor_IT_MeteoMont
import avacore.processor_NO
import avacore.processor_PL
import avacore.processor_PL_12
import avacore.processor_RO
import avacore.processor_SE
import avacore.processor_UA
import avacore.processor_GB


def new_processor(region_id: str) -> avacore.processor.Processor:
    if region_id.startswith("AD"):
        return avacore.processor_AD.Processor()
    if region_id.startswith("CH"):
        return avacore.processor_caamlv6.Processor()
    if region_id.startswith("AT"):
        return avacore.processor_caamlv6.Processor()
    if region_id.startswith("DE-BY"):
        return avacore.processor_caamlv6.Processor()
    if region_id.startswith("IT-Livigno"):
        return avacore.processor_IT_Livigno.Processor()
    if region_id.startswith("IT-MeteoMont"):
        return avacore.processor_IT_MeteoMont.Processor()
    if region_id.startswith("IT"):
        return avacore.processor_caamlv6.Processor()
    if region_id.startswith("CZ"):
        return avacore.processor_CZ.Processor()
    if region_id.startswith("ES-CT-L-04"):
        return avacore.processor_ES_CT.Processor()
    if region_id.startswith("ES-CT-L"):
        return avacore.processor_caamlv6.Processor()
    if region_id.startswith("ES-CT"):
        return avacore.processor_ES_CT.Processor()
    if region_id.startswith("ES"):
        return avacore.processor_ES.Processor()
    if region_id.startswith("FI"):
        return avacore.processor_FI.Processor()
    if region_id.startswith("FR"):
        return avacore.processor_FR.Processor()
    if region_id.startswith("GB"):
        return avacore.processor_GB.Processor()
    if region_id.startswith("IS"):
        return avacore.processor_IS.Processor()
    if region_id.startswith("NO"):
        return avacore.processor_NO.Processor()
    if region_id.startswith("PL-12"):
        return avacore.processor_PL_12.Processor()
    if region_id.startswith("PL"):
        return avacore.processor_PL.Processor()
    if region_id.startswith("RO"):
        return avacore.processor_RO.Processor()
    if region_id.startswith("SE"):
        return avacore.processor_SE.Processor()
    if region_id.startswith("SI"):
        return avacore.processor_caamlv6.Processor()
    if region_id.startswith("SK"):
        return avacore.processor_caamlv6.Processor2022()
    if region_id.startswith("UA"):
        return avacore.processor_UA.Processor()
    raise ValueError
