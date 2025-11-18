from account_by_key_api.account_by_key_api_description import GetKeyReferencesResponse
from beekeepy._apis.abc.api import AbstractAsyncApi


class AccountByKeyApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def get_key_references(self, *, keys: list) -> GetKeyReferencesResponse:
        """Parameters:

        - `keys`: An array of strings representing keys to query. Example:
          - `["STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9"]` — queries for the key "STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9".
          - `["STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9", "STM4uSuD4da2uqp52J2pQ7Pth3hGa7j4ECyrHASnXmmH16NymEg6Q"]` — queries for the keys "STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9" and "STM4uSuD4da2uqp52J2pQ7Pth3hGa7j4ECyrHASnXmmH16NymEg6Q".
        """
