from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..arctrl_validation_packages.validation_package import ValidationPackage
from ..fable_library.list import (choose, of_array, FSharpList)
from ..fable_library.seq import (to_list, delay, collect, singleton)
from ..fable_library.util import (equals, IEnumerable_1)
from ..yamlicious.yamlicious_types import YAMLContent_create_27AED5E3
from ..yamlicious.decode import (object, IRequiredGetter, string as string_1, IOptionalGetter, IGetters)
from ..yamlicious.encode import (string, try_include)
from ..yamlicious.reader import read
from ..yamlicious.writer import write
from ..yamlicious.yamlicious_types import (YAMLElement, Config)
from .encode import default_whitespace

def ValidationPackage_encoder(validationpackage: ValidationPackage) -> YAMLElement:
    def chooser(tupled_arg: tuple[str, YAMLElement], validationpackage: Any=validationpackage) -> tuple[str, YAMLElement] | None:
        v: YAMLElement = tupled_arg[1]
        if equals(v, YAMLElement(5)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow3505(value: str, validationpackage: Any=validationpackage) -> YAMLElement:
        return string(value)

    obj_seq: FSharpList[tuple[str, YAMLElement]] = choose(chooser, of_array([("name", string(validationpackage.Name)), try_include("version", _arrow3505, validationpackage.Version)]))
    def _arrow3507(__unit: None=None, validationpackage: Any=validationpackage) -> IEnumerable_1[YAMLElement]:
        def _arrow3506(match_value: tuple[str, YAMLElement]) -> IEnumerable_1[YAMLElement]:
            return singleton(YAMLElement(0, YAMLContent_create_27AED5E3(match_value[0]), match_value[1]))

        return collect(_arrow3506, obj_seq)

    return YAMLElement(3, to_list(delay(_arrow3507)))


def _arrow3510(value_2: YAMLElement) -> ValidationPackage:
    def getter(get: IGetters) -> ValidationPackage:
        def _arrow3508(__unit: None=None, get: Any=get) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("name", string_1)

        def _arrow3509(__unit: None=None, get: Any=get) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("version", string_1)

        return ValidationPackage(_arrow3508(), _arrow3509())

    return object(getter, value_2)


ValidationPackage_decoder: Callable[[YAMLElement], ValidationPackage] = _arrow3510

def ARCtrl_ValidationPackages_ValidationPackage__ValidationPackage_fromYamlString_Static_Z721C83C5(s: str) -> ValidationPackage:
    return ValidationPackage_decoder(read(s))


def ARCtrl_ValidationPackages_ValidationPackage__ValidationPackage_toYamlString_Static_71136F3F(whitespace: int | None=None) -> Callable[[ValidationPackage], str]:
    def _arrow3512(vp: ValidationPackage, whitespace: Any=whitespace) -> str:
        element: YAMLElement = ValidationPackage_encoder(vp)
        whitespace_1: int = default_whitespace(whitespace) or 0
        def _arrow3511(c: Config) -> Config:
            return Config(whitespace_1, c.Level)

        return write(element, _arrow3511)

    return _arrow3512


def ARCtrl_ValidationPackages_ValidationPackage__ValidationPackage_toYamlString_71136F3F(this: ValidationPackage, whitespace: int | None=None) -> str:
    return ARCtrl_ValidationPackages_ValidationPackage__ValidationPackage_toYamlString_Static_71136F3F(whitespace)(this)


__all__ = ["ValidationPackage_encoder", "ValidationPackage_decoder", "ARCtrl_ValidationPackages_ValidationPackage__ValidationPackage_fromYamlString_Static_Z721C83C5", "ARCtrl_ValidationPackages_ValidationPackage__ValidationPackage_toYamlString_Static_71136F3F", "ARCtrl_ValidationPackages_ValidationPackage__ValidationPackage_toYamlString_71136F3F"]

