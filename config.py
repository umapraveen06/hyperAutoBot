#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = "fc31348a-bee3-4f59-8614-3e974fb3e036"
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    LUIS_APP_ID = os.environ.get("LuisAppId", "")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "")

    #CLU credentials
    CLU_ENDPOINT = "https://hyperautolangresourceus.cognitiveservices.azure.com/"
    CLU_KEY = "c93a9d94086b438fb42026cd0f798f0d"
    CLU_PROJECT_NAME = "hyperautoCLU"
    CLU_DEPLOYMENT_NAME = "deployment8"
