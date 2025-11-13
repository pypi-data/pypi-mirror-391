class ElementaryCloudClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key

    def get_assets(self):
        return self.api_key
