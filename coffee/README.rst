================================
Coffee - The WIRE SDK for Python
================================

|Version| |Python| |License|

Coffee is the WIRE Software Development Kit (SDK) for
Python that simplifies working with the WIRE API. Leveraging 
the embedded `jsonapi-client` library, it allows developers to seamlessly
use the WIRE API for standard and custom workflow automation.
You can find the latest, most up to date, documentation at the ClickUp `doc site`_,
including a list of features, endpoints, handlers and workflows that are supported.

"The SDK derives its name from the beverage beloved by MMS people, coffee.
The original author of the Coffee library chose this name to symbolise the
anticipated boost in productivity and workflow efficiency it offers.

.. _`doc site`: https://app.clickup.com/7272257/v/dc/6xxu1-12962
.. _`jsonapi-client`: https://github.com/qvantel/jsonapi-client
.. |Python| image:: https://img.shields.io/pypi/pyversions/coffee.svg?style=flat
    :target: https://pypi.python.org/pypi/coffee/
    :alt: Python Versions
.. |Version| image:: http://img.shields.io/pypi/v/coffee.svg?style=flat
    :target: https://pypi.python.org/pypi/coffee/
    :alt: Package Version
.. |License| image:: http://img.shields.io/pypi/l/coffee.svg?style=flat
    :target: https://github.com/coffee/coffee/blob/develop/LICENSE
    :alt: License

Architecture
------------
.. image:: /coffee-sdk-architecture-abbridged.svg
   :alt: SDK Architecture
   :width: 1000px
   :align: center

