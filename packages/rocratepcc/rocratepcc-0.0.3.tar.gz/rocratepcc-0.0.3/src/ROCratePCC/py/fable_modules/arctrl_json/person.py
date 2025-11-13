from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..arctrl_core.comment import Comment
from ..arctrl_core.conversion import (Person_setCommentFromORCID, Person_setOrcidFromComments)
from ..arctrl_core.ontology_annotation import OntologyAnnotation
from ..arctrl_core.person import Person
from ..fable_library.array_ import map as map_2
from ..fable_library.list import (choose, of_array, FSharpList)
from ..fable_library.option import (map, default_arg)
from ..fable_library.seq import (map as map_1, try_pick)
from ..fable_library.string_ import (replace, split, join)
from ..fable_library.types import Array
from ..fable_library.util import IEnumerable_1
from ..thoth_json_core.decode import (object, IOptionalGetter, string, resize_array, IGetters, IRequiredGetter, map as map_3, array as array_3)
from ..thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from .comment import (encoder as encoder_1, decoder as decoder_1, ROCrate_encoderDisambiguatingDescription, ROCrate_decoderDisambiguatingDescription)
from .context.rocrate.isa_organization_context import context_jsonvalue
from .context.rocrate.isa_person_context import (context_jsonvalue as context_jsonvalue_1, context_minimal_json_value)
from .decode import Decode_objectNoAdditionalProperties
from .encode import (try_include, try_include_seq)
from .idtable import encode
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder, OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderDefinedTerm)

__A_ = TypeVar("__A_")

def encoder(person: Person) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], person: Any=person) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow1818(value: str, person: Any=person) -> IEncodable:
        class ObjectExpr1817(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1817()

    def _arrow1820(value_2: str, person: Any=person) -> IEncodable:
        class ObjectExpr1819(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_2)

        return ObjectExpr1819()

    def _arrow1822(value_4: str, person: Any=person) -> IEncodable:
        class ObjectExpr1821(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_4)

        return ObjectExpr1821()

    def _arrow1824(value_6: str, person: Any=person) -> IEncodable:
        class ObjectExpr1823(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_6)

        return ObjectExpr1823()

    def _arrow1826(value_8: str, person: Any=person) -> IEncodable:
        class ObjectExpr1825(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_8)

        return ObjectExpr1825()

    def _arrow1828(value_10: str, person: Any=person) -> IEncodable:
        class ObjectExpr1827(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_10)

        return ObjectExpr1827()

    def _arrow1830(value_12: str, person: Any=person) -> IEncodable:
        class ObjectExpr1829(IEncodable):
            def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                return helpers_6.encode_string(value_12)

        return ObjectExpr1829()

    def _arrow1832(value_14: str, person: Any=person) -> IEncodable:
        class ObjectExpr1831(IEncodable):
            def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
                return helpers_7.encode_string(value_14)

        return ObjectExpr1831()

    def _arrow1834(value_16: str, person: Any=person) -> IEncodable:
        class ObjectExpr1833(IEncodable):
            def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
                return helpers_8.encode_string(value_16)

        return ObjectExpr1833()

    def _arrow1835(oa: OntologyAnnotation, person: Any=person) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow1836(comment: Comment, person: Any=person) -> IEncodable:
        return encoder_1(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("firstName", _arrow1818, person.FirstName), try_include("lastName", _arrow1820, person.LastName), try_include("midInitials", _arrow1822, person.MidInitials), try_include("orcid", _arrow1824, person.ORCID), try_include("email", _arrow1826, person.EMail), try_include("phone", _arrow1828, person.Phone), try_include("fax", _arrow1830, person.Fax), try_include("address", _arrow1832, person.Address), try_include("affiliation", _arrow1834, person.Affiliation), try_include_seq("roles", _arrow1835, person.Roles), try_include_seq("comments", _arrow1836, person.Comments)]))
    class ObjectExpr1837(IEncodable):
        def Encode(self, helpers_9: IEncoderHelpers_1[Any], person: Any=person) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_9))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_9.encode_object(arg)

    return ObjectExpr1837()


