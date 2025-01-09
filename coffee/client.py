import ssl
import asyncio
import logging
from typing import Optional, Any, Awaitable, Union, Dict, List

import pandas as pd
from aiohttp import BasicAuth
import requests
from requests.auth import HTTPBasicAuth

from coffee.dataapi.dataobject import DataObject, SeriesDataObject
from coffee.jsonapi_client.common import ResourceNameTuple, ResourceTuple
from coffee.jsonapi_client.document import Document
from coffee.jsonapi_client.exceptions import DocumentError
from coffee.jsonapi_client.filter import Filter, R
from coffee.jsonapi_client.objects import ResourceIdentifier
from coffee.jsonapi_client.resourceobject import ResourceObject
from coffee.jsonapi_client.session import Session
from coffee.config import settings, logger
from coffee.schemas import schema_registry
from coffee.utils.helpers import validate_linked_resource_types, exponential_backoff
from coffee.exceptions.client_exceptions import ResourceNotFoundException, NoDataReturnedException


class BaseClient:
    """
    Base client for shared configuration between JsonApiClient and DataClient.
    """

    def __init__(
            self,
            base_url: str = None,
            auth: Optional[tuple[str, str]] = None,
            verify_ssl: bool = True,
            disable_ssl_warnings: bool = False,
            account_id: str = None,
    ):
        self.base_url = base_url if base_url is not None else settings.API_BASE_URL
        self.verify_ssl = verify_ssl
        self.auth = self._set_auth_obj(auth if auth else self._get_auth_from_settings())
        self.account_id = account_id if account_id else self._get_account_id_from_settings()

        if disable_ssl_warnings:
            self._set_disable_ssl_warnings()

    @staticmethod
    def _get_auth_from_settings() -> Optional[tuple[str, str]]:
        """
        Fetch authentication details from settings.
        """
        if hasattr(settings, 'API_TOKEN'):
            return str(), settings.API_TOKEN
        return None

    def _set_auth_obj(self, auth: Optional[tuple[str, str]]) -> None:
        """
        Set the auth object for making requests.
        """
        self.auth = auth
        return auth

    @staticmethod
    def _get_account_id_from_settings() -> str:
        """
        Fetch account_id from settings.
        """
        return settings.API_ACCOUNT_ID if hasattr(settings, 'API_ACCOUNT_ID') else None

    @staticmethod
    def _set_disable_ssl_warnings(self) -> None:
        """
        Disable SSL warnings.
        """
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return None


