import re
from collections import defaultdict
from datetime import date
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Type, Union

import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pydantic import BaseModel, ConfigDict, Field
from pandera.typing import Series, String  # type: ignore[attr-defined]
from typing_extensions import Annotated


# data level models
class MappingValue(BaseModel):
    """Represents a single input-to-output mapping rule."""
    input: Dict[str, str]
    output: Dict[str, str]

    class Config:
        frozen = True
        strict = True
        populate_by_name = True

class CustomData(BaseModel):
    uuid: str = Field(..., description="Stable identifier for the custom field")
    name: str = Field(..., description="Human-readable field name")
    technical_name: str = Field(
        ...,
        alias="technicalName",
        description="Canonical identifier used in the source system"
    )
    source: str = Field(..., description="Source category bucket")
    description: str = Field(..., description="Business description / purpose")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True

# Field scale models (Source/Target branches models)
class CustomSourceTarget(BaseModel):
    type: Literal["CUSTOM"] = Field(
        "CUSTOM",
        description="Discriminator—always 'CUSTOM' for this branch"
    )
    data: List[CustomData] = Field(
        ...,
        description="List of rich field descriptors coming from an external system"
    )

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class LibraryFieldDescriptor(BaseModel):
    """Rich metadata describing a library field target."""
    id: Optional[int] = None
    uuid: Optional[str] = None
    required: Optional[bool] = None
    field: Optional[str] = None
    field_label: Optional[Dict[str, str]] = Field(default=None, alias="fieldLabel")
    app_id: Optional[int] = Field(default=None, alias="appId")
    category: Optional[Dict[str, Any]] = None

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class LibrarySourceTarget(BaseModel):
    type: Literal["LIBRARY"] = Field(
        "LIBRARY",
        description="Discriminator—fixed value for library look-ups"
    )
    data: List[Union[str, LibraryFieldDescriptor]] = Field(
        ...,
        description="List of library field identifiers or metadata objects"
    )

    class Config:
        frozen = True
        strict = True
        populate_by_name = True

class EmptySourceTarget(BaseModel):
    type: Literal['EMPTY'] = Field(
        "EMPTY",
        description="Represents an empty value used as mapping field."
    )
    class Config:
        frozen = True
        strict = True
        populate_by_name = True
        extra = "allow"

class FixedSourceTarget(BaseModel):
    type: Literal["FIXED"] = Field(
        "FIXED",
        description="Discriminator—fixed value for constant/literal values"
    )
    data: str = Field(
        ...,
        description="A fixed literal value (e.g., '082')"
    )

    class Config:
        frozen = True
        strict = True
        populate_by_name = True

SourceTarget = Annotated[
    Union[CustomSourceTarget, LibrarySourceTarget, FixedSourceTarget, EmptySourceTarget],
    Field(discriminator="type", description="Polymorphic source/target contract"),
]


def _sanitize_alias(alias: str) -> str:
    """Normalize a scenario alias into a python-safe field name."""
    pythonic_name = re.sub(r"\W|^(?=\d)", "_", alias)
    pythonic_name = re.sub(r"_+", "_", pythonic_name).strip("_").lower()
    if not pythonic_name:
        pythonic_name = "field"
    if pythonic_name[0].isdigit():
        pythonic_name = f"field_{pythonic_name}"
    return pythonic_name

# Field scale models (Field properties)
class FieldProperties(BaseModel):
    """Metadata for a single field‑mapping detail returned by the API."""
    model_config = ConfigDict(extra="allow", frozen=True)
    logic: Optional[str] = None
    unique: bool = False
    required: bool = False
    mapping: Dict[str, Any] = Field(default_factory=dict)
    system_type: Optional[str] = None  # "source" or "target"
    original_alias: Optional[str] = None


# Down-stream models (from scenario to field, nested in scenario detail)
class ScenarioMappingConfiguration(BaseModel):
    # The type hint for 'values' is updated to use the new MappingValue model
    values: List[MappingValue] = Field(
        default_factory=list,
        description="Explicit mapping values when value mapping is required"
    )
    default_value: str = Field(
        default="",
        alias="defaultValue",
        description="Fallback value applied when no mapping match is found"
    )

    class Config:
        frozen = True
        strict = True
        populate_by_name = True

