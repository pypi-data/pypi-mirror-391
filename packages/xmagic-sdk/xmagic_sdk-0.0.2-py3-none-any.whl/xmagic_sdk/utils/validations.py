import requests
from xmagic_sdk.config import Config


def is_config_valid(api_key: str):
    try:
        response = requests.get(
            url=f"{Config.XMAGIC_BASE_PATH}/v1/personas", headers={"x-api-key": api_key}
        )

        response.raise_for_status()
        return True
    except:
        return False
