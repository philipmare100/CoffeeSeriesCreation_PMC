import logging
from typing import Any, Optional, Awaitable, Union, List

from coffee.client import JsonApiClient
from coffee.jsonapi_client.common import ResourceNameTuple, ResourceTuple
from coffee.jsonapi_client.document import Document
from coffee.jsonapi_client.exceptions import DocumentError
from coffee.jsonapi_client.filter import Filter
from coffee.jsonapi_client.objects import ResourceIdentifier
from coffee.jsonapi_client.resourceobject import ResourceObject
from coffee.exceptions.client_exceptions import ResourceNotFoundException


class BaseResourceHandler:
    resource_type: str = ""  # To be defined by subclasses

    def __init__(self, client: JsonApiClient):
        """
        Initializes the handler with a JsonApiClient.

        :param client: The client used to interact with the API.
        :type client: JsonApiClient
        """
        if not self.resource_type:
            raise NotImplementedError("Subclasses must define a resource_type.")
        self.client = client

    def filter(self, *args, **filter_kwargs) -> Document:
        """
        Synchronously filters resources based on filter criteria.

        :param args: Expression objects for filtering.
        :type args: Optional[Any]
        :param filter_kwargs: Keyword arguments for filtering.
        :type filter_kwargs: Optional[Dict]
        :return: The filtered resource document.
        :rtype: Document
        :raises RuntimeError: If the client is configured for async.
        """
        if self.client.enable_async:
            raise RuntimeError(
                "Client is configured for async. Use 'async_filter' instead."
            )

        filter_obj = Filter(*args,resource_type=self.resource_type, **filter_kwargs)
        return self.client.get(self.resource_type, filter_obj=filter_obj)

    async def async_filter(self, *args, **filter_kwargs) -> Document:
        """
        Asynchronously filters resources based on filter criteria.

        :param args: Expression objects for filtering.
        :type args: Optional[Any]
        :param filter_kwargs: Keyword arguments for filtering.
        :type filter_kwargs: Optional[Dict]
        :return: The filtered resource document.
        :rtype: Document
        :raises RuntimeError: If the client is configured for sync.
        """
        if not self.client.enable_async:
            raise RuntimeError("Client is configured for sync. Use 'filter' instead.")

        filter_obj = Filter(*args,resource_type=self.resource_type, **filter_kwargs)
        return await self.client.async_get(self.resource_type, filter_obj=filter_obj)

    # Create Methods
    def create(
        self,
        attributes: Optional[dict[str, Any]] = None,
        relationships: Optional[
            dict[str, Union[ResourceObject, ResourceIdentifier, ResourceTuple]]
        ] = None,
    ) -> ResourceObject:
        """
        Synchronously creates a new resource.

        :param attributes: The attributes of the new resource.
        :type attributes: Optional[dict[str, Any]]
        :param relationships: The relationships of the new resource.
        :type relationships: Optional[dict[str, ResourceTuple]]
        :return: The created resource.
        :rtype: ResourceObject
        :raises RuntimeError: If the client is configured for async.
        :raises DocumentError: If creation fails.
        """
        if self.client.enable_async:
            raise RuntimeError(
                f"Client is configured for async. Use 'async_create' instead."
            )
        try:
            return self.client.create(self.resource_type, attributes, relationships)
        except DocumentError as e:
            logging.error(f"Failed to create {self.resource_type}: {e}")
            raise

    async def async_create(
        self,
        attributes: dict[str, Any],
        relationships: Optional[dict[str, Any]] = None,
    ) -> ResourceObject:
        """
        Asynchronously creates a new resource.

        :param attributes: Attributes for the new resource.
        :type attributes: dict[str, Any]
        :param relationships: Relationships for the new resource.
        :type relationships: Optional[dict[str, Any]]
        :return: The created resource object.
        :rtype: ResourceObject
        :raises RuntimeError: If the client is configured for sync.
        :raises DocumentError: If creation fails.
        """
        if not self.client.enable_async:
            raise RuntimeError(
                f"Client is configured for sync. Use 'create' instead."
            )
        try:
            return await self.client.async_create(
                self.resource_type, attributes, relationships
            )
        except DocumentError as e:
            logging.error(f"Failed to create {self.resource_type}: {e}")
            raise

    # Read Methods
    def get(
        self,
        resource_id: Optional[str] = None,
        filter_obj: Optional[Any] = None,
    ) -> Document:
        """
        Synchronously fetches a resource by ID or filter.

        :param resource_id: The ID of a specific resource to fetch.
        :type resource_id: Optional[str]
        :param filter_obj: An object to filter the resources.
        :type filter_obj: Optional[Any]
        :return: The fetched resource document.
        :rtype: Document
        :raises RuntimeError: If the client is configured for async.
        """
        if self.client.enable_async:
            raise RuntimeError(
                "Client is configured for async. Use 'async_get' instead."
            )
        return self.client.get(self.resource_type, resource_id, filter_obj)

    async def async_get(
        self,
        resource_id: Optional[str] = None,
        filter_obj: Optional[Any] = None,
    ) -> Document:
        """
        Asynchronously fetches a resource by ID or filter.

        :param resource_id: The ID of a specific resource to fetch.
        :type resource_id: Optional[str]
        :param filter_obj: An object to filter the resources.
        :type filter_obj: Optional[Any]
        :return: The fetched resource document.
        :rtype: Document
        :raises RuntimeError: If the client is configured for sync.
        """
        if not self.client.enable_async:
            raise RuntimeError("Client is configured for sync. Use 'get' instead.")
        return await self.client.async_get(self.resource_type, resource_id, filter_obj)

    def get_by_name(self, resource_name: str) -> Document:
        """
        Synchronously fetches a resource by name.

        :param resource_name: The name of the resource to fetch.
        :type resource_name: str
        :return: The fetched resource document.
        :rtype: Document
        :raises RuntimeError: If the client is configured for async.
        """
        if self.client.enable_async:
            raise RuntimeError(
                "Client is configured for async. Use 'async_get_by_name' instead."
            )
        try:
            return self.client.get_by_name(self.resource_type, resource_name)
        except ResourceNotFoundException as e:
            logging.error(
                f"Failed to get {self.resource_type} by name '{resource_name}': {e}"
            )
            raise

    async def async_get_by_name(self, resource_name: str) -> Document:
        """
        Asynchronously fetches a resource by name.

        :param resource_name: The name of the resource to fetch.
        :type resource_name: str
        :return: The fetched resource document.
        :rtype: Document
        :raises RuntimeError: If the client is configured for sync.
        """
        if not self.client.enable_async:
            raise RuntimeError(
                "Client is configured for sync. Use 'get_by_name' instead."
            )
        try:
            return await self.client.async_get_by_name(
                self.resource_type, resource_name
            )
        except ResourceNotFoundException as e:
            logging.error(
                f"Failed to get {self.resource_type} by name '{resource_name}': {e}"
            )
            raise

    def get_by_linked_resource_names(
        self, linked_resources: List[ResourceNameTuple]
    ) -> Document:
        """
        Synchronously fetches resources linked to the provided ResourceNameTuples.

        :param linked_resources: A list of ResourceNameTuples defining related resources.
        :type linked_resources: List[ResourceNameTuple]
        :return: The fetched resource document.
        :rtype: Document
        :raises RuntimeError: If the client is configured for async.
        """
        if self.client.enable_async:
            raise RuntimeError(
                "Client is configured for async. Use 'async_get_by_linked_resource_names' instead."
            )
        try:
            return self.client.get_by_linked_resource(
                self.resource_type, linked_resources
            )
        except ResourceNotFoundException as e:
            logging.error(
                f"Failed to get {self.resource_type} linked to resources '{linked_resources}': {e}"
            )
            raise

    async def async_get_by_linked_resource_names(
        self, linked_resources: List[ResourceNameTuple]
    ) -> Document:
        """
        Asynchronously fetches resources linked to the provided ResourceNameTuples.

        :param linked_resources: A list of ResourceNameTuples defining related resources.
        :type linked_resources: List[ResourceNameTuple]
        :return: The fetched resource document.
        :rtype: Document
        :raises RuntimeError: If the client is configured for sync.
        """
        if not self.client.enable_async:
            raise RuntimeError(
                "Client is configured for sync. Use 'get_by_linked_resource_names' instead."
            )
        try:
            return await self.client.async_get_by_linked_resource(
                self.resource_type, linked_resources
            )
        except ResourceNotFoundException as e:
            logging.error(
                f"Failed to get {self.resource_type} linked to resources '{linked_resources}': {e}"
            )
            raise

    # Update Methods
    def patch(
        self,
        resource: ResourceObject,
        attributes: Optional[dict[str, Any]] = None,
        relationships: Optional[dict[str, ResourceTuple]] = None,
    ) -> ResourceObject:
        """
        Synchronously patches a resource.

        :param resource: The resource to patch.
        :type resource: ResourceObject
        :param attributes: The attributes to update.
        :type attributes: Optional[dict[str, Any]]
        :param relationships: The relationships to update.
        :type relationships: Optional[dict[str, ResourceTuple]]
        :return: The updated resource.
        :rtype: ResourceObject
        :raises RuntimeError: If the client is configured for async.
        :raises DocumentError: If the update fails.
        """
        if self.client.enable_async:
            raise RuntimeError(
                f"Client is configured for async. Use 'async_patch' instead."
            )
        try:
            return self.client.patch(resource, attributes, relationships)
        except DocumentError as e:
            logging.error(f"Failed to patch {self.resource_type}: {e}")
            raise

    async def async_patch(
        self,
        resource: ResourceObject,
        attributes: Optional[dict[str, Any]] = None,
        relationships: Optional[dict[str, ResourceTuple]] = None,
    ) -> ResourceObject:
        """
        Asynchronously patches a resource.

        :param resource: The resource to patch.
        :type resource: ResourceObject
        :param attributes: The attributes to update.
        :type attributes: Optional[dict[str, Any]]
        :param relationships: The relationships to update.
        :type relationships: Optional[dict[str, ResourceTuple]]
        :return: The updated resource.
        :rtype: ResourceObject
        :raises RuntimeError: If the client is configured for sync.
        :raises DocumentError: If the update fails.
        """
        if not self.client.enable_async:
            raise RuntimeError(
                f"Client is configured for sync. Use 'patch' instead."
            )
        try:
            return await self.client.async_patch(resource, attributes, relationships)
        except DocumentError as e:
            logging.error(f"Failed to patch {self.resource_type}: {e}")
            raise

    def update(self, resource: ResourceObject) -> None:
        """
        Synchronously updates a resource.

        :param resource: The resource to update.
        :type resource: ResourceObject
        :raises RuntimeError: If the client is configured for async.
        """
        if self.client.enable_async:
            raise RuntimeError(
                "Client is configured for async. Use 'async_update' instead."
            )
        self.client.update(resource)

    async def async_update(self, resource: ResourceObject) -> None:
        """
        Asynchronously updates a resource.

        :param resource: The resource to update.
        :type resource: ResourceObject
        :raises RuntimeError: If the client is configured for sync.
        """
        if not self.client.enable_async:
            raise RuntimeError("Client is configured for sync. Use 'update' instead.")
        await self.client.async_update(resource)

    # Delete Methods
    def delete(self, resource: ResourceObject) -> None:
        """
        Synchronously deletes a resource.

        :param resource: The resource to delete.
        :type resource: ResourceObject
        :raises RuntimeError: If the client is configured for async.
        """
        if self.client.enable_async:
            raise RuntimeError(
                "Client is configured for async. Use 'async_delete' instead."
            )
        self.client.delete(resource)

    async def async_delete(self, resource: ResourceObject) -> None:
        """
        Asynchronously deletes a resource.

        :param resource: The resource to delete.
        :type resource: ResourceObject
        :raises RuntimeError: If the client is configured for sync.
        """
        if not self.client.enable_async:
            raise RuntimeError("Client is configured for sync. Use 'delete' instead.")
        await self.client.async_delete(resource)
