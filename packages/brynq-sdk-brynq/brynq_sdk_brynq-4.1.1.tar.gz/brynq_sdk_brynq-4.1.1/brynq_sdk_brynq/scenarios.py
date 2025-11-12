"""
Scenarios sdk for BrynQ.
This module provides a class for managing scenarios in BrynQ, allowing you to fetch and parse scenarios from the BrynQ API,

In the BrynQ frontend, there is a scenarios tab in the interfaces of customers, e.g. https://ssc.app.brynq.com/interfaces/19/scenarios (id may differ).
This tab contains scenarios like 'Personal information' or 'Adres'.
In each scenario, you can see the fields that are available, how they map from source to target, and its properties (unique, required, etc.)

General usage
- The (parsed) scenario object can be accessed as a dictionary*, e.g. self.scenarios['Personal information'].
*Why dict? -> name of the scenario is often not python friendly.

- The parsed scenario object attributes such as scenario properties, its fields and the properties of those fields can be accessed using either dict or dot notation**:
e.g. self.scenarios['Personal information'].surname.required == self.scenarios['Personal information']['surname'].required
**why both dict and dot notation? -> follow pandas workflow, with same access methods. scenario can be considered 'the dataframe', and the fields the 'columns'. so df.column and df['column'] are the same.

# Example usage
We can use the Taskscheduler to access this data, as it inherits from BrynQ and thus the interfaces object (and thus the scenarios object ...)
below you can see setup of getting scenario data and some example usage.

class Koppeling(TaskScheduler):
    def __init__(self):
        super().__init__(data_interface_id=19)
        self.scenarios = self.brynq.interfaces.scenarios.get()

    def run(self):
        #most general methods that operate on all scenarios
        self.scenarios.find_scenarios_with_field(field_name = 'employee_id')                        #returns empty (a list of scenarios that contain the field 'employee_id', defaults to source)
        self.scenarios.find_scenarios_with_field(field_name = 'employee_id', field_type = 'target') #returns [<ParsedScenario name='Personal information' id='3c7f8e04-5b74-408f-a2d8-ad99b924a1af' details=15 unique=2 required=20>, <ParsedScenario name='Adres' (...)]
        self.scenarios.scenario_names                                                               #['Personal information', 'Adres', 'Bank Account', 'Contract Information', (...)]


        #base parsed scenario attributes, which are dynamically made into python objects.
        #scenario level attributes
        self.scenarios['Personal information']                                                      #returns a ParsedScenario object <ParsedScenario name='Personal information' id='3c7f8e04-5b74-408f-a2d8-ad99b924a1af' details=15 unique=2 required=20>
        self.scenarios['Personal information'].name                                                 #returns 'Personal information'
        self.scenarios['Personal information'].id                                                   #returns '3c7f8e04-5b74-408f-a2d8-ad99b924a1af'
        self.scenarios['Personal information'].details_count                                        #returns 15
        self.scenarios['Personal information'].source_to_target_map                                 #returns {'work.employeeIdInCompany': [], 'root.firstName': ['firstname'], 'root.surname': ['lastname'], (...)}
        self.scenarios['Personal information'].target_to_source_map                                 #returns {'employee_id': [], 'firstname': ['root.firstName'], 'lastname': ['root.surname'], (...)}
        self.scenarios['Personal information'].field_properties                                     #returns {'employee_id': FieldProperties(logic='', unique=True, required=True, mapping={'values': [], 'default...a': ['personal_information-employee_id']}), 'work.employeeIdInCompany': FieldProperties(logic='Field is only used to detect new employees and not send to Dat...}, target={'type': 'LIBRARY', 'data': []}), (...)}
        self.scenarios['Personal information'].unique_fields                                        #returns ['employee_id', 'work.employeeIdInCompany']
        self.scenarios['Personal information'].required_fields                                      #returns ['employee_id', 'work.employeeIdInCompany', 'root.firstName', 'firstname', 'root.surname',(...)]

        #field level attributes (accesible via the field property class; logic, unique, required, mapping, system_type)
        self.scenarios['Personal information']['root.firstName'].required                           #returns True
        self.brynq.interfaces.scenarios['Personal information'].firstname.required                  #returns True
        self.scenarios['Personal information']['root.firstName'].unique                             #returns False
        self.scenarios['Personal information'].get_mapped_field_names('root.surname')               #returns ['lastname']

        #dunder methods (python object structure- e.g. calling len, iterate over object, etc)
        n_of_scenarios = len(self.scenarios)    #returns 13

        #iterate over scenarios
        for scenario in self.scenarios:
            print(scenario.name)                                                            #returns 'Personal information', 'Adres', ...
            print(scenario.id)                                                              #returns '3c7f8e04-5b74-408f-a2d8-ad99b924a1af', 'c20dfca5-d30e-4f57-bfe9-8c9fc7a956a9', ...

            #anything useful u can get from the scenario object (example returns are from 'Adres' scenario, but are in reality for each scenario retrieved as you iterate)
            scenario.source_to_target_map                                                   #returns {'address.line1': ['house_number', 'street'], 'address.postCode': ['postalcode', 'postalcode_foreign_country'], 'address.city': ['city'], 'address.line2': ['supplement'], 'address_country': ['country']}
            all_source_fields = scenario.all_source_fields                                  #returns {'address.line2', 'address.line1', 'address.postCode', 'address.city', 'address_country'}
            all_target_fields = scenario.all_target_fields                                  #returns {'employee_id', 'city', 'house_number', 'postalcode', 'supplement', 'postalcode_foreign_country', 'street', 'country'}
            required_fields = scenario.required_fields                                      #returns ['employee_id', 'address.line1', 'house_number', 'postalcode', 'address.city', 'city', 'street', 'address.line2', 'supplement', 'address_country', 'country']
            unique_fields = scenario.unique_fields                                          #returns ['employee_id', 'house_number', 'postalcode']
"""
# imports
from __future__ import annotations

