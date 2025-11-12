"""AAS HTTP Client Package."""

import importlib.metadata
from datetime import datetime, timezone

__copyright__ = f"Copyright (C) {datetime.now(tz=timezone.utc).year} :em engineering methods AG. All rights reserved."
__author__ = "Daniel Klein"

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"

__project__ = "aas-http-client"
__package__ = "aas-http-client"

from aas_http_client.classes.client.aas_client import AasHttpClient, create_client_by_config, create_client_by_dict, create_client_by_url
from aas_http_client.classes.wrapper.sdk_wrapper import SdkWrapper, create_wrapper_by_config, create_wrapper_by_dict, create_wrapper_by_url
from aas_http_client.core.version_check import check_for_update
from aas_http_client.utilities import model_builder, sdk_tools

check_for_update()

__all__ = [
    "AasHttpClient",
    "SdkWrapper",
    "create_client_by_config",
    "create_client_by_dict",
    "create_client_by_url",
    "create_wrapper_by_config",
    "create_wrapper_by_dict",
    "create_wrapper_by_url",
    "model_builder",
    "sdk_tools",
]
