from amzsc.handlers import safe_method
from amzsc.modules.proxy.proxy_request import ProxyRequest


@safe_method
def get_proxy(api_key: str) -> str | None:
    """
    Get a new proxy from the ProxyRequest module.
    If no new proxy is available, it returns the current proxy.
    """
    proxy_cli = ProxyRequest(api_key=api_key)
    proxy = proxy_cli.get_new_proxy() or proxy_cli.get_current_proxy()
    if not proxy or not ProxyRequest.is_proxy_live(proxy):
        raise ValueError("No valid proxy available.")
    return proxy
