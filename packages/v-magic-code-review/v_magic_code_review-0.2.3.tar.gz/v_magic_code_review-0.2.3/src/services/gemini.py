from gemini_webapi import GeminiClient
from gemini_webapi.constants import Model

from config import GeminiConfig
from util import call_async_func


class GeminiService:
    def __init__(self):
        self.gemini_client = GeminiClient(
            secure_1psid=GeminiConfig.cookie_secure_1psid,
            secure_1psidts=GeminiConfig.cookie_secure_1psidts,
        )
        call_async_func(self.gemini_client.init, timeout=600, auto_refresh=False, verbose=False)

    def chat(self, prompt: str, model: Model = Model.G_2_5_PRO) -> str:
        resp = call_async_func(
            self.gemini_client.generate_content,
            prompt=prompt,
            model=Model.G_2_5_FLASH,
        )
        return resp.text
