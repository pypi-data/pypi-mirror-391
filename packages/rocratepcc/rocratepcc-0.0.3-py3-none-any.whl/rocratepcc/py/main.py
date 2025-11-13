from __future__ import annotations
from .fable_modules.arctrl_python.JsonIO.ldobject import ARCtrl_ROCrate_LDGraph__LDGraph_ToROCrateJsonString_71136F3F
from .fable_modules.arctrl_rocrate.Generic.creative_work import LDCreativeWork
from .fable_modules.arctrl_rocrate.Generic.dataset import LDDataset
from .fable_modules.arctrl_rocrate.Generic.defined_term import LDDefinedTerm
from .fable_modules.arctrl_rocrate.Generic.file import LDFile
from .fable_modules.arctrl_rocrate.Generic.person import LDPerson
from .fable_modules.arctrl_rocrate.ldcontext import LDContext
from .fable_modules.arctrl_rocrate.ldobject import (LDNode, LDNode_reflection, LDRef, LDGraph)
from .fable_modules.arctrl_rocrate.rocrate_context import init_v1_2draft
from .fable_modules.fable_library.list import FSharpList
from .fable_modules.fable_library.option import (value, default_arg)
from .fable_modules.fable_library.reflection import (TypeInfo, class_type)
from .fable_modules.fable_library.seq import (to_list, delay, collect, append, singleton, map)
from .fable_modules.fable_library.types import (FSharpRef, Array)
from .fable_modules.fable_library.util import IEnumerable_1

def _expr4018() -> TypeInfo:
    return class_type("ROCratePCC.CustomResourceDescriptor", None, CustomResourceDescriptor)


class CustomResourceDescriptor:
    def __init__(self, id: str, role: str) -> None:
        self.id: str = id
        self.role: str = role

    @property
    def Id(self, __unit: None=None) -> str:
        this: CustomResourceDescriptor = self
        return this.id

    @property
    def Role(self, __unit: None=None) -> str:
        this: CustomResourceDescriptor = self
        return this.role


CustomResourceDescriptor_reflection = _expr4018

def CustomResourceDescriptor__ctor_Z384F8060(id: str, role: str) -> CustomResourceDescriptor:
    return CustomResourceDescriptor(id, role)


def ResourceDescriptorType__get_ID(this: ResourceDescriptorType) -> str:
    if this == "constraint":
        return "#hasConstraint"

    elif this == "guidance":
        return "#hasGuidance"

    elif this == "example":
        return "#hasExample"

    elif isinstance(this, CustomResourceDescriptor):
        return this.Id

    else: 
        return "#hasSpecification"



def ResourceDescriptorType__get_Role(this: ResourceDescriptorType) -> str:
    if this == "constraint":
        return "http://www.w3.org/ns/dx/prof/role/constraints"

    elif this == "guidance":
        return "http://www.w3.org/ns/dx/prof/role/guidance"

    elif this == "example":
        return "http://www.w3.org/ns/dx/prof/role/example"

    elif isinstance(this, CustomResourceDescriptor):
        return this.Role

    else: 
        return "http://www.w3.org/ns/dx/prof/role/specification"



def _expr4019() -> TypeInfo:
    return class_type("ROCratePCC.Author", None, Author, LDNode_reflection())


class Author(LDNode):
    def __init__(self, orcid: str, name: str) -> None:
        super().__init__(("https://orcid.org/" + orcid) + "", [LDPerson.schema_type()])
        n: FSharpRef[Author] = FSharpRef(None)
        n.contents = self
        self.init_004042: int = 1
        LDDataset.set_name_as_string(n.contents, name)


Author_reflection = _expr4019

def Author__ctor_Z384F8060(orcid: str, name: str) -> Author:
    return Author(orcid, name)


def _expr4020() -> TypeInfo:
    return class_type("ROCratePCC.UsedType", None, UsedType, LDNode_reflection())


class UsedType(LDNode):
    def __init__(self, iri: str, name: str) -> None:
        super().__init__(iri, [LDDefinedTerm.schema_type()])
        n: FSharpRef[UsedType] = FSharpRef(None)
        n.contents = self
        self.init_004049_002D1: int = 1
        LDDataset.set_name_as_string(n.contents, name)


UsedType_reflection = _expr4020

def UsedType__ctor_Z384F8060(iri: str, name: str) -> UsedType:
    return UsedType(iri, name)


def _expr4021() -> TypeInfo:
    return class_type("ROCratePCC.License", None, License, LDNode_reflection())


