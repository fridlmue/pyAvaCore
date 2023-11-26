from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExternalFile:
    """External file is used to link to external files like maps, thumbnails etc."""

    description: Optional[str] = None
    fileReferenceURI: Optional[str] = None
    fileType: Optional[str] = None


@dataclass
class MetaData:
    """Meta data for various uses. Can be used to link to external files like maps, thumbnails
    etc.
    """

    comment: Optional[str] = None
    extFiles: Optional[List[ExternalFile]] = None
