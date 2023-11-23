# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import InputHints

from booking_details import BookingDetails
from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper, Intent
from .booking_dialog import BookingDialog

import json

class MainDialog(ComponentDialog):
    def __init__(
        self, luis_recognizer: FlightBookingRecognizer, booking_dialog: BookingDialog
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self._luis_recognizer = luis_recognizer
        self._booking_dialog_id = booking_dialog.id

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(booking_dialog)
        self.add_dialog(
            # WaterfallDialog(
            #     "WFDialog", [self.intro_step, self.act_step, self.final_step]
            # )
            WaterfallDialog(
                "WFDialog", [self.intro_step, self.act_step]
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # print("\n step_context:",json.dumps(step_context))
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)
        message_text = (
            str(step_context.options)
            if step_context.options
            else "How can i help you?"
        )
        print("message_text:",message_text)
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            # LUIS is not configured, we just run the BookingDialog path with an empty BookingDetailsInstance.
            return await step_context.begin_dialog(
                self._booking_dialog_id, BookingDetails()
            )

        # Call LUIS and gather any potential booking details. (Note the TurnContext has the response to the prompt.)
        intent, entities = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )
        intent_text = "intent:"+intent
        # print(intent_text);
        intent_message = MessageFactory.text(
            intent_text, intent_text, InputHints.ignoring_input
        )
        await step_context.context.send_activity(intent_message)

        entities_text = "Entities"+json.dumps(entities)
        print(entities_text);
        entities_message = MessageFactory.text(
            entities_text, entities_text, InputHints.ignoring_input
        )
        await step_context.context.send_activity(entities_message)
        
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents import SearchClient
        # import json
        # service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
        # index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
        # key = os.environ["AZURE_SEARCH_API_KEY"]
        service_endpoint = "https://hyperautosearchservice.search.windows.net"
        index_name = "azuresql-index"
        key = "mBxsjXw5SX5U7ekDXFgdViZqwiIXpBBYlD0K3VpSyyAzSeCfMIyh"

        search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
        
        results = search_client.search(search_text=json.dumps(entities))
        count = 0
        suites = []
        for result in results:
            print(result)
            count = count+1
            suites.append(result["suite_description"])
            # await step_context.context.send_activity("suite:"+result["suite_description"])
            # print("{})".format(result))
        await step_context.context.send_activity("search count:"+str(count))
        await step_context.context.send_activity("suites:"+json.dumps(suites))

        # if intent == Intent.TABLE_NAME.value and luis_result:
        #     # Show a warning for Origin and Destination if we can't resolve them.
        #     await MainDialog._show_warning_for_unsupported_cities(
        #         step_context.context, luis_result
        #     )

        #     # Run the BookingDialog giving it whatever details we have from the LUIS call.
        #     return await step_context.begin_dialog(self._booking_dialog_id, luis_result)

        # if intent == Intent.TABLE_COUNT.value:
        #     get_weather_text = "TODO: get weather flow here"
        #     get_weather_message = MessageFactory.text(
        #         get_weather_text, get_weather_text, InputHints.ignoring_input
        #     )
        #     await step_context.context.send_activity(get_weather_message)

        # else:
        #     didnt_understand_text = (
        #         "Sorry, I didn't get that. Please try asking in a different way"
        #     )
        #     didnt_understand_message = MessageFactory.text(
        #         didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
        #     )
        #     await step_context.context.send_activity(didnt_understand_message)

        # return await step_context.next(None)
        # prompt_message = "Anything else can I do for you?"
        # await step_context.replace_dialog(self.id, prompt_message)
        return await step_context.begin_dialog(self.id)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # If the child dialog ("BookingDialog") was cancelled or the user failed to confirm,
        # the Result here will be null.
        if step_context.result is not None:
            result = step_context.result

            # Now we have all the booking details call the booking service.

            # If the call to the booking service was successful tell the user.
            # time_property = Timex(result.travel_date)
            # travel_date_msg = time_property.to_natural_language(datetime.now())
            msg_txt = f"I have you booked to {result.destination} from {result.origin} on {result.travel_date}"
            message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
            await step_context.context.send_activity(message)

        prompt_message = "What else can I do for you?"
        return await step_context.replace_dialog(self.id, prompt_message)

    @staticmethod
    async def _show_warning_for_unsupported_cities(
        context: TurnContext, luis_result: BookingDetails
    ) -> None:
        if luis_result.unsupported_airports:
            message_text = (
                f"Sorry but the following airports are not supported:"
                f" {', '.join(luis_result.unsupported_airports)}"
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await context.send_activity(message)
