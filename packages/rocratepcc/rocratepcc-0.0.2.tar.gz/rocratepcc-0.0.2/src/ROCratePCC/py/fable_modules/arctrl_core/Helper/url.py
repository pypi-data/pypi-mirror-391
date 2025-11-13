from collections.abc import Callable
from typing import Any
from ...fable_library.util import to_enumerable
from .collections_ import (Dictionary_ofSeq, Dictionary_tryFind)

def OntobeeParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "http://purl.obolibrary.org/obo/") + "") + tsr) + "_") + local_tan) + ""


def BioregistryParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://bioregistry.io/") + "") + tsr) + ":") + local_tan) + ""


def OntobeeDPBOParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "http://purl.org/nfdi4plants/ontology/dpbo/") + "") + tsr) + "_") + local_tan) + ""


def MSParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://www.ebi.ac.uk/ols4/ontologies/ms/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F") + "") + tsr) + "_") + local_tan) + ""


def POParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://www.ebi.ac.uk/ols4/ontologies/po/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F") + "") + tsr) + "_") + local_tan) + ""


def ROParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://www.ebi.ac.uk/ols4/ontologies/ro/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F") + "") + tsr) + "_") + local_tan) + ""


def _arrow26(tsr: str) -> Callable[[str], str]:
    def _arrow25(local_tan: str) -> str:
        return OntobeeDPBOParser(tsr, local_tan)

    return _arrow25


def _arrow28(tsr_1: str) -> Callable[[str], str]:
    def _arrow27(local_tan_1: str) -> str:
        return MSParser(tsr_1, local_tan_1)

    return _arrow27


def _arrow30(tsr_2: str) -> Callable[[str], str]:
    def _arrow29(local_tan_2: str) -> str:
        return POParser(tsr_2, local_tan_2)

    return _arrow29


def _arrow32(tsr_3: str) -> Callable[[str], str]:
    def _arrow31(local_tan_3: str) -> str:
        return ROParser(tsr_3, local_tan_3)

    return _arrow31


def _arrow34(tsr_4: str) -> Callable[[str], str]:
    def _arrow33(local_tan_4: str) -> str:
        return BioregistryParser(tsr_4, local_tan_4)

    return _arrow33


def _arrow36(tsr_5: str) -> Callable[[str], str]:
    def _arrow35(local_tan_5: str) -> str:
        return BioregistryParser(tsr_5, local_tan_5)

    return _arrow35


def _arrow38(tsr_6: str) -> Callable[[str], str]:
    def _arrow37(local_tan_6: str) -> str:
        return BioregistryParser(tsr_6, local_tan_6)

    return _arrow37


def _arrow40(tsr_7: str) -> Callable[[str], str]:
    def _arrow39(local_tan_7: str) -> str:
        return BioregistryParser(tsr_7, local_tan_7)

    return _arrow39


def _arrow42(tsr_8: str) -> Callable[[str], str]:
    def _arrow41(local_tan_8: str) -> str:
        return BioregistryParser(tsr_8, local_tan_8)

    return _arrow41


def _arrow44(tsr_9: str) -> Callable[[str], str]:
    def _arrow43(local_tan_9: str) -> str:
        return BioregistryParser(tsr_9, local_tan_9)

    return _arrow43


def _arrow46(tsr_10: str) -> Callable[[str], str]:
    def _arrow45(local_tan_10: str) -> str:
        return BioregistryParser(tsr_10, local_tan_10)

    return _arrow45


def _arrow48(tsr_11: str) -> Callable[[str], str]:
    def _arrow47(local_tan_11: str) -> str:
        return BioregistryParser(tsr_11, local_tan_11)

    return _arrow47


def _arrow50(tsr_12: str) -> Callable[[str], str]:
    def _arrow49(local_tan_12: str) -> str:
        return BioregistryParser(tsr_12, local_tan_12)

    return _arrow49


def _arrow52(tsr_13: str) -> Callable[[str], str]:
    def _arrow51(local_tan_13: str) -> str:
        return BioregistryParser(tsr_13, local_tan_13)

    return _arrow51


def _arrow54(tsr_14: str) -> Callable[[str], str]:
    def _arrow53(local_tan_14: str) -> str:
        return BioregistryParser(tsr_14, local_tan_14)

    return _arrow53


uri_parser_collection: Any = Dictionary_ofSeq(to_enumerable([("DPBO", _arrow26), ("MS", _arrow28), ("PO", _arrow30), ("RO", _arrow32), ("ENVO", _arrow34), ("CHEBI", _arrow36), ("GO", _arrow38), ("OBI", _arrow40), ("PATO", _arrow42), ("PECO", _arrow44), ("TO", _arrow46), ("UO", _arrow48), ("EFO", _arrow50), ("NCIT", _arrow52), ("OMP", _arrow54)]))

def create_oauri(tsr: str, local_tan: str) -> str:
    match_value: Callable[[str, str], str] | None = Dictionary_tryFind(tsr, uri_parser_collection)
    if match_value is None:
        return OntobeeParser(tsr, local_tan)

    else: 
        return match_value(tsr)(local_tan)



__all__ = ["OntobeeParser", "BioregistryParser", "OntobeeDPBOParser", "MSParser", "POParser", "ROParser", "uri_parser_collection", "create_oauri"]