class JsonApiClient:
    """
    A client for managing sessions and performing CRUD operations on a JSON API.

    :param base_url: The base URL of the WIRE JSON:API. If not provided, it defaults to the value of
     `settings.API_BASE_URL` from environment variables.
    :type base_url: str
    :param enable_async: Flag to enable asynchronous operations. If not provided, it defaults to False.
    :type enable_async: bool, optional
    :param schema: A schema defining the JSON structure expected from the API. If not provided, it defaults to
     `api_schema_all`.
    :type schema: dict[str, str], optional
    :param auth: A tuple of (username=wire_user, password=wire_token) for basic authentication. If not provided,
     authentication details are retrieved from environment settings.
    :type auth: Optional[tuple[str, str]], optional
    :param verify_ssl: Flag to enable SSL certificate verification. Defaults to True.
    :type verify_ssl: bool, optional
    :param account_id: An account identifier. If not provided, it is retrieved from environment settings.
    :type account_id: str, optional
    :ivar _auth_obj: Authentication object for the session, can be either `HTTPBasicAuth` or `BasicAuth`.
    :ivar session: The JSON API client session, can be either synchronous or asynchronous.
    """

    def __init__(
            self,
            base_url: str = None,
            enable_async: bool = None,
            schema: dict[str, str] = None,
            auth: Optional[tuple[str, str]] = None,
            verify_ssl: bool = True,
            disable_ssl_warnings: bool = False,
            account_id: str = None,
    ):
        """
        Initializes the JsonApiClient with settings prioritisation.

        :param base_url: The base URL of the WIRE JSON:API. If not provided, it defaults to the value of
         `settings.API_BASE_URL` from environment variables.
        :type base_url: str
        :param enable_async: Flag to enable asynchronous operations. If not provided, it defaults to False.
        :type enable_async: bool, optional
        :param schema: A schema defining the JSON structure expected from the API. If not provided, it defaults to
         `api_schema_all`.
        :type schema: dict[str, str], optional
        :param auth: A tuple of (username=wire_user, password=wire_token) for basic authentication. If not provided,
         authentication details are retrieved from environment settings.
        :type auth: Optional[tuple[str, str]], optional
        :param verify_ssl: Flag to enable SSL certificate verification. Defaults to True.
        :type verify_ssl: bool, optional
        :param account_id: An account identifier. If not provided, it is retrieved from environment settings.
        :type account_id: str, optional
        """
        # Prioritize __init__ parameters over settings from environment variables or CLI inputs
        self.base_url = base_url if base_url is not None else settings.API_BASE_URL
        self.enable_async = enable_async if enable_async is not None else False
        self.schema = schema if schema is not None else schema_registry.get_all_schemas()
        self.verify_ssl = verify_ssl

        self._set_auth_obj(auth if auth else self._get_auth_from_settings())
        self._set_account(account_id if account_id else self._get_wire_account_id_from_settings())

        # Build request_kwargs using the helper method
        self.request_kwargs = self._build_request_kwargs()

        self.session = Session(
            self.base_url,
            enable_async=self.enable_async,
            schema=self.schema,
            request_kwargs=self.request_kwargs
        )

        self._set_disable_ssl_warnings(
            disable_ssl_warnings if disable_ssl_warnings else self._get_disable_ssl_warnings_from_settings()
        )

    @staticmethod
    def _get_auth_from_settings() -> Optional[tuple[str, str]]:
        """
        Constructs auth tuple from settings if API_TOKEN is available.

        :return: Tuple `(username, password)`, where username can be empty string, password is api_token
        :rtype: tuple[str, str]
        """
        if hasattr(settings, 'API_TOKEN'):
            return str(), settings.API_TOKEN
        return None

    def _set_auth_obj(self, auth: Optional[tuple[str, str]] = None) -> None:
        """
        Sets the appropriate authentication object based on the operation mode (sync or async).
        """
        if auth:
            if not self.enable_async:
                self._auth_obj = HTTPBasicAuth(*auth)
            else:
                self._auth_obj = BasicAuth(*auth)
        else:
            self._auth_obj = None

    @staticmethod
    def _get_wire_account_id_from_settings() -> str | None:
        """
        Gets the WIRE account id from settings if API_ACCOUNT_ID is available.

        :return: account_id
        :rtype: str
        """
        if hasattr(settings, 'API_ACCOUNT_ID'):
            return str(settings.API_ACCOUNT_ID)
        return None

    def _set_account(self, account_id: str) -> None:
        """
        Sets the appropriate account resource tuple based on the account id.
        """
        if account_id:
            self._account = ResourceTuple(id=account_id, type='account')
        else:
            self._account = None

    @staticmethod
    def _get_disable_ssl_warnings_from_settings() -> bool:
        """
        Gets the disable SSL warnings from settings if DISABLE_SSL_WARNINGS is available.
        :return: boolean
        :rtype: bool
        """
        if hasattr(settings, 'DISABLE_SSL_WARNINGS'):
            return bool(settings.DISABLE_SSL_WARNINGS)
        return False

    def _set_disable_ssl_warnings(self, disable_ssl_warnings: bool) -> None:
        """
        Sets the disable-SSL-warning flag based on the client instantiation.
        """
        if disable_ssl_warnings:
            self._disable_ssl_warnings = disable_ssl_warnings
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _build_request_kwargs(self):
        """
        Helper method to build request keyword arguments based on the session type.
        """
        #TODO Add other kwargs
        request_kwargs = {'auth': self._auth_obj}

        if self.enable_async:
            # For aiohttp, use 'ssl' parameter
            if self.verify_ssl is False:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                request_kwargs['ssl'] = ssl_context
            elif isinstance(self.verify_ssl, str):
                # If verify_ssl is a path to a CA bundle
                ssl_context = ssl.create_default_context(cafile=self.verify_ssl)
                request_kwargs['ssl'] = ssl_context
            else:
                # SSL verification is enabled by default; no need to set 'ssl' parameter
                pass
        else:
            # For requests library, use 'verify' parameter
            request_kwargs['verify'] = self.verify_ssl

        return request_kwargs

    def __enter__(self) -> 'JsonApiClient':
        """
        Context manager entry for synchronous operations.
        """
        if not self.enable_async:
            # Use the helper method to build request_kwargs
            self.request_kwargs = self._build_request_kwargs()
            self.session = Session(
                self.base_url,
                enable_async=False,
                schema=self.schema,
                request_kwargs=self.request_kwargs
            )
            return self
        else:
            raise RuntimeError("Synchronous context manager not supported for async sessions")

    async def __aenter__(self) -> 'JsonApiClient':
        """
        Context manager entry for asynchronous operations.
        """
        if self.enable_async:
            # Use the helper method to build request_kwargs
            self.request_kwargs = self._build_request_kwargs()
            self.session = Session(
                self.base_url,
                enable_async=True,
                schema=self.schema,
                request_kwargs=self.request_kwargs
            )
            return self
        else:
            raise RuntimeError("Asynchronous context manager not supported for sync sessions")

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Context manager exit for synchronous operations.
        """
        if not self.enable_async:
            self.session.close()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Context manager exit for asynchronous operations.
        """
        # Close the session and await if necessary
        close_result = self.session.close()
        if asyncio.iscoroutine(close_result):
            await close_result

    def close(self):
        """
        Close client session and invalidate resources.
        """
        self.session.close()


    def get(self, resource_type: str,
            resource_id: Optional[str] = None,
            filter_obj: Optional[Any] = None) -> Awaitable[Document] | Document:
        """
        Synchronously fetches resources of a given type, optionally filtered by an ID or other criteria.

        :param resource_type: The type of resource to fetch.
        :type resource_type: str
        :param resource_id: The ID of a specific resource to fetch, defaults to None.
        :type resource_id: Optional[str], optional
        :param filter_obj: An object to filter the resources, defaults to None.
        :type filter_obj: Optional[Any], optional
        :return: The fetched resources.
        :rtype: Awaitable[jsonapi_client.document.Document] | jsonapi_client.document.Document
        :raises RuntimeError: If called in asynchronous mode.
        """
        if self.enable_async:
            raise RuntimeError("Use 'async_get' for async sessions")
        else:
            return self.session.get(resource_type, resource_id_or_filter=resource_id or filter_obj)

    async def async_get(self, resource_type: str,
                        resource_id: Optional[str] = None,
                        filter_obj: Optional[Any] = None) -> Awaitable[Document] | Document:
        """
        Asynchronously fetches resources of a given type, optionally filtered by an ID or other criteria.

        :param resource_type: The type of resource to fetch.
        :type resource_type: str
        :param resource_id: The ID of a specific resource to fetch, defaults to None.
        :type resource_id: Optional[str], optional
        :param filter_obj: An object to filter the resources, defaults to None.
        :type filter_obj: Optional[Any], optional
        :return: The fetched resources.
        :rtype: Awaitable[jsonapi_client.document.Document] | jsonapi_client.document.Document
        :raises RuntimeError: If called in synchronous mode.
        """
        if not self.enable_async:
            raise RuntimeError("Session is not initialized for async operations")
        return await self.session.get(resource_type, resource_id_or_filter=resource_id or filter_obj)

    def get_by_name(self, resource_type: str, resource_name: str) -> Document:
        """
        Synchronously fetches resource of a given type and name.

        :param resource_type: The type of resource to fetch.
        :type resource_type: str
        :param resource_name: The name of a specific resource to fetch, defaults to None.
        :type resource_name: Optional[str], optional
        :return: The fetched resource document.
        :rtype: jsonapi_client.document.Document
        :raises ResourceNotFoundException: If GET request does not find resource of given type and name.
        """
        resource_filter = Filter(R.name == resource_name)
        try:
            resource_document = self.get(resource_type=resource_type, filter_obj=resource_filter)
            resource = resource_document.resource
            logger.info(f"Found `{resource.type}` with name `{resource.name}`.")
            return resource_document
        except (DocumentError, IndexError) as e:
            msg = f"Could not find `{resource_type}` with name `{resource_name}`. Error: {e}"
            logger.error(msg)
            raise ResourceNotFoundException(msg)  # ToDo: ErrorHandling: Does this cover all things that could go wrong?

    async def async_get_by_name(self, resource_type: str, resource_name: str) -> Document:
        """
        Asynchronously fetches a resource of a given type and name.

        :param resource_type: The type of resource to fetch.
        :type resource_type: str
        :param resource_name: The name of the specific resource to fetch.
        :type resource_name: str
        :return: The fetched resource document.
        :rtype: jsonapi_client.document.Document
        :raises ResourceNotFoundException: If the resource is not found.
        """
        try:
            resource_document = await self.async_get(
                resource_type=resource_type,
                filter_obj=Filter(R.name == resource_name)
            )
            resource = resource_document.resource
            logger.info(f"Found `{resource.type}` with name `{resource.name}`.")
            return resource_document
        except (DocumentError, IndexError) as e:
            msg = f"Could not find `{resource_type}` with name `{resource_name}`. Error: {e}"
            logger.error(msg)
            raise ResourceNotFoundException(msg)

    def get_by_linked_resource(self, resource_type: str, linked_resources: list[ResourceNameTuple]) -> Document:
        """
        Synchronously fetches resources that are linked based on the provided list of ResourceNameTuples.
         ResourceNameTuples(name, type)

        :param resource_type: Resource type to be queried and returned
        :type resource_type: str
        :param linked_resources: A list of ResourceNameTuple defining the related (linked) resources.
        :type linked_resources: List[ResourceNameTuple]
        :return: Fetched resource document that is linked to the provided list of relationship resources.
        :rtype: List[jsonapi_client.document.Document]
        :raises ResourceNotFoundException: If the resource can't be found or if they are not linked as expected.
        """
        # Check that the linked resources are included in the valid types in the keys of the relationship model map
        # TODO This should use the schema
        validate_linked_resource_types(linked_resources)

        # Construct the filter kwargs dict based on the list of resources
        filter_kwargs = {}
        for resource_tuple in linked_resources:
            # Use property if available, otherwise default to type
            key = resource_tuple.property if resource_tuple.property else resource_tuple.type
            filter_kwargs.update({f'{key}__name': resource_tuple.name})

        try:
            resource_document = self.get(
                resource_type=resource_type,
                filter_obj=Filter(**filter_kwargs)
            )
            resource = resource_document.resource
            try:
                logger.info(f"Found `{resource.type}` with name `{resource.name}`.")
            except AttributeError:
                logger.info(f"Found `{resource.type}` with id `{resource.id}`.")
            # ToDo: Implement the logic here to verify if the fetched resources are indeed linked based on the criteria.
            #  This might involve checking relationships within the fetched resource document or any other logic
            #  applicable. For now, we'll assume all fetched resources are linked (may not always be the case.)
            return resource_document
        except (DocumentError, IndexError) as e:
            linked_resources_str = ', '.join([str(resource_tuple) for resource_tuple in linked_resources])
            msg = f"Could not find `{resource_type}` linked to `[{linked_resources_str}]`. Error: {e}"
            logger.error(msg)
            raise ResourceNotFoundException(msg)  # ToDo: ErrorHandling: Does this cover all things that could go wrong?

    async def async_get_by_linked_resource(self, resource_type: str,
                                           linked_resources: list[ResourceNameTuple]) -> Document:
        """
        Asynchronously fetches resources that are linked based on the provided list of ResourceNameTuples.

        :param resource_type: The type of resource to fetch.
        :type resource_type: str
        :param linked_resources: A list of ResourceNameTuple defining the related (linked) resources.
        :type linked_resources: List[ResourceNameTuple]
        :return: The fetched resource document.
        :rtype: jsonapi_client.document.Document
        :raises ResourceNotFoundException: If the resource can't be found or if they are not linked as expected.
        """
        # Validate linked resource types
        validate_linked_resource_types(linked_resources)

        # Construct filter kwargs based on linked resources
        filter_kwargs = {}
        for resource_tuple in linked_resources:
            key = resource_tuple.property if hasattr(resource_tuple,
                                                     'property') and resource_tuple.property else resource_tuple.type
            filter_kwargs[f'{key}__name'] = resource_tuple.name

        try:
            resource_document = await self.async_get(
                resource_type=resource_type,
                filter_obj=Filter(**filter_kwargs)
            )
            resource = resource_document.resource
            try:
                logger.info(f"Found `{resource.type}` with name `{resource.name}`.")
            except AttributeError:
                logger.info(f"Found `{resource.type}` with id `{resource.id}`.")
            # TODO: Implement logic to verify if the fetched resources are indeed linked as expected.
            return resource_document
        except (DocumentError, IndexError) as e:
            linked_resources_str = ', '.join([str(resource_tuple) for resource_tuple in linked_resources])
            msg = f"Could not find `{resource_type}` linked to `[{linked_resources_str}]`. Error: {e}"
            logger.error(msg)
            raise ResourceNotFoundException(msg)

    def create(self, resource_type: str, attributes: dict[str, str | bool] | None = None,
               relationships: dict[str, 'Union[ResourceObject, ResourceIdentifier, ResourceTuple]'] | None = None
               ) -> 'ResourceObject':
        """
        Synchronously creates a new resource of a given type with specified attributes and relationships.

        :param resource_type: The type of resource to create.
        :type resource_type: str
        :param attributes: The attributes of the new resource.
        :type attributes: dict[str, str | bool], optional
        :param relationships: The relationships of the new resource.
        :type relationships: dict[str, ResourceTuple], optional
        :return: The created resource.
        :rtype: jsonapi_client.resourceobject.ResourceObject
        :raises RuntimeError: If called in asynchronous mode.
        :raises ValueError: If both attributes and relationships are None.
        """
        if self.enable_async:
            raise RuntimeError("Use 'async_create' for async sessions")

        if attributes is None and relationships is None:
            raise ValueError("Either attributes or relationships must be provided.")

        if relationships is None:
            relationships = {}
        relationships.setdefault('account', self._account)

        fields = {}
        if attributes:
            fields.update(attributes)
        if relationships:
            fields.update(relationships)

        resource = self.session.create(resource_type, fields)
        # resource.commit()
        return resource

    async def async_create(self, resource_type: str, attributes: dict[str, Any],
                           relationships: Optional[dict[str, Any]] = None) -> ResourceObject:
        """
        Asynchronously creates a new resource of a given type with specified attributes and relationships.

        :param resource_type: The type of resource to create.
        :type resource_type: str
        :param attributes: The attributes of the new resource.
        :type attributes: Dict[str, Any]
        :param relationships: The relationships of the new resource.
        :type relationships: Optional[Dict[str, Any]], optional
        :return: The created resource.
        :rtype: jsonapi_client.resourceobject.ResourceObject
        :raises RuntimeError: If called in synchronous mode.
        """
        if not self.enable_async:
            raise RuntimeError("Session is not initialized for async operations")
        resource = self.session.create(resource_type)
        for key, value in attributes.items():
            setattr(resource, key, value)
        if relationships:
            for rel_name, rel_data in relationships.items():  # ToDO: BAD IMPLEMENTATION? CHECK SESSION.
                setattr(resource, rel_name, rel_data)
        await resource.commit()
        return resource

    def patch(self, resource: ResourceObject, attributes: dict[str, Any],
              relationships: Optional[dict[str, ResourceTuple]] = None) -> ResourceObject:
        """
        Synchronously patched a resource with specified attributes and relationships.

        :param resource: Resource object to patch
        :type resource: ResourceObject
        :param attributes: The attributes of the new resource.
        :type attributes: dict[str, Any], optional
        :param relationships: The relationships of the new resource.
        :type relationships: dict[str, ResourceTuple], optional
        :return: The created resource.
        :rtype: jsonapi_client.resourceobject.ResourceObject
        :raises RuntimeError: If called in asynchronous mode.
        """
        if self.enable_async:
            raise RuntimeError("Use 'async_patch' for async sessions")
        else:
            if attributes:
                for attr, value in attributes.items():
                    setattr(resource, attr, value)
            if relationships:  # TODO: Confirm that this works for relationships
                for rel_name, rel_data in relationships.items():
                    setattr(resource, rel_name, rel_data)
            logger.info(f'===== PATCHING {resource} =====')
            resource.commit()
            if logger.getEffectiveLevel() == logging.DEBUG:
                logger.debug(f'Commit response for dirty resource {str(resource)}: resource.commit()')
            return resource

    async def async_patch(self, resource: ResourceObject, attributes: dict[str, Any],
                          relationships: Optional[dict[str, ResourceTuple]] = None) -> ResourceObject:
        if not self.enable_async:
            raise RuntimeError("Session is not initialized for async operations")
        if attributes:
            for attr, value in attributes.items():
                setattr(resource, attr, value)
        if relationships:
            for rel_name, rel_data in relationships.items():
                setattr(resource, rel_name, rel_data)
        logger.info(f'===== ASYNC PATCHING {resource} =====')
        await resource.commit()
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug(f'Commit response for dirty resource {str(resource)}: await resource.commit()')
        return resource

    def update(self, resource) -> None:
        """
        Synchronously updates a given resource by committing its current state.

        :param resource: The resource to update.
        :type resource: Any
        :raises RuntimeError: If called in asynchronous mode.
        """
        if self.enable_async:
            raise RuntimeError("Use 'async_update' for async sessions")
        else:
            resource.commit()

    async def async_update(self, resource: Any) -> None:
        """
        Asynchronously updates a given resource by committing its current state.

        :param resource: The resource to update.
        :type resource: Any
        :raises RuntimeError: If called in synchronous mode.
        """
        if not self.enable_async:
            raise RuntimeError("Session is not initialized for async operations")
        await resource.commit()

    def delete(self, resource: Any) -> None:
        """
        Synchronously deletes a given resource.

        :param resource: The resource to delete.
        :type resource: Any
        :raises RuntimeError: If called in asynchronous mode.
        """
        if self.enable_async:
            raise RuntimeError("Use 'async_delete' for async sessions")
        else:
            resource.delete()
            resource.commit()

    async def async_delete(self, resource: Any) -> None:
        """
        Asynchronously deletes a given resource.

        :param resource: The resource to delete.
        :type resource: Any
        :raises RuntimeError: If called in synchronous mode.
        """
        if not self.enable_async:
            raise RuntimeError("Session is not initialized for async operations")
        resource.delete()
        await resource.commit()