def _arrow1849(get: IGetters) -> Person:
    def _arrow1838(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("orcid", string)

    def _arrow1839(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("lastName", string)

    def _arrow1840(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("firstName", string)

    def _arrow1841(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("midInitials", string)

    def _arrow1842(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("email", string)

    def _arrow1843(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("phone", string)

    def _arrow1844(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("fax", string)

    def _arrow1845(__unit: None=None) -> str | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("address", string)

    def _arrow1846(__unit: None=None) -> str | None:
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("affiliation", string)

    def _arrow1847(__unit: None=None) -> Array[OntologyAnnotation] | None:
        arg_19: Decoder_1[Array[OntologyAnnotation]] = resize_array(OntologyAnnotation_decoder)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("roles", arg_19)

    def _arrow1848(__unit: None=None) -> Array[Comment] | None:
        arg_21: Decoder_1[Array[Comment]] = resize_array(decoder_1)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("comments", arg_21)

    return Person(_arrow1838(), _arrow1839(), _arrow1840(), _arrow1841(), _arrow1842(), _arrow1843(), _arrow1844(), _arrow1845(), _arrow1846(), _arrow1847(), _arrow1848())


decoder: Decoder_1[Person] = object(_arrow1849)

def ROCrate_genID(p: Person) -> str:
    def chooser(c: Comment, p: Any=p) -> str | None:
        match_value: str | None = c.Name
        match_value_1: str | None = c.Value
        (pattern_matching_result, n, v) = (None, None, None)
        if match_value is not None:
            if match_value_1 is not None:
                pattern_matching_result = 0
                n = match_value
                v = match_value_1

            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1

        if pattern_matching_result == 0:
            if True if (True if (n == "orcid") else (n == "Orcid")) else (n == "ORCID"):
                return v

            else: 
                return None


        elif pattern_matching_result == 1:
            return None


    orcid: str | None = try_pick(chooser, p.Comments)
    if orcid is None:
        match_value_1: str | None = p.EMail
        if match_value_1 is None:
            match_value_2: str | None = p.FirstName
            match_value_3: str | None = p.MidInitials
            match_value_4: str | None = p.LastName
            (pattern_matching_result_1, fn, ln, mn, fn_1, ln_1, ln_2, fn_2) = (None, None, None, None, None, None, None, None)
            if match_value_2 is None:
                if match_value_3 is None:
                    if match_value_4 is not None:
                        pattern_matching_result_1 = 2
                        ln_2 = match_value_4

                    else: 
                        pattern_matching_result_1 = 4


                else: 
                    pattern_matching_result_1 = 4


            elif match_value_3 is None:
                if match_value_4 is None:
                    pattern_matching_result_1 = 3
                    fn_2 = match_value_2

                else: 
                    pattern_matching_result_1 = 1
                    fn_1 = match_value_2
                    ln_1 = match_value_4


            elif match_value_4 is not None:
                pattern_matching_result_1 = 0
                fn = match_value_2
                ln = match_value_4
                mn = match_value_3

            else: 
                pattern_matching_result_1 = 4

            if pattern_matching_result_1 == 0:
                return (((("#" + replace(fn, " ", "_")) + "_") + replace(mn, " ", "_")) + "_") + replace(ln, " ", "_")

            elif pattern_matching_result_1 == 1:
                return (("#" + replace(fn_1, " ", "_")) + "_") + replace(ln_1, " ", "_")

            elif pattern_matching_result_1 == 2:
                return "#" + replace(ln_2, " ", "_")

            elif pattern_matching_result_1 == 3:
                return "#" + replace(fn_2, " ", "_")

            elif pattern_matching_result_1 == 4:
                return "#EmptyPerson"


        else: 
            return match_value_1


    else: 
        return orcid



def ROCrate_Affiliation_encoder(affiliation: str) -> IEncodable:
    class ObjectExpr1851(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any], affiliation: Any=affiliation) -> Any:
            return helpers.encode_string("Organization")

    def _arrow1853(__unit: None=None, affiliation: Any=affiliation) -> IEncodable:
        value_1: str = replace(("#Organization_" + affiliation) + "", " ", "_")
        class ObjectExpr1852(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr1852()

    class ObjectExpr1854(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any], affiliation: Any=affiliation) -> Any:
            return helpers_2.encode_string(affiliation)

    values: FSharpList[tuple[str, IEncodable]] = of_array([("@type", ObjectExpr1851()), ("@id", _arrow1853()), ("name", ObjectExpr1854()), ("@context", context_jsonvalue)])
    class ObjectExpr1855(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], affiliation: Any=affiliation) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_3))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping, values)
            return helpers_3.encode_object(arg)

    return ObjectExpr1855()


def _arrow1856(get: IGetters) -> str:
    object_arg: IRequiredGetter = get.Required
    return object_arg.Field("name", string)


ROCrate_Affiliation_decoder: Decoder_1[str] = object(_arrow1856)

def ROCrate_encoder(oa: Person) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow1860(__unit: None=None, oa: Any=oa) -> IEncodable:
        value: str = ROCrate_genID(oa)
        class ObjectExpr1859(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1859()

    class ObjectExpr1861(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            return helpers_1.encode_string("Person")

    def _arrow1863(value_2: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1862(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_2)

        return ObjectExpr1862()

    def _arrow1865(value_4: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1864(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_4)

        return ObjectExpr1864()

    def _arrow1867(value_6: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1866(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_6)

        return ObjectExpr1866()

    def _arrow1869(value_8: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1868(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_8)

        return ObjectExpr1868()

    def _arrow1871(value_10: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1870(IEncodable):
            def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                return helpers_6.encode_string(value_10)

        return ObjectExpr1870()

    def _arrow1873(value_12: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1872(IEncodable):
            def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
                return helpers_7.encode_string(value_12)

        return ObjectExpr1872()

    def _arrow1875(value_14: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1874(IEncodable):
            def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
                return helpers_8.encode_string(value_14)

        return ObjectExpr1874()

    def _arrow1879(value_16: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1878(IEncodable):
            def Encode(self, helpers_9: IEncoderHelpers_1[Any]) -> Any:
                return helpers_9.encode_string(value_16)

        return ObjectExpr1878()

    def _arrow1881(affiliation: str, oa: Any=oa) -> IEncodable:
        return ROCrate_Affiliation_encoder(affiliation)

    def _arrow1883(oa_1: OntologyAnnotation, oa: Any=oa) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_1)

    def _arrow1884(comment: Comment, oa: Any=oa) -> IEncodable:
        return ROCrate_encoderDisambiguatingDescription(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow1860()), ("@type", ObjectExpr1861()), try_include("orcid", _arrow1863, oa.ORCID), try_include("firstName", _arrow1865, oa.FirstName), try_include("lastName", _arrow1867, oa.LastName), try_include("midInitials", _arrow1869, oa.MidInitials), try_include("email", _arrow1871, oa.EMail), try_include("phone", _arrow1873, oa.Phone), try_include("fax", _arrow1875, oa.Fax), try_include("address", _arrow1879, oa.Address), try_include("affiliation", _arrow1881, oa.Affiliation), try_include_seq("roles", _arrow1883, oa.Roles), try_include_seq("comments", _arrow1884, oa.Comments), ("@context", context_jsonvalue_1)]))
    class ObjectExpr1886(IEncodable):
        def Encode(self, helpers_10: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_10))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_10.encode_object(arg)

    return ObjectExpr1886()


def _arrow1901(get: IGetters) -> Person:
    def _arrow1890(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("orcid", string)

    def _arrow1891(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("lastName", string)

    def _arrow1892(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("firstName", string)

    def _arrow1893(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("midInitials", string)

    def _arrow1894(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("email", string)

    def _arrow1895(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("phone", string)

    def _arrow1896(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("fax", string)

    def _arrow1897(__unit: None=None) -> str | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("address", string)

    def _arrow1898(__unit: None=None) -> str | None:
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("affiliation", ROCrate_Affiliation_decoder)

    def _arrow1899(__unit: None=None) -> Array[OntologyAnnotation] | None:
        arg_19: Decoder_1[Array[OntologyAnnotation]] = resize_array(OntologyAnnotation_ROCrate_decoderDefinedTerm)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("roles", arg_19)

    def _arrow1900(__unit: None=None) -> Array[Comment] | None:
        arg_21: Decoder_1[Array[Comment]] = resize_array(ROCrate_decoderDisambiguatingDescription)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("comments", arg_21)

    return Person(_arrow1890(), _arrow1891(), _arrow1892(), _arrow1893(), _arrow1894(), _arrow1895(), _arrow1896(), _arrow1897(), _arrow1898(), _arrow1899(), _arrow1900())


ROCrate_decoder: Decoder_1[Person] = object(_arrow1901)

def ROCrate_encodeAuthorListString(author_list: str) -> IEncodable:
    def encode_single(name: str, author_list: Any=author_list) -> IEncodable:
        def chooser(tupled_arg: tuple[str, IEncodable | None], name: Any=name) -> tuple[str, IEncodable] | None:
            def mapping_1(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
                return (tupled_arg[0], v_1)

            return map(mapping_1, tupled_arg[1])

        class ObjectExpr1903(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any], name: Any=name) -> Any:
                return helpers.encode_string("Person")

        def _arrow1905(value_1: str, name: Any=name) -> IEncodable:
            class ObjectExpr1904(IEncodable):
                def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_1.encode_string(value_1)

            return ObjectExpr1904()

        values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@type", ObjectExpr1903()), try_include("name", _arrow1905, name), ("@context", context_minimal_json_value)]))
        class ObjectExpr1906(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any], name: Any=name) -> Any:
                def mapping_2(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                    return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_2))

                arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_2, values)
                return helpers_2.encode_object(arg)

        return ObjectExpr1906()

    def mapping(s: str, author_list: Any=author_list) -> str:
        return s.strip()

    values_2: Array[IEncodable] = map_2(encode_single, map_2(mapping, split(author_list, ["\t" if (author_list.find("\t") >= 0) else (";" if (author_list.find(";") >= 0) else ",")], None, 0), None), None)
    class ObjectExpr1907(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], author_list: Any=author_list) -> Any:
            def mapping_3(v_3: IEncodable) -> __A_:
                return v_3.Encode(helpers_3)

            arg_1: Array[__A_] = map_2(mapping_3, values_2, None)
            return helpers_3.encode_array(arg_1)

    return ObjectExpr1907()


def ctor(v: Array[str]) -> str:
    return join(", ", v)


def _arrow1909(get: IGetters) -> str:
    def _arrow1908(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("name", string)

    return default_arg(_arrow1908(), "")


ROCrate_decodeAuthorListString: Decoder_1[str] = map_3(ctor, array_3(object(_arrow1909)))

ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "firstName", "lastName", "midInitials", "email", "phone", "fax", "address", "affiliation", "roles", "comments", "@type", "@context"])

def ISAJson_encoder(id_map: Any | None, person: Person) -> IEncodable:
    def f(person_1: Person, id_map: Any=id_map, person: Any=person) -> IEncodable:
        person_2: Person = Person_setCommentFromORCID(person_1)
        def chooser(tupled_arg: tuple[str, IEncodable | None], person_1: Any=person_1) -> tuple[str, IEncodable] | None:
            def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
                return (tupled_arg[0], v_1)

            return map(mapping, tupled_arg[1])

        def _arrow1913(value: str, person_1: Any=person_1) -> IEncodable:
            class ObjectExpr1912(IEncodable):
                def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                    return helpers.encode_string(value)

            return ObjectExpr1912()

        def _arrow1915(value_2: str, person_1: Any=person_1) -> IEncodable:
            class ObjectExpr1914(IEncodable):
                def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_1.encode_string(value_2)

            return ObjectExpr1914()

        def _arrow1917(value_4: str, person_1: Any=person_1) -> IEncodable:
            class ObjectExpr1916(IEncodable):
                def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_2.encode_string(value_4)

            return ObjectExpr1916()

        def _arrow1919(value_6: str, person_1: Any=person_1) -> IEncodable:
            class ObjectExpr1918(IEncodable):
                def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_3.encode_string(value_6)

            return ObjectExpr1918()

        def _arrow1921(value_8: str, person_1: Any=person_1) -> IEncodable:
            class ObjectExpr1920(IEncodable):
                def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_4.encode_string(value_8)

            return ObjectExpr1920()

        def _arrow1923(value_10: str, person_1: Any=person_1) -> IEncodable:
            class ObjectExpr1922(IEncodable):
                def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_5.encode_string(value_10)

            return ObjectExpr1922()

        def _arrow1925(value_12: str, person_1: Any=person_1) -> IEncodable:
            class ObjectExpr1924(IEncodable):
                def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_6.encode_string(value_12)

            return ObjectExpr1924()

        def _arrow1928(value_14: str, person_1: Any=person_1) -> IEncodable:
            class ObjectExpr1927(IEncodable):
                def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_7.encode_string(value_14)

            return ObjectExpr1927()

        def _arrow1931(value_16: str, person_1: Any=person_1) -> IEncodable:
            class ObjectExpr1930(IEncodable):
                def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_8.encode_string(value_16)

            return ObjectExpr1930()

        def _arrow1932(oa: OntologyAnnotation, person_1: Any=person_1) -> IEncodable:
            return OntologyAnnotation_encoder(oa)

        def _arrow1934(comment: Comment, person_1: Any=person_1) -> IEncodable:
            return encoder_1(comment)

        values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("@id", _arrow1913, ROCrate_genID(person_2)), try_include("firstName", _arrow1915, person_2.FirstName), try_include("lastName", _arrow1917, person_2.LastName), try_include("midInitials", _arrow1919, person_2.MidInitials), try_include("email", _arrow1921, person_2.EMail), try_include("phone", _arrow1923, person_2.Phone), try_include("fax", _arrow1925, person_2.Fax), try_include("address", _arrow1928, person_2.Address), try_include("affiliation", _arrow1931, person_2.Affiliation), try_include_seq("roles", _arrow1932, person_2.Roles), try_include_seq("comments", _arrow1934, person_2.Comments)]))
        class ObjectExpr1935(IEncodable):
            def Encode(self, helpers_9: IEncoderHelpers_1[Any], person_1: Any=person_1) -> Any:
                def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                    return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_9))

                arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
                return helpers_9.encode_object(arg)

        return ObjectExpr1935()

    if id_map is not None:
        def _arrow1936(p_1: Person, id_map: Any=id_map, person: Any=person) -> str:
            return ROCrate_genID(p_1)

        return encode(_arrow1936, f, person, id_map)

    else: 
        return f(person)



def _arrow1947(get: IGetters) -> Person:
    def _arrow1937(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("lastName", string)

    def _arrow1938(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("firstName", string)

    def _arrow1939(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("midInitials", string)

    def _arrow1940(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("email", string)

    def _arrow1941(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("phone", string)

    def _arrow1942(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("fax", string)

    def _arrow1943(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("address", string)

    def _arrow1944(__unit: None=None) -> str | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("affiliation", string)

    def _arrow1945(__unit: None=None) -> Array[OntologyAnnotation] | None:
        arg_17: Decoder_1[Array[OntologyAnnotation]] = resize_array(OntologyAnnotation_decoder)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("roles", arg_17)

    def _arrow1946(__unit: None=None) -> Array[Comment] | None:
        arg_19: Decoder_1[Array[Comment]] = resize_array(decoder_1)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("comments", arg_19)

    return Person_setOrcidFromComments(Person(None, _arrow1937(), _arrow1938(), _arrow1939(), _arrow1940(), _arrow1941(), _arrow1942(), _arrow1943(), _arrow1944(), _arrow1945(), _arrow1946()))


ISAJson_decoder: Decoder_1[Person] = Decode_objectNoAdditionalProperties(ISAJson_allowedFields, _arrow1947)

__all__ = ["encoder", "decoder", "ROCrate_genID", "ROCrate_Affiliation_encoder", "ROCrate_Affiliation_decoder", "ROCrate_encoder", "ROCrate_decoder", "ROCrate_encodeAuthorListString", "ROCrate_decodeAuthorListString", "ISAJson_allowedFields", "ISAJson_encoder", "ISAJson_decoder"]

