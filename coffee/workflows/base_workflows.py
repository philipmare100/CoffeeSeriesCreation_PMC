from coffee.client import JsonApiClient


class BaseWorkflow:
    def __init__(self, client: JsonApiClient, upload_multithreaded: bool = False):
        """
        :param client: An instance of JsonApiClient used to perform API operations.
        """
        if client.enable_async and upload_multithreaded:
            raise ValueError("Multithreaded uploads not allowed with async client."
                             "Disable `client.enable_async` or `upload_multithreaded.")

        self.client = client
        self.upload_multithreaded = upload_multithreaded