class ScenarioDetail(BaseModel):
    id: str = Field(..., description="Primary key of the detail record")
    logic: str = Field(default="", description="Optional transformation logic")
    unique: Optional[bool] = Field(default=False, description="Must this mapping be unique across the scenario?")
    required: Optional[bool] = Field(default=False, description="Is the field mandatory?")
    mapping_required: Optional[bool] = Field(
    default=False,
    alias="mappingRequired",
    description="Flag indicating whether an explicit mapping table is needed, right now not always present in reponse so defaults to False."
  )

    source: SourceTarget = Field(..., description="Source definition")
    target: SourceTarget = Field(..., description="Target definition")
    mapping: Optional[ScenarioMappingConfiguration] = Field(
        default=None,
        description="Mapping/value-translation configuration (may be absent)"
    )

    class Config:
        frozen = True
        strict = True
        populate_by_name = True

# Scenario models
class Scenario(BaseModel):
    id: str = Field(..., description="Scenario identifier")
    name: str = Field(..., description="Scenario display name")
    description: str = Field(default="", description="Scenario business context")
    details: List[ScenarioDetail] = Field(
        ..., description="Collection of field-level mappings"
    )

    class Config:
        frozen = True
        strict = True
        populate_by_name = True

class ParsedScenario(BaseModel):
    """
    Create object that contains all the information about a scenario that is returned by the API.
    This object is used to access the scenario data in a pythonic and flexible way.
    """
    # Core attributes
    name: str
    id: str
    details_count: int

    # Derived mappings
    source_to_target_map: Dict[str, List[str]]
    target_to_source_map: Dict[str, List[str]]
    field_properties: Dict[str, FieldProperties]
    all_source_fields: Set[str]
    all_target_fields: Set[str]
    unique_fields: List[str]
    required_fields: List[str]
    custom_fields: List[str]
    custom_fields_model: Optional[type] = None
    alias_to_pythonic: Optional[Dict[str, str]] = None
    pythonic_to_alias: Optional[Dict[str, str]] = None
    all_pythonic_source_fields: Optional[List[str]] = None
    source_pythonic_to_target: Optional[Dict[str, List[str]]] = None
    target_to_source_pythonic: Optional[Dict[str, Union[str, List[str]]]] = None

    # Direct lookup for value mappings from a source field
    source_to_value_mappings: Dict[str, List[ScenarioMappingConfiguration]]

    #public methods with specific functionality
    def get_mapped_field_names(self, field_name: str, direction: str = "source_to_target") -> List[str]:
        """
        Return all mapped fields for `field_name` based on the mapping `direction`.

        Args:
            field_name: The name of the field to look up.
            direction: Can be "source_to_target" (default) or "target_to_source".

        Returns:
            A list of mapped field names.
        """
        if direction == "source_to_target":
            return self.source_to_target_map.get(field_name, [])
        if direction == "target_to_source":
            return self.target_to_source_map.get(field_name, [])
        raise ValueError("Direction must be 'source_to_target' or 'target_to_source'.")

    def get_value_mappings(self, source_field_name: str) -> List[ScenarioMappingConfiguration]:
        """
        Return all value mapping configurations for a given source field.
        """
        return self.source_to_value_mappings.get(source_field_name, [])

    def get_source_fields_with_value_mappings(self) -> List[str]:
        """Returns a list of source fields that have value mappings."""
        return list(self.source_to_value_mappings.keys())

    def has_field(self, field_name: str, field_type: Optional[str] = None) -> bool:
        """Check field existence in scenario. Can denote source or target, else looks for both."""
        if field_type == "source":
            return field_name in self.all_source_fields
        if field_type == "target":
            return field_name in self.all_target_fields
        return field_name in self.all_source_fields or field_name in self.all_target_fields

    #Dunder methods for pythonic field access
    def __getitem__(self, field_id: str) -> FieldProperties:
        """Enable dict-style access to field properties: `scenario['customer_id']`."""
        try:
            return self.field_properties[field_id]
        except KeyError as exc:
            raise KeyError(f"Field '{field_id}' not found in scenario '{self.name}'.") from exc

    def __getattr__(self, name: str) -> FieldProperties:
        """Enable attribute-style access to field properties: `scenario.customer_id.unique`."""
        if name.startswith("_") or name in self.__dict__ or name in self.__class__.__dict__:
            return super().__getattribute__(name)
        try:
            return self.field_properties[name]
        except KeyError as exc:
            raise AttributeError(f"'{name}' is not a valid field in scenario '{self.name}'.") from exc

    def __repr__(self) -> str:
        """A human-friendly string representation."""
        return (
            f"<ParsedScenario name='{self.name}' id='{self.id}' "
            f"details={self.details_count} unique={len(self.unique_fields)} required={len(self.required_fields)}>"
        )

    @classmethod
    def from_api_dict(cls, scenario: Dict[str, Any], source_sdk: Any, sdk_mapping_config: Any) -> "ParsedScenario":
        """
        Factory method to transform raw API scenario data into a ParsedScenario object.

        This method processes the raw scenario dictionary from the API and:
        - Extracts field mappings from scenario details
        - Builds bidirectional source-to-target and target-to-source mapping dictionaries
        - Creates field properties for each field with metadata (unique, required, logic, etc.)
        - Identifies all source and target fields
        - Categorizes fields by their properties (unique, required)

        Args:
            scenario (Dict[str, Any]): Raw scenario dictionary from the BrynQ API containing
                                     'name', 'id', 'details' and other scenario metadata.

        Returns:
            ParsedScenario: A fully parsed scenario object with convenient access methods
                          for field mappings, properties, and validation capabilities.
        """
        details = scenario.get("details", [])
        src_map: Dict[str, Set[str]] = defaultdict(set)
        tgt_map: Dict[str, Set[str]] = defaultdict(set)
        props: Dict[str, FieldProperties] = {}
        source_to_value_maps: Dict[str, List[ScenarioMappingConfiguration]] = defaultdict(list)
        custom_aliases: Set[str] = set()
        custom_alias_order: List[str] = []

        def _extract_names_from_branch(branch: SourceTarget) -> Set[str]:
            """Normalise source/target branch data into canonical field names."""
            if isinstance(branch, CustomSourceTarget):
                names = {item.technical_name for item in branch.data if item.technical_name}
                # names = {_sanitize_alias(name) for name in names}
                if names:
                    return names
                return {item.uuid for item in branch.data if getattr(item, "uuid", None)}
            if isinstance(branch, LibrarySourceTarget):
                names: Set[str] = set()
                for entry in branch.data:
                    if isinstance(entry, str):
                        names.add(entry)
                    else:
                        if entry.field:
                            names.add(entry.field)
                        elif entry.uuid:
                            names.add(entry.uuid)
                return names
            if isinstance(branch, FixedSourceTarget):
                return set()
            if isinstance(branch, EmptySourceTarget):
                return set()

        for detail in details:
            detail_model = ScenarioDetail.model_validate(detail)

            source_names = _extract_names_from_branch(detail_model.source)
            target_names = _extract_names_from_branch(detail_model.target)

            for s_name in source_names:
                src_map[s_name].update(target_names)
            for t_name in target_names:
                tgt_map[t_name].update(source_names)

            mapping_config = detail_model.mapping
            if mapping_config and mapping_config.values:
                key = '|'.join(sorted(source_names)) if source_names else detail_model.id
                source_to_value_maps[key].append(mapping_config)

            base_props = FieldProperties.model_validate(detail)

            # Create source field properties
            for field_name in source_names:
                source_props = base_props.model_copy(update={"system_type": "source", "original_alias": field_name})
                props[field_name] = source_props
                if detail_model.source.type == "CUSTOM":
                    if field_name not in custom_aliases:
                        custom_aliases.add(field_name)
                        custom_alias_order.append(field_name)

            # Create target field properties
            for field_name in target_names:
                target_props = base_props.model_copy(update={"system_type": "target", "original_alias": field_name})
                props[field_name] = target_props

        custom_field_aliases = custom_alias_order
        # Create a Pandera schema model for custom fields. This is needed to be able to call custom fields in SDK's
        custom_fields_model = cls._build_custom_field_model(custom_field_aliases) if custom_field_aliases else None

        all_source_fields = set(src_map.keys())
        unique_fields = [fid for fid, props in props.items() if props.unique]
        required_fields = [fid for fid, props in props.items() if props.required]
        source_to_target_map = {k: sorted(v) for k, v in src_map.items()}
        target_to_source_map = {k: sorted(v) for k, v in tgt_map.items()}
        all_target_fields = set(tgt_map.keys())

        alias_to_pythonic: Optional[Dict[str, str]] = None
        pythonic_to_alias: Optional[Dict[str, str]] = None
        source_pythonic_to_target: Optional[Dict[str, List[str]]] = None
        target_to_source_pythonic: Optional[Dict[str, Union[str, List[str]]]] = None
        all_pythonic_source_fields: Optional[List[str]] = None

        if source_sdk and sdk_mapping_config:
            alias_to_pythonic = cls._generate_sdk_alias_mappings(
                scenario_name=scenario.get("name", "Unnamed"),
                source_fields=all_source_fields,
                source_sdk=source_sdk,
                sdk_mapping_config=sdk_mapping_config,
            )

            alias_to_pythonic = cls._merge_custom_alias_mappings(alias_to_pythonic, custom_aliases)
            pythonic_source_to_target: Dict[str, List[str]] = {}
            for alias, targets in source_to_target_map.items():
                pythonic_key = alias_to_pythonic.get(alias, alias)
                pythonic_targets = [alias_to_pythonic.get(target, target) for target in targets]
                pythonic_source_to_target[pythonic_key] = pythonic_targets

            pythonic_target_to_source: Dict[str, List[str]] = {}
            for alias, sources in target_to_source_map.items():
                pythonic_key = alias_to_pythonic.get(alias, alias)
                pythonic_sources = [alias_to_pythonic.get(source, source) for source in sources]
                pythonic_target_to_source[pythonic_key] = pythonic_sources

            pythonic_props: Dict[str, FieldProperties] = {}
            for alias, field_props in props.items():
                pythonic_key = alias_to_pythonic.get(alias, alias)
                updated_props = field_props.model_copy(update={"original_alias": alias})
                pythonic_props[pythonic_key] = updated_props
            props = pythonic_props

            unique_fields = [alias_to_pythonic.get(field, field) for field in unique_fields]
            required_fields = [alias_to_pythonic.get(field, field) for field in required_fields]
            all_source_fields = {alias_to_pythonic.get(field, field) for field in all_source_fields}
            all_target_fields = {alias_to_pythonic.get(field, field) for field in all_target_fields}

            pythonic_source_to_value_maps: Dict[str, List[ScenarioMappingConfiguration]] = {}
            for alias_key, mappings in source_to_value_maps.items():
                if "|" in alias_key:
                    parts = alias_key.split("|")
                    pythonic_parts = [alias_to_pythonic.get(part, part) for part in parts]
                    pythonic_key = "|".join(sorted(pythonic_parts))
                else:
                    pythonic_key = alias_to_pythonic.get(alias_key, alias_key)
                pythonic_source_to_value_maps[pythonic_key] = mappings
            source_to_value_maps = pythonic_source_to_value_maps

            source_to_target_map = pythonic_source_to_target
            target_to_source_map = pythonic_target_to_source
            source_pythonic_to_target = pythonic_source_to_target

            target_to_source_pythonic = {}
            for pythonic_source, pythonic_targets in source_pythonic_to_target.items():
                for target in pythonic_targets:
                    existing = target_to_source_pythonic.get(target)
                    if existing is None:
                        target_to_source_pythonic[target] = pythonic_source
                    elif isinstance(existing, list):
                        if pythonic_source not in existing:
                            existing.append(pythonic_source)
                    else:
                        if existing != pythonic_source:
                            target_to_source_pythonic[target] = [existing, pythonic_source]

            all_pythonic_source_fields = sorted(source_pythonic_to_target.keys())
            pythonic_to_alias = {py_name: alias for alias, py_name in alias_to_pythonic.items()}

        instance = cls(
            name=scenario.get("name", "Unnamed"),
            id=scenario.get("id", ""),
            details_count=len(details),
            source_to_target_map=source_to_target_map,
            target_to_source_map=target_to_source_map,
            field_properties=props,
            unique_fields=unique_fields,
            required_fields=required_fields,
            custom_fields=[alias_to_pythonic.get(alias, alias) for alias in custom_field_aliases] if alias_to_pythonic else custom_field_aliases,
            custom_fields_model=custom_fields_model,
            all_source_fields=all_source_fields,
            all_pythonic_source_fields=all_pythonic_source_fields,
            all_target_fields=all_target_fields,
            source_to_value_mappings=dict(source_to_value_maps),
            alias_to_pythonic=alias_to_pythonic,
            source_pythonic_to_target=source_pythonic_to_target,
            target_to_source_pythonic=target_to_source_pythonic,
            pythonic_to_alias=pythonic_to_alias,
        )
        return instance

    @staticmethod
    def _merge_custom_alias_mappings(alias_to_pythonic: Dict[str, str], custom_aliases: Set[str]) -> Dict[str, str]:
        """Ensure custom aliases obtain unique pythonic names."""
        merged_mapping = dict(alias_to_pythonic)
        existing_pythonic = set(merged_mapping.values())

        for alias in custom_aliases:
            if alias in merged_mapping:
                continue
            base_name = _sanitize_alias(alias)
            candidate = base_name
            counter = 1
            while candidate in existing_pythonic:
                counter += 1
                candidate = f"{base_name}_{counter}"
            merged_mapping[alias] = candidate
            existing_pythonic.add(candidate)

        return merged_mapping

    @staticmethod
    def _generate_sdk_alias_mappings(
        scenario_name: str,
        source_fields: Set[str],
        source_sdk: Any,
        sdk_mapping_config: Dict,
    ) -> Dict[str, str]:
        """
        Performs a strict validation of source fields against source SDK schemas.
        This static method is a self-contained helper for the factory.
        """
        # get schema classes and extract pythonic mappings
        source_alias_to_pythonic: Dict[str, str] = {}

        mapping = sdk_mapping_config.get(scenario_name)
        if mapping is None:
            raise ValueError(f"No SDK mapping found for scenario '{scenario_name}'")
        if isinstance(mapping, str):
            schema_classes = [mapping]
        elif isinstance(mapping, list):
            schema_classes = mapping
        elif isinstance(mapping, dict) and 'tables' in mapping:
            schema_classes = mapping['tables']
        else:
            raise ValueError(f"Invalid SDK mapping format for scenario '{scenario_name}': {mapping}")

        for schema_class_name in schema_classes:
            sdk_attr_name = schema_class_name.replace('Schema', '').lower()  # e.g. 'people' from PeopleSchema
            clss = getattr(source_sdk, sdk_attr_name)
            schema_clss = clss.schema
            schema_vars = vars(schema_clss)
            # Loop over the schema class attributes
            for pythonic_field_name, field_info in schema_vars.items():
                if hasattr(field_info, '__class__') and 'FieldInfo' in field_info.__class__.__name__:
                    # Extract alias from FieldInfo object
                    alias = str(field_info).split('"')[1]  # Get the string between quotes
                    source_alias_to_pythonic[alias] = pythonic_field_name

        schema_field_mappings = {
            alias: pythonic
            for alias, pythonic in source_alias_to_pythonic.items()
            if alias in source_fields
        }

        return schema_field_mappings

    @staticmethod
    def _build_custom_field_model(custom_fields: List[str]) -> Optional[type]:
        """
        Create a Pandera schema model for custom fields configured in a scenario.

        Args:
            custom_fields: Source field names from the BrynQ scenario.

        Returns:
            A dynamically generated BrynQ Pandera model class or None when no fields can be mapped.
        """
        annotations: Dict[str, Any] = {}
        model_fields: Dict[str, Any] = {}

        for field in custom_fields:
            alias = str(field)
            pythonic_name = _sanitize_alias(alias)

            annotations[pythonic_name] = Optional[Series[String]]
            model_fields[pythonic_name] = pa.Field(coerce=True, nullable=True, alias=str(alias))

        model_fields["__annotations__"] = annotations
        model = type("CustomFieldModel", (BrynQPanderaDataFrameModel,), model_fields)
        return model
    class Config:
        frozen = False
        strict = True
        populate_by_name = True