class License(LDNode):
    def __init__(self, iri: str, name: str) -> None:
        super().__init__(iri, [LDCreativeWork.schema_type()])
        n: FSharpRef[License] = FSharpRef(None)
        n.contents = self
        self.init_004056_002D2: int = 1
        LDDataset.set_name_as_string(n.contents, name)


License_reflection = _expr4021

def License__ctor_Z384F8060(iri: str, name: str) -> License:
    return License(iri, name)


def _expr4022() -> TypeInfo:
    return class_type("ROCratePCC.TextualResource", None, TextualResource, LDNode_reflection())


class TextualResource(LDNode):
    def __init__(self, name: str, file_path: str, encoding_format: str, root_data_entity_id: str | None=None) -> None:
        super().__init__(file_path, [LDFile.schema_type()])
        n: FSharpRef[TextualResource] = FSharpRef(None)
        n.contents = self
        self.init_004061_002D3: int = 1
        LDDataset.set_name_as_string(n.contents, name)
        LDFile.set_encoding_format_as_string(n.contents, encoding_format)
        if root_data_entity_id is None:
            pass

        else: 
            id: str = root_data_entity_id
            n.contents.SetProperty(LDFile.about(), LDRef(id))



TextualResource_reflection = _expr4022

def TextualResource__ctor_5978D483(name: str, file_path: str, encoding_format: str, root_data_entity_id: str | None=None) -> TextualResource:
    return TextualResource(name, file_path, encoding_format, root_data_entity_id)


def _expr4023() -> TypeInfo:
    return class_type("ROCratePCC.ResourceDescriptor", None, ResourceDescriptor, LDNode_reflection())


class ResourceDescriptor(LDNode):
    def __init__(self, textual_resources: Array[TextualResource], resource_descriptor_type: ResourceDescriptorType) -> None:
        super().__init__(ResourceDescriptorType__get_ID(resource_descriptor_type), ["http://www.w3.org/ns/dx/prof/ResourceDescriptor"])
        n: FSharpRef[ResourceDescriptor] = FSharpRef(None)
        n.contents = self
        self.init_004072_002D4: int = 1
        n.contents.SetProperty("http://www.w3.org/ns/dx/prof/hasRole", LDRef(ResourceDescriptorType__get_Role(resource_descriptor_type)))
        n.contents.SetProperty("http://www.w3.org/ns/dx/prof/hasArtifact", textual_resources)


ResourceDescriptor_reflection = _expr4023

def ResourceDescriptor__ctor_40E96EF7(textual_resources: Array[TextualResource], resource_descriptor_type: ResourceDescriptorType) -> ResourceDescriptor:
    return ResourceDescriptor(textual_resources, resource_descriptor_type)


def _expr4024() -> TypeInfo:
    return class_type("ROCratePCC.Specification", None, Specification, ResourceDescriptor_reflection())


class Specification(ResourceDescriptor):
    def __init__(self, textual_resources: Array[TextualResource]) -> None:
        super().__init__(textual_resources, "specification")
        self.init_004081_002D5: int = 1


Specification_reflection = _expr4024

def Specification__ctor_Z715ED06F(textual_resources: Array[TextualResource]) -> Specification:
    return Specification(textual_resources)


def _expr4025() -> TypeInfo:
    return class_type("ROCratePCC.Constraint", None, Constraint, ResourceDescriptor_reflection())


class Constraint(ResourceDescriptor):
    def __init__(self, textual_resources: Array[TextualResource]) -> None:
        super().__init__(textual_resources, "constraint")
        self.init_004085_002D6: int = 1


Constraint_reflection = _expr4025

def Constraint__ctor_Z715ED06F(textual_resources: Array[TextualResource]) -> Constraint:
    return Constraint(textual_resources)


def _expr4026() -> TypeInfo:
    return class_type("ROCratePCC.Guidance", None, Guidance, ResourceDescriptor_reflection())


class Guidance(ResourceDescriptor):
    def __init__(self, textual_resources: Array[TextualResource]) -> None:
        super().__init__(textual_resources, "guidance")
        self.init_004089_002D7: int = 1


Guidance_reflection = _expr4026

def Guidance__ctor_Z715ED06F(textual_resources: Array[TextualResource]) -> Guidance:
    return Guidance(textual_resources)


def _expr4027() -> TypeInfo:
    return class_type("ROCratePCC.Example", None, Example, ResourceDescriptor_reflection())


class Example(ResourceDescriptor):
    def __init__(self, textual_resources: Array[TextualResource]) -> None:
        super().__init__(textual_resources, "example")
        self.init_004093_002D8: int = 1


