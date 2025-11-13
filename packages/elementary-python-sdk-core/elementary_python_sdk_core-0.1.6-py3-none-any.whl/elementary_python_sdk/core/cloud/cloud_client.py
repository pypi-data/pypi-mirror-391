import requests
from elementary_python_sdk.core.cloud.request import ElementaryCloudIngestRequest
from elementary_python_sdk.core.test_context import TestContext


class ElementaryCloudClient:
    def __init__(self, project_id: str, api_key: str, url: str):
        self.project_id = project_id
        self.api_key = api_key
        self.url = url

    def send_to_cloud(self, test_context: TestContext):
        objects = test_context.get_elementary_objects()
        request = ElementaryCloudIngestRequest(
            project=self.project_id,
            objects=objects,
        )
        response = requests.post(
            f"{self.url}",
            json=request.model_dump(),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        return response.json()
