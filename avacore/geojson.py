# Generated using https://app.quicktype.io/
from dataclasses import dataclass
from typing import Optional, List, Any, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Geometry:
    type: Optional[str] = None
    coordinates: Optional[List[List[List[List[float]]]]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Geometry':
        assert isinstance(obj, dict)
        type = from_union([from_str, from_none], obj.get("type"))
        coordinates = from_union([lambda x: from_list(lambda x: from_list(lambda x: from_list(lambda x: from_list(from_float, x), x), x), x), from_none], obj.get("coordinates"))
        return Geometry(type, coordinates)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = from_union([from_str, from_none], self.type)
        result["coordinates"] = from_union([lambda x: from_list(lambda x: from_list(lambda x: from_list(lambda x: from_list(to_float, x), x), x), x), from_none], self.coordinates)
        return result


@dataclass
class Style:
    stroke: Optional[bool] = None
    fill_color: Optional[str] = None
    fill_opacity: Optional[float] = None
    class_name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Style':
        assert isinstance(obj, dict)
        stroke = from_union([from_bool, from_none], obj.get("stroke"))
        fill_color = from_union([from_str, from_none], obj.get("fillColor"))
        fill_opacity = from_union([from_float, from_none], obj.get("fillOpacity"))
        class_name = from_union([from_str, from_none], obj.get("className"))
        return Style(stroke, fill_color, fill_opacity, class_name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["stroke"] = from_union([from_bool, from_none], self.stroke)
        result["fillColor"] = from_union([from_str, from_none], self.fill_color)
        result["fillOpacity"] = from_union([to_float, from_none], self.fill_opacity)
        result["className"] = from_union([from_str, from_none], self.class_name)
        return result


@dataclass
class Properties:
    threshold: None
    id: Optional[str] = None
    elevation: Optional[str] = None
    style: Optional[Style] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Properties':
        assert isinstance(obj, dict)
        threshold = from_none(obj.get("threshold"))
        id = from_union([from_str, from_none], obj.get("id"))
        elevation = from_union([from_str, from_none], obj.get("elevation"))
        style = from_union([Style.from_dict, from_none], obj.get("style"))
        return Properties(threshold, id, elevation, style)

    def to_dict(self) -> dict:
        result: dict = {}
        result["threshold"] = from_none(self.threshold)
        result["id"] = from_union([from_str, from_none], self.id)
        result["elevation"] = from_union([from_str, from_none], self.elevation)
        result["style"] = from_union([lambda x: to_class(Style, x), from_none], self.style)
        return result


@dataclass
class Feature:
    type: Optional[str] = None
    properties: Optional[Properties] = None
    geometry: Optional[Geometry] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Feature':
        assert isinstance(obj, dict)
        type = from_union([from_str, from_none], obj.get("type"))
        properties = from_union([Properties.from_dict, from_none], obj.get("properties"))
        geometry = from_union([Geometry.from_dict, from_none], obj.get("geometry"))
        return Feature(type, properties, geometry)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = from_union([from_str, from_none], self.type)
        result["properties"] = from_union([lambda x: to_class(Properties, x), from_none], self.properties)
        result["geometry"] = from_union([lambda x: to_class(Geometry, x), from_none], self.geometry)
        return result


@dataclass
class FeatureCollection:
    type: Optional[str] = None
    features: Optional[List[Feature]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FeatureCollection':
        assert isinstance(obj, dict)
        type = from_union([from_str, from_none], obj.get("type"))
        features = from_union([lambda x: from_list(Feature.from_dict, x), from_none], obj.get("features"))
        return FeatureCollection(type, features)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = from_union([from_str, from_none], self.type)
        result["features"] = from_union([lambda x: from_list(lambda x: to_class(Feature, x), x), from_none], self.features)
        return result