Project Structure
-----------------
- **coffee/jsonapi_client/**: Embedded version of the `jsonapi-client`_ library.
- **coffee/client.py**: Entry point for interacting with the WIRE API. The client has a JsonApiClient class, built on the `jsonapi-client`_ library, and manages the authentication and base/generic CRUD operations to interact with the WIRE JSON:API endpoints in a simpler way.
- **coffee/request_handlers/**: Handlers to perform custom/specialised CRUD operations on for different JSON:API endpoints.
- **coffee/workflows/**: High-level modules that implement complex workflows by orchestrating calls across multiple resource handlers e.g. Bulk Series Creation Workflow (with calculations creation, process linking, estimate creation and linking)
- **coffee/utils/**: For utility functions and helpers that can be used across the Coffee SDK e.g. `sort_constant_properties_topological`
- **coffee/schemas/**: Defines data schemas that correspond to the WIRE JSON:API resources.
- **coffee/exceptions/**: For clearer and more precise error handling.
- **tests/**: For unit and integration tests.
- **docs/**, **examples/**, **README.rst**, **LICENSE**, **requirements.txt**, **setup.py**, **config.py**: Standard project files.

**NB**: Why do we have both a `coffee/client.py` and `coffee/request_handlers/base_resource_handler.py`? The
`coffee/request_handlers/base_resource_handler.py` abstracts out the `resource_type` from the `jsonapi_client/session.py`.
This way, a user is less prone to mistakes typing out resource type names. The IDE will
code-complete resource_handler names. In addition, the `coffee/base_resource_handler.py` abstracts
out the shared CRUD methods from each `coffee/{custom}_handler.py`.

.. code-block:: none
    +---coffee
    |   |   coffee-sdk-architecture.png
    |   |   README.rst
    |   |   requirements.txt
    |   |   setup.py
    |   |
    |   +---coffee
    |   |   |   client.py
    |   |   |   config.py
    |   |   |   __init__.py
    |   |   |
    |   |   +---exceptions
    |   |   |   |   client_exceptions.py
    |   |   |   |   database_exceptions.py
    |   |   |   |   helper_exceptions.py
    |   |   |   |   __init__.py
    |   |   |
    |   |   +---jsonapi_client
    |   |   |   |   common.py
    |   |   |   |   document.py
    |   |   |   |   exceptions.py
    |   |   |   |   filter.py
    |   |   |   |   objects.py
    |   |   |   |   relationships.py
    |   |   |   |   resourceobject.py
    |   |   |   |   session.py
    |   |   |   |   __init__.py
    |   |   |
    |   |   +---resource_handlers
    |   |   |   |   base_resource_handler.py
    |   |   |   |   component_constant_collation_series_export_handler.py
    |   |   |   |   component_type_handler.py
    |   |   |   |   constant_property_component_type_handler.py
    |   |   |   |   constant_property_handler.py
    |   |   |   |   series_handler.py
    |   |   |   |   __init__.py
    |   |   |
    |   |   +---schemas
    |   |   |   |   component_constant_collation_series_export_schema.py
    |   |   |   |   component_type_schema.py
    |   |   |   |   constant_property_component_type_schema.py
    |   |   |   |   constant_property_schema.py
    |   |   |   |   series_schema.py
    |   |   |   |   __init__.py
    |   |   |
    |   |   +---utils
    |   |   |   |   calc_helpers.py
    |   |   |   |   helpers.py
    |   |   |   |   __init__.py
    |   |   |
    |   |   +---workflows
    |   |   |   |   base_workflows.py
    |   |   |   |   collation_workflows.py
    |   |   |   |   constant_property_workflows.py
    |   |   |   |   mapper_workflows.py
    |   |   |   |   series_workflows.py
    |   |   |   |   __init__.py
    |   |
    |   +---docs
    |   |       index.md
    |   |
    |   +---examples
    |   |       coffee-sdk-examples-01.ipynb
    |   |       coffee-sdk-examples-02.ipynb
    |   |       coffee-sdk-examples-03.ipynb
    |   |
    |   +---tests
    |   |   |   test_client.py
    |   |   |   test_collation_service.py
    |   |   |   test_constant_property_calculation_topological_sort.py
    |   |   |   test_create_constant_property_workflow.py
    |   |   |   test_delete_collation_series_export.py
    |   |   |   test_native_relationships.py
    |   |   |   test_simple_usage.py
    |   |   |   __init__.py
    |   |   |
    |   |   +---data
    |   |   |       test_constant_properties_data.csv
    |   |   |       __init__.py


Getting Started
---------------
Assuming that you have a supported version of Python installed, you can first
set up your environment as follows (tested for Ubuntu, adapt accordingly for other operating systems):

.. code-block:: sh

    $ python3 -m venv .venv
    ...
    $ . .venv/bin/activate

Then, you can install coffee from MMSWIRE's Github with:

.. code-block:: sh

    $ python3 -m pip install "git+git@github.com:mmswire/autoflows.git@main"

or install from source with:

.. code-block:: sh

    $ git clone git@github.com:mmswire/autoflows.git
    $ cd coffee
    $ python3 -m pip install -r requirements.txt
    $ python3 -m pip install -e .


Using Coffee
~~~~~~~~~~~~~~
After installing coffee

Next, set up credentials and other environment variable in ``.env``:

.. code-block:: ini

    [default]
    API_TOKEN='my client instance wire token'
    API_ACCOUNT_ID='my default wire account id'
    BASE_URL='https://<client>.mmswire.com'
    API_BASE_URL='https://<client>.mmswire.com/api'
    LOG_LEVEL=DEBUG # default is INFO


To use the Coffee SDK:

1. Import the SDK and initialize your client:

.. code-block:: python

    >>> from coffee.client import JsonApiClient
    >>> client = JsonApiClient(enable_async=True)

2. Use the client to interact with the Coffee API asynchronously:

.. code-block:: python

    >>> import asyncio
    >>> from coffee.resource_handlers import SeriesHandler
    >>> async def get_series():
            series = await SeriesHandler(client).get_by_name('TEST_WIRE_SERIES_PER').resource
            print(series.description)
    >>> asyncio.run(get_series())


Usage Tips
~~~~~~~~~~~~~~
- When working with relationships, one must ensure that the target resource schema has been defined otherwise

Running Tests
~~~~~~~~~~~~~
You can run tests using ``pytest``. By default, it will run all of the unit and functional tests:

.. code-block:: sh

    $ pytest

You can also run individual tests by specifying your own ``pytest`` commands directly:

.. code-block:: sh

    $ pytest tests/helpers


Testing Strategy
~~~~~~~~~~~~~~~~
- `Unit Tests`: For each method in the resource handlers, using mocks for API responses. Focus on testing individual components or functions in isolation. This includes testing each method for handling API requests, processing responses, error handling, and utility functions. For the WIRE API interactions, you can mock API responses to test how your SDK handles various scenarios, including success, failure, and edge cases.
- `Integration Tests`: For testing the interaction between the client, resource handlers, and workflows, using actual API calls if possible or mocked responses. Test how different parts of your SDK work together, including the interaction between your SDK and the WIRE API. This is crucial for ensuring that the SDK correctly implements the API's authentication, request handling, and response processing. For these tests, you may use a combination of real API requests (if feasible) and mocked responses to cover a broader range of scenarios.
- `Workflow Tests`: Specific tests for the workflows to ensure the correct sequence of API calls and data manipulation. Since you're automating complex workflows, create tests that simulate end-to-end processes, such as creating a series, adding it to processes, creating calculations, etc. These tests should verify that the SDK correctly sequences API calls, handles dependencies between resources, and processes bulk operations without errors.
- `Performance Testing`: Even though there are no specific rate limits mentioned, it's essential to ensure that the SDK performs efficiently under load. Test how the SDK handles large batches of operations, multiple concurrent workflows, and intensive data manipulation, particularly with pandas data structures. This can help identify bottlenecks or areas for optimization.
- `Error Handling and Recovery Testing`: Specifically test the SDK's ability to handle API errors, network issues, and other exceptions gracefully. Verify that the SDK can retry operations when appropriate, log errors informatively, and fail cleanly without leaving processes in an inconsistent state.


Getting Help
------------

We use the ClickUp `Data Planning > Data Backlog <https://app.clickup.com/7272257/v/li/900500916243>`__
for tracking bugs and feature requests. Please use these following resources for getting help:

* Ask a question on the Data Team channel on Slack
* Open a support ticket with `Service Desk <servicedesk@metalmanagementsolutions.com>`__
* If it turns out that you may have found a bug, please `open a ClickUp issue <https://app.clickup.com/7272257/v/li/900500916243>`__

Contributing
------------

We value feedback and contributions from anyone. Whether it's a bug report, new feature,
correction, or additional documentation, we welcome your ClickUp issues and pull requests.
Document before submitting any ClickUp issues or pull requests to ensure we have all the necessary
information to effectively address to your contribution.


Maintenance and Support for SDK
-------------------------------

Coffee was made generally available on ##/##/2024 and is currently in the general availability phase of the
availability life cycle.

For information about maintenance and support for SDK major versions and their underlying dependencies, see
the following in the SDKs `doc site`_.

