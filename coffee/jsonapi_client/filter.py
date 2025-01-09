"""
JSON API Python client
https://github.com/qvantel/jsonapi-client

(see JSON API specification in http://jsonapi.org/)

Copyright (c) 2017, Qvantel
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Qvantel nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL QVANTEL BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import json
from typing import TYPE_CHECKING, Union, Dict, Sequence, Any

from coffee.schemas import schema_registry

if TYPE_CHECKING:
    FilterKeywords = Dict[str, Union[str, Sequence[Union[str, int, float]]]]
    IncludeKeywords = Sequence[str]


class Modifier:
    """
    Base class for query modifiers.
    You can derive your own class and use it if you have custom syntax.
    """

    def __init__(self, query_str: str = '') -> None:
        self._query_str = query_str

    def url_with_modifiers(self, base_url: str) -> str:
        """
        Returns url with modifiers appended.

        Example:
            Modifier('filter[attr1]=1,2&filter[attr2]=2').filtered_url('doc')
              -> 'GET doc?filter[attr1]=1,2&filter[attr2]=2'
        """
        filter_query = self.appended_query()
        fetch_url = f'{base_url}?{filter_query}'
        return fetch_url

    def appended_query(self) -> str:
        return self._query_str

    def __add__(self, other: 'Modifier') -> 'Modifier':
        mods = []
        for m in [self, other]:
            if isinstance(m, ModifierSum):
                mods += m.modifiers
            else:
                mods.append(m)
        return ModifierSum(mods)


class ModifierSum(Modifier):
    def __init__(self, modifiers):
        self.modifiers = modifiers

    def appended_query(self) -> str:
        return '&'.join(m.appended_query() for m in self.modifiers)


class Field:
    def __init__(self, name_parts):
        if isinstance(name_parts, str):
            self.name_parts = [name_parts]
        else:
            self.name_parts = name_parts

    def __getattr__(self, attr):
        return Field(self.name_parts + [attr])

    @property
    def _name(self):
        return '__'.join(self.name_parts)

    # Overload comparison operators
    def __eq__(self, other):
        return Expression(self._name, 'eq', other)

    def __ne__(self, other):
        return Expression(self._name, 'ne', other)

    def __gt__(self, other):
        return Expression(self._name, 'gt', other)

    def __ge__(self, other):
        return Expression(self._name, 'ge', other)

    def __lt__(self, other):
        return Expression(self._name, 'lt', other)

    def __le__(self, other):
        return Expression(self._name, 'le', other)

    # Additional operators can be added as needed
    def like(self, other):
        return Expression(self._name, 'like', other)

    def ilike(self, other):
        return Expression(self._name, 'ilike', other)

    # Extend the Field class to support more operators available
    def in_(self, other):
        return Expression(self._name, 'in_', other)

    def notin_(self, other):
        return Expression(self._name, 'notin_', other)

    def startswith(self, other):
        return Expression(self._name, 'startswith', other)

    def endswith(self, other):
        return Expression(self._name, 'endswith', other)


class Expression:
    def __init__(self, name: str, op: str, val: Any):
        self.name = name
        self.op = op
        self.val = val


# Helper class to create Field instances dynamically
class ResourceTypeFields:
    def __getattr__(self, name):
        return Field(name)


R = ResourceTypeFields()  # Instance to access fields


class Filter(Modifier):
    """
    Implements query filtering for Session.get etc.
    You can derive your own filter class and use it if you have a
    custom filter query syntax.
    """

    def __init__(self, *args, query_str: str = '', resource_type: str = None, **filter_kwargs: 'FilterKeywords') -> None:
        """
        :param query_str: Specify query string manually.
        :param filter_kwargs: Specify required conditions on result.
            Example: Filter(attribute='1', relation__attribute='2')
        :param resource_type: Specify the resource type context for filter relationships.
        """
        super().__init__(query_str)
        self._filter_kwargs = filter_kwargs
        self._filter_expressions = args
        self.resource_type = resource_type

    # This and next method prevent any existing subclasses from breaking
    def url_with_modifiers(self, base_url: str) -> str:
        return self.filtered_url(base_url)

    def filtered_url(self, base_url: str) -> str:
        return super().url_with_modifiers(base_url)

    def appended_query(self) -> str:
        if self._query_str:
            return super().appended_query()
        else:
            return self.format_filter_query(*self._filter_expressions, **self._filter_kwargs)

    def format_filter_query(self, *args, **kwargs) -> str:
        """
        Formats the filter query according to Flask-REST-JSONAPI specifications.
        Supports both keyword arguments and Expression objects.
        """
        filters = []

        # Process keyword arguments (existing functionality)
        for key, value in kwargs.items():
            parts = key.split('__')
            filter_dict = {}

            if len(parts) == 2:
                filter_dict = self._build_filter_for_relationship(parts, value)
            elif len(parts) > 2:
                raise Exception("More complex criteria cannot be handled")
            else:
                # Simple criteria (e.g., name='John')
                filter_dict = {"name": parts[0], "op": "eq", "val": value}

            filters.append(filter_dict)

        # Process Expression objects (new functionality)
        for expr in args:
            if isinstance(expr, Expression):
                parts = expr.name.split('__')
                filter_dict = Filter.build_nested_filter(parts, expr.op, expr.val, self.resource_type)
                filters.append(filter_dict)
            else:
                raise Exception("Invalid filter expression")

        # Convert the filters list to a JSON string
        filter_query = json.dumps(filters)
        return f'filter={filter_query}'

    def _build_filter_for_relationship(self, parts, value):
        """
        Uses the schema_registry to determine if a field represents a to-one or to-many relationship.
        """
        if not self.resource_type:
            raise ValueError("resource_type must be specified for relationship filters")

        # Check the relationship type using schema_registry
        relation_type = schema_registry.get_relationship_type(self.resource_type, parts[0])

        if relation_type == 'to-many':
            op = 'any'
        elif relation_type == 'to-one':
            op = 'has'
        else:
            raise Exception(f"Cannot determine relationship type for {parts[0]}")

        return {"name": parts[0], "op": op, "val": {"name": parts[1], "op": "eq", "val": value}}

    @staticmethod
    def build_nested_filter(parts, op, val, resource_type=None):
        """
        Recursively builds the filter dictionary for nested fields, considering the resource_type if provided.
        """
        if len(parts) == 1:
            return {"name": parts[0], "op": op, "val": val}
        else:
            first_part = parts[0]
            remaining_parts = parts[1:]

            if resource_type:
                relation_type = schema_registry.get_relationship_type(resource_type, first_part)
                if relation_type == 'to-many':
                    rel_op = 'any'
                else:
                    rel_op = 'has'
            else:
                # Default logic if resource_type is not specified
                rel_op = 'any' if first_part.endswith('s') else 'has'

            return {
                "name": first_part,
                "op": rel_op,
                "val": Filter.build_nested_filter(remaining_parts, op, val, resource_type)
            }


class Inclusion(Modifier):
    """
    Implements query inclusion for Session.get etc.
    """

    def __init__(self, *include_args: 'IncludeKeywords') -> None:
        super().__init__()
        self._include_args = include_args

    def appended_query(self) -> str:
        includes = ','.join(self._include_args)
        return f'include={includes}'