class DataClient(BaseClient):
    """
    A client for managing data retrieval and storage from custom API endpoints.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> DataObject:
        """
        Perform a custom request to the data API.

        :param method: HTTP method ('GET', 'POST', etc.).
        :param endpoint: Custom endpoint to hit (e.g., 'GetData', 'GetSeriesSummary').
        :param params: Optional query parameters or filters.
        :return: DataObject representing the response data.
        :raises NoDataReturnedException: If no data is returned from the API.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        response = requests.request(method, url, params=params, headers=headers, verify=self.verify_ssl, auth=self.auth)
        if response.status_code != 200:
            response.raise_for_status()

        data = response.json().get('data')
        if not data:
            raise NoDataReturnedException(f"No data returned from endpoint {endpoint}")

        return DataObject(data)


    def get_data(
            self,
            start: Optional[str] = None,
            end: Optional[str] = None,
            sample_period: Optional[str] = None,
            shifts: Optional[bool] = None,
            estimate: Optional[List[str]] = None,
            series_list: Optional[List[str]] = None,
            process: Optional[str] = None,
            format: Optional[str] = "columns",
            all_data: Optional[bool] = False,
            process_name: Optional[str] = None,
            deepness: Optional[int] = 1,
            pivot: Optional[bool] = False,
            period_type: Optional[str] = "default",
            retries: int = 3
    ) -> SeriesDataObject:
        """
        Retrieve data from the 'GetData' endpoint, with support for custom filters and parameters.

        :return: A SeriesDataObject containing the retrieved data and query parameters as attributes.
        """
        # Prepare the request parameters according to the SeriesDataRequestSchema
        params = {
            "start": start,
            "end": end,
            "sample_period": sample_period,
            "shifts": shifts,
            "estimate": estimate,
            "series_list": series_list,
            "process": process,
            "format": format,
            "all": all_data,
            "process_name": process_name,
            "deepness": deepness,
            "pivot": pivot,
            "period_type": period_type,
        }

        # Remove None values from the request parameters
        params = {k: v for k, v in params.items() if v is not None}

        # Retry logic in case of failure
        for attempt in range(retries):
            try:
                url = f"{self.base_url}/GetData"
                headers = {'Content-Type': 'application/json'}
                response = requests.request("GET", url, params=params, headers=headers, verify=self.verify_ssl,
                                            auth=self.auth)
                if response.status_code != 200:
                    response.raise_for_status()

                response_json = response.json()
                data = response_json.get('data')
                if not data:
                    raise NoDataReturnedException(f"No data returned from endpoint GetData")

                # Extract other fields
                quality = response_json.get('quality', {})
                missing_values = response_json.get('missing_values', {})
                uncertainties = response_json.get('uncertainties', {})

                # Collect non-protected query params to set as attributes (exclude params starting with '_')
                query_params = {k: v for k, v in params.items() if not k.startswith('_')}

                # Create SeriesDataObject and set query parameters as attributes
                series_data_object = SeriesDataObject(
                    data=data,
                    quality=quality,
                    missing_values=missing_values,
                    uncertainties=uncertainties,
                    **query_params  # Unwrap query params as attributes
                )

                return series_data_object

            except (requests.HTTPError, requests.RequestException) as e:
                logger.error(f"Error retrieving data from GetData: {e}")
                if attempt < retries - 1:
                    exponential_backoff(attempt)
                else:
                    raise e

    # Implement more custom methods as required, following the same pattern.