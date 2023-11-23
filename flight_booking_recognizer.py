# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.ai.luis import LuisApplication, LuisRecognizer
from botbuilder.core import Recognizer, RecognizerResult, TurnContext
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

from config import DefaultConfig
import json

class FlightBookingRecognizer(Recognizer):
    def __init__(self, configuration: DefaultConfig):
        # self._recognizer = None

        # luis_is_configured = (
        #     configuration.LUIS_APP_ID
        #     and configuration.LUIS_API_KEY
        #     and configuration.LUIS_API_HOST_NAME
        # )
        # if luis_is_configured:
        #     # Set the recognizer options depending on which endpoint version you want to use e.g v2 or v3.
        #     # More details can be found in https://docs.microsoft.com/azure/cognitive-services/luis/luis-migration-api-v3
        #     luis_application = LuisApplication(
        #         configuration.LUIS_APP_ID,
        #         configuration.LUIS_API_KEY,
        #         "https://" + configuration.LUIS_API_HOST_NAME,
        #     )

        #     self._recognizer = LuisRecognizer(luis_application)
        self._client = None
        self._projectName = configuration.CLU_PROJECT_NAME
        self._deploymentName = configuration.CLU_DEPLOYMENT_NAME
        self._endPoint = configuration.CLU_ENDPOINT
        self._key = configuration.CLU_KEY
        self._client = ConversationAnalysisClient(configuration.CLU_ENDPOINT, AzureKeyCredential(configuration.CLU_KEY))
        # print("\n FlightBookingRecognizer init:",json.dumps(self))

    @property
    def is_configured(self) -> bool:
        # Returns true if luis is configured in the config.py and initialized.
        # return self._recognizer is not None
        return self._client is not None
        

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        result = None
        self._client = ConversationAnalysisClient(self._endPoint, AzureKeyCredential(self._key))
        # print("\n FlightBookingRecognizer recognize:",json.dumps(self))
        # return await self._recognizer.recognize(turn_context)
        with self._client:
            try:
                result = self._client.analyze_conversation(
                    task={
                        "kind": "Conversation",
                        "analysisInput": {
                            "conversationItem": {
                                "participantId": "1",
                                "id": "1",
                                # "modality": "text",
                                "language": "en",
                                "text": turn_context.activity.text
                            },
                            "isLoggingEnabled": False
                        },
                        "parameters": {
                            "projectName": self._projectName,
                            "deploymentName": self._deploymentName ,
                            "verbose": True
                        }
                    }
                )
            except Exception as exception:
                print("\n exception:",exception)
        return result