import re
import warnings
from collections import defaultdict
from functools import cached_property
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Union

import pandas as pd
import requests
from pydantic import BaseModel, ConfigDict, Field

from brynq_sdk_functions import Functions

from .schemas.scenarios import FieldProperties, ParsedScenario, Scenario

# TOOD: Value mapping return string None if empty, should be a real None
# TODO: employee_id, id and person_id are always kept when renaming fields, but thats only relevant for HiBob.

class Scenarios():
    """
    Provides convenient access to BrynQ scenarios, with lookups and a Pythonic interface.
    """
    def __init__(self,
                 brynq_instance: Any
    ):
        """
        Initialize the manager, automatically fetching and parsing all scenarios.

        #example (direct) usage, usually will be inherited from BrynQ/TaskScheduler.
        scenarios = Scenarios(brynq_instance)
        scenarios.get()
        scenarios.find_scenarios_with_field(field_name = 'employee_id')
        scenarios['Personal information'].surname.required
        scenarios['Personal information'].surname.unique
        scenarios['Personal information'].surname.mapping

        Args:
            brynq_instance: An authenticated BrynQ client instance.
            strict: If True, will raise an error on any data validation failure.
        """
        self._brynq = brynq_instance

        #attributes to be filled in get()
        self.raw_scenarios: Optional[List[Dict]] = None
        self.scenarios: Optional[List[ParsedScenario]] = None
        self.source_system: Optional[Any] = None
        self.source_sdk_config: Optional[Dict] = None
        self.target_system = None

    #public methods
    def get(self, strict: bool = True, setup_helper: bool = True) -> List[ParsedScenario]:
        """Fetches scenarios from the API, parses themand returns them as a list.

        Args:
            strict (bool): If True, will raise an error on any data validation failure.

        Returns:
            List[ParsedScenario]: A list of parsed scenario objects retrieved from the API.
        """
        if self.scenarios is None:
            self.raw_scenarios = self._fetch_from_api(strict=strict)
            self.scenarios = [ParsedScenario.from_api_dict(
                                                                scenario=s,
                                                                source_sdk=self.source_system,
                                                                sdk_mapping_config=self.source_sdk_config
                                                            )
                                                                for s in self.raw_scenarios if "name" in s]
        return self.scenarios


    #public convenience methods
    def find_scenarios_with_field(
        self, field_name: str, field_type: str = "source"
    ) -> List[ParsedScenario]:
        """Find all scenarios that contain a specific field.

        Args:
            field_name (str): The name of the field to search for.
            field_type (str, optional): The type of field to search in ("source" or "target"). Defaults to "source".

        Returns:
            List[ParsedScenario]: A list of scenarios containing the specified field.
        """
        return [
            p for p in self.get()
            if p.has_field(field_name, field_type=field_type)
        ]

    #(cached) properties - blijft hangen als attribute
    @cached_property
    def scenario_names(self) -> List[str]:
        """A list of all scenario names. call as attribute, e.g. self.scenarios.scenario_names"""
        return [s.name for s in self.get()] if self.scenarios is not None else []

    #dunder methods for pythonic access to raw scenarios
    def __getitem__(self, scenario_name: str) -> ParsedScenario:
        """Enable dict-style access: `scenarios['Demo']`."""
        scenarios = {s.name: s for s in self.get()}
        if scenario_name not in scenarios:
            raise KeyError(f"Scenario '{scenario_name}' not found.")
        return scenarios[scenario_name]

    def __iter__(self) -> Iterator[ParsedScenario]:
        """Iterate over the parsed scenarios."""
        return iter(self.get())

    def __len__(self) -> int:
        """Return the number of available scenarios."""
        return len(self.get())

    #internal helpers
    @staticmethod
    def _to_attribute_name(name: str) -> str:
        """Converts a scenario name into a valid, snake_case Python attribute.
        e.g. 'Personal information' -> 'personal_information'
        Args:
            name (str): The (scenario/field) name to convert.
        Returns:
            str: The snake_case, valid Python attribute name derived from the scenario name.
        """
        #sub spaces and hyphens with an underscore
        s = name.lower().replace(" ", "_").replace("-", "_")
        #sub non-word characters with an empty string
        s = re.sub(r"[^\w_]", "", s)
        #sub consecutive underscores wiht a single underscore
        s = re.sub(r"_+", "_", s)
        #if the first character is a digit, add an underscore in front
        if s and s[0].isdigit():
            return f"_{s}"
        return s

    def _fetch_from_api(self, strict: bool = True) -> List[Dict[str, Any]]:
        """Retrieve and validate scenario payloads from the API as is.
        Args:
            strict (bool): If True, will raise an error on any data validation failure.
        Returns:
            List[Dict[str, Any]]: A list of scenario payloads retrieved from the API.
        """
        response = self._brynq.brynq_session.get(
            url=f"{self._brynq.url}interfaces/{self._brynq.data_interface_id}/scenarios",
            timeout=self._brynq.timeout,
        )
        response.raise_for_status()
        scenario_list = response.json()
        if not isinstance(scenario_list, list):
            raise TypeError(f"Expected a list of scenarios, but got {type(scenario_list).__name__}.")

        valid_scenarios, invalid_scenarios = Functions.validate_pydantic_data(
            scenario_list, schema=Scenario, debug=True
        )

        if invalid_scenarios:
            msg = f"{len(invalid_scenarios)} scenario(s) failed validation and were skipped."
            if strict:
                raise ValueError(f"Invalid scenario data found: {msg}")
            warnings.warn(msg, UserWarning)

        return valid_scenarios

    #public helper functions to be used in project specific logic and require a dataframe with data of corresponding scenario.
    def add_fixed_values(self, df: pd.DataFrame, scenario_name: str) -> pd.DataFrame:
        """
        Add fixed values to the dataframe.
        """
        df_with_fixed = df.copy()
        scenario = None
        for s in self.scenarios:
            if getattr(s, "name", None) == scenario_name:
                scenario = s
                break
        if scenario is None:
            raise ValueError(f"Scenario with name '{scenario_name}' not found.")
        for _, value in scenario.field_properties.items():
            try:
                source_type = value.source['type']
                if source_type == 'FIXED':
                    source_value = value.source['data']
                    target_field = value.target['data'][0]['field']
                    df_with_fixed[target_field] = source_value
            except Exception as e:
                warnings.warn(f"Error adding fixed value to dataframe: {e}")
                continue
        return df_with_fixed

    def apply_value_mappings(self, df: pd.DataFrame, scenario_name: str, drop_unmapped: bool = False, fix_source_val: bool = True, fix_target_val: bool = True) -> Tuple[pd.DataFrame, Set[str]]:
        """
        Apply value mappings from the scenario.
        For example, maps 'F' to '1' and 'M' to '0' for gender.
        Unmapped values are set to a default if provided, otherwise they remain unchanged.
        Returns the modified dataframe and a set of pythonic source fields that were handled.
        """
        scenario = None
        # Find the correct scenario object based on its name
        for s in self.scenarios:
            if getattr(s, "name", None) == scenario_name:
                scenario = s
                break

        # Exit early if the scenario has no value mappings to apply
        if not hasattr(scenario, 'source_to_value_mappings') or not scenario.source_to_value_mappings:
            return df, set()

        source_to_value_mappings = scenario.source_to_value_mappings
        alias_to_pythonic = scenario.alias_to_pythonic or {}
        handled_source_fields = set()

        # Process each source field that has value mappings
        for source_field_alias, mappings in source_to_value_mappings.items():
            # Handle multiple source fields joined with pipe symbol
            source_field_aliases = source_field_alias.split('|')
            source_field_aliases = sorted(source_field_aliases)
            pythonic_source_fields = []

            # Convert each source field alias to pythonic format and validate existence
            all_fields_exist = True
            for field_alias in source_field_aliases:
                pythonic_field = alias_to_pythonic.get(field_alias, field_alias)
                if pythonic_field not in df.columns and field_alias in df.columns:
                    # Dataframe already uses pythonic naming; fall back to the alias itself
                    pythonic_field = field_alias
                if pythonic_field not in df.columns or pythonic_field is None:
                    warnings.warn(f"Source field {field_alias.strip()} not found in dataframe.")
                    all_fields_exist = False
                    break
                pythonic_source_fields.append(pythonic_field)

            # Skip if any of the source fields are missing
            if not all_fields_exist:
                continue

            # Ensure all columns are of string type and track handled fields
            for pythonic_field in pythonic_source_fields:
                df[pythonic_field] = df[pythonic_field].astype(str)
                handled_source_fields.add(pythonic_field)

            # For mapping operations, we'll use the combined values if multiple fields
            if len(pythonic_source_fields) == 1:
                source_column_for_mapping = pythonic_source_fields[0]
            else:
                # Create a temporary combined column for mapping
                combined_field_name = '|'.join(pythonic_source_fields)
                df[combined_field_name] = df[pythonic_source_fields].apply(
                    lambda row: '|'.join(row.astype(str)), axis=1
                )
                source_column_for_mapping = combined_field_name

            # Process each mapping rule (i.e., each target column to be created from this source)
            for mapping in mappings:
                # Build a dictionary of all replacements for this target column
                replacements = {}
                for mapping_value in mapping.values:
                    # This complex access is based on the provided JSON structure
                    source_map_val = mapping_value.input
                    target_map_val = mapping_value.output

                    # Handle different cases for source and target mapping
                    if source_map_val and target_map_val and len(target_map_val) == 1:
                        target_val = list(target_map_val.values())[0]
                        # Strip whitespace and newline characters from target value
                        target_val = target_val.strip()

                        # Case 1: Single source field to single target field
                        if len(source_map_val) == 1:
                            source_val = list(source_map_val.values())[0]

                            # Strip whitespace and newline characters from both values
                            source_val = source_val.strip()
                            target_val = target_val.strip()

                            # Clean the mapping values to handle different delimiters
                            if (fix_source_val) and ('-' in source_val or ':' in source_val):
                                source_val = source_val.replace('-', ':').split(':')[0]
                            if (fix_target_val) and ('-' in target_val or ':' in target_val):
                                target_val = target_val.replace('-', ':').split(':')[0]

                            replacements[source_val] = target_val

                        # Case 2: Multiple source fields to single target field
                        elif len(source_map_val) > 1 and len(pythonic_source_fields) > 1:
                            # Extract target field name using the same logic as later in the code
                            target_field = list(mapping.values[0].output)[0].split('-')[1]

                            # Transform keys in source_map_val using the target field logic
                            transformed_source_map = {}
                            for key, value in source_map_val.items():
                                # Apply the same transformation logic
                                transformed_key = key.split('-')[1] if '-' in key else key
                                transformed_source_map[transformed_key] = value

                            # Extract values from each source field in the mapping using transformed keys
                            source_values = []
                            for field_alias in source_field_aliases:
                                if field_alias in transformed_source_map:
                                    field_val = transformed_source_map[field_alias]
                                    # Strip whitespace and newline characters
                                    field_val = field_val.strip()
                                    # Clean the mapping values
                                    if (fix_source_val) and ('-' in field_val or ':' in field_val):
                                        field_val = field_val.replace('-', ':').split(':')[0]
                                    source_values.append(field_val)

                            # Only create mapping if we have values for all source fields
                            if len(source_values) == len(source_field_aliases):
                                combined_source_val = '|'.join(source_values)

                                # Strip whitespace and newline characters from target value
                                target_val = target_val.strip()

                                # Clean target value
                                if (fix_target_val) and ('-' in target_val or ':' in target_val):
                                    target_val = target_val.replace('-', ':').split(':')[0]

                                replacements[combined_source_val] = target_val

                # Apply the mappings if any were found
                if replacements:
                    # Determine if we modify the column in-place or create a new one
                    if len(mappings) == 1:
                        target_field = source_column_for_mapping
                    else:
                        # Extract the target field name from the mapping configuration
                        target_field = list(mapping.values[0].output)[0].split('-')[1]

                    # Retrieve the default value from the mapping configuration
                    default_val = mapping.default_value

                    # Apply mapping: use the replacement if key exists, otherwise use the default value.
                    # If no default_val is provided, it falls back to the original value (x).
                    df[target_field] = df[source_column_for_mapping].apply(
                        lambda x: replacements.get(x, default_val if default_val else x)
                    )

                    # Dropping unmapped values only makes sense if a default value is NOT being used
                    if drop_unmapped and not default_val:
                        # Keep only the rows with target values
                        df = df[df[source_column_for_mapping].isin(list(replacements.values()))]

        return df, handled_source_fields

    def rename_fields(self, df: pd.DataFrame, scenario_name: str = None, field_mapping: Dict[str, Union[str, List[str]]] = None,
                    columns_to_keep: List[str] = None, drop_unmapped: bool = True) -> pd.DataFrame:
        """
        Rename fields with clear, separate logic for unique and non-unique mappings.
        """
        if columns_to_keep is None:
            columns_to_keep = []

        if scenario_name and not field_mapping:
            parsed_scenario = self[scenario_name]
            use_pythonic = self.source_system and self.source_sdk_config
            field_mapping = parsed_scenario.source_pythonic_to_target if use_pythonic else parsed_scenario.source_to_target_map
        elif not field_mapping:
            raise ValueError("Either scenario_name or field_mapping must be provided")

        # Build a definitive plan for all renaming tasks
        # This will store the final plan, e.g., {'source_A': ['target_1', 'target_2']}
        planned_tasks = defaultdict(list)
        # This set will help us identify which targets are part of a conflict.
        conflicting_targets = {
            target for target, sources in parsed_scenario.target_to_source_map.items() if len(sources) > 1
        }

        # Plan the renaming for all NON-UNIQUE (conflicting)
        # NOTE: commented out since there is now logic below to handle conflicting targets (when there are multiple sources for a target)
        # for target in conflicting_targets:
        #     source_list = parsed_scenario.target_to_source_map.get(target, [])
            # conflicting_pythonic_sources = sorted([
            #     parsed_scenario.alias_to_pythonic.get(s, s) for s in source_list
            # ])
            # for i, pythonic_source in enumerate(conflicting_pythonic_sources):
            #     new_name = f"{target}_{i + 1}"
            #     planned_tasks[pythonic_source].append(new_name)

        # Plan the renaming for all UNIQUE sources
        for source, target in field_mapping.items():
            individual_targets = []
            if isinstance(target, str):
                individual_targets = [target]
            elif isinstance(target, list):
                individual_targets = target
            for target_field in individual_targets:
                if target_field not in conflicting_targets:
                    # If the target is not in our conflict list, it's a simple, unique mapping.
                    planned_tasks[source].append(target_field)

        for target in conflicting_targets:
            source_list = parsed_scenario.target_to_source_map.get(target, [])
            source_list = sorted(source_list)
            pythonic_source_list = [parsed_scenario.alias_to_pythonic.get(source, source) for source in source_list]
            source_list = '|'.join(pythonic_source_list)
            planned_tasks[source_list].append(target)

        # Execute the plan on the DataFrame
        newly_created_target_fields = set()
        for source, final_targets in planned_tasks.items():
            if source in df.columns:
                for final_target_name in final_targets:
                    df[final_target_name] = df[source]
                    newly_created_target_fields.add(final_target_name)
            else:
                for final_target_name in final_targets:
                    df[final_target_name] = ''
                    newly_created_target_fields.add(final_target_name)

        # Cleanup and Finalizing Section
        if drop_unmapped:
            protected_columns = {'employee_id', 'person_id', 'id'} | newly_created_target_fields | set(columns_to_keep)
            columns_to_drop = [col for col in planned_tasks.keys() if col not in protected_columns]
            df = df.drop(columns=columns_to_drop, errors='ignore')
        all_expected_columns = list(protected_columns) + columns_to_keep
        final_df_columns = [col for col in df.columns if col in all_expected_columns]
        df = df[final_df_columns].copy()
        columns_missing_in_df = [col for col in all_expected_columns if col not in df.columns]
        if columns_missing_in_df:
            for col in columns_missing_in_df:
                df[col] = None

        return df
