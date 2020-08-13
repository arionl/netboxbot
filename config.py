#!/usr/bin/env python3

import os


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    URL_PATH = os.environ.get("URLPath", "netboxbot")
    APP_ID = os.environ.get("APP_ID", None)
    APP_PASSWORD = os.environ.get("APP_PASSWORD", None)
    NETBOX_HOST = os.environ.get("NETBOX_HOST", None)
    NETBOX_APIKEY = os.environ.get("NETBOX_APIKEY", None)