Example_reflection = _expr4027

def Example__ctor_Z715ED06F(textual_resources: Array[TextualResource]) -> Example:
    return Example(textual_resources)


def _expr4034() -> TypeInfo:
    return class_type("ROCratePCC.RootDataEntity", None, RootDataEntity, LDNode_reflection())


class RootDataEntity(LDNode):
    def __init__(self, id: str, name: str, description: str, license: License, used_types: Array[UsedType], resource_descriptors: Array[ResourceDescriptor], authors: Array[Author]) -> None:
        super().__init__(id, [LDDataset.schema_type(), "http://www.w3.org/ns/dx/prof/Profile"])
        n: FSharpRef[RootDataEntity] = FSharpRef(None)
        n.contents = self
        self.init_004097_002D9: int = 1
        def _arrow4029(__unit: None=None) -> IEnumerable_1[LDNode]:
            def _arrow4028(rd: ResourceDescriptor) -> IEnumerable_1[LDNode]:
                return rd.GetPropertyNodes("http://www.w3.org/ns/dx/prof/hasArtifact")

            return collect(_arrow4028, resource_descriptors)

        textual_resources: Array[LDNode] = list(to_list(delay(_arrow4029)))
        def _arrow4033(__unit: None=None) -> IEnumerable_1[LDNode]:
            def _arrow4032(tr: LDNode) -> IEnumerable_1[LDNode]:
                def _arrow4031(__unit: None=None) -> IEnumerable_1[LDNode]:
                    def _arrow4030(ut: UsedType) -> LDNode:
                        return ut

                    return map(_arrow4030, used_types)

                return append(singleton(tr), delay(_arrow4031))

            return collect(_arrow4032, textual_resources)

        has_parts: FSharpList[LDNode] = to_list(delay(_arrow4033))
        LDDataset.set_license_as_creative_work(n.contents, license)
        LDDataset.set_name_as_string(n.contents, name)
        LDDataset.set_description_as_string(n.contents, description)
        n.contents.SetProperty("http://schema.org/author", authors)
        LDDataset.set_has_parts(n.contents, list(has_parts))
        n.contents.SetProperty("http://www.w3.org/ns/dx/prof/hasResource", resource_descriptors)


RootDataEntity_reflection = _expr4034

def RootDataEntity__ctor_Z58FF24F6(id: str, name: str, description: str, license: License, used_types: Array[UsedType], resource_descriptors: Array[ResourceDescriptor], authors: Array[Author]) -> RootDataEntity:
    return RootDataEntity(id, name, description, license, used_types, resource_descriptors, authors)


def _expr4035() -> TypeInfo:
    return class_type("ROCratePCC.Profile", None, Profile, LDNode_reflection())


class Profile(LDNode):
    def __init__(self, root_data_entity: RootDataEntity, license: License | None=None, ro_crate_spec: str | None=None) -> None:
        super().__init__("ro-crate-metadata.json", [LDCreativeWork.schema_type()])
        n: FSharpRef[Profile] = FSharpRef(None)
        n.contents = self
        self.init_0040114_002D10: int = 1
        LDDataset.set_abouts(n.contents, [root_data_entity])
        if license is not None:
            LDDataset.set_license_as_creative_work(n.contents, value(license))

        ro_crate_spec_1: str = default_arg(ro_crate_spec, "https://w3id.org/ro/crate/1.2")
        n.contents.SetProperty("http://purl.org/dc/terms/conformsTo", ro_crate_spec_1)

    def ToROCrateJsonString(self, spaces: int | None=None) -> str:
        this: Profile = self
        context: LDContext = init_v1_2draft()
        this.Compact_InPlace(context, False)
        graph: LDGraph = this.Flatten()
        graph.SetContext(context)
        return ARCtrl_ROCrate_LDGraph__LDGraph_ToROCrateJsonString_71136F3F(graph, spaces)


Profile_reflection = _expr4035

def Profile__ctor_6B2DF90D(root_data_entity: RootDataEntity, license: License | None=None, ro_crate_spec: str | None=None) -> Profile:
    return Profile(root_data_entity, license, ro_crate_spec)


__all__ = ["CustomResourceDescriptor_reflection", "ResourceDescriptorType__get_ID", "ResourceDescriptorType__get_Role", "Author_reflection", "UsedType_reflection", "License_reflection", "TextualResource_reflection", "ResourceDescriptor_reflection", "Specification_reflection", "Constraint_reflection", "Guidance_reflection", "Example_reflection", "RootDataEntity_reflection", "Profile_reflection"]

