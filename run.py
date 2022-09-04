import logging
import ask_sdk_core.utils as ask_utils
import json

# Webserver
from flask import Flask
from flask_ask_sdk.skill_adapter import SkillAdapter

# Alexa thingies
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective)

from ask_sdk_model import Response



__MAC_ADDRESS__ = ""



# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Class gets triggered with the "open" command
class LaunchRequestHandler(AbstractRequestHandler):
    # Handler for Skill Launch.
    # Alexa, open <skill trigger>
    def can_handle(self, handler_input: HandlerInput) -> bool:
        logging.debug("Request type: " + handler_input.request_envelope.request.object_type)

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        logging.debug("LaunchRequestHandler")
        # What Alexa will say
        speak_output = f"Turning on PC"
        
        #====================================================================
        # Add a visual with Alexa Layouts
        #====================================================================
        # Import an Alexa Presentation Language (APL) template
        with open("./documents/APL_simple.json") as apl_doc:
            apl_simple = json.load(apl_doc)

            if ask_utils.get_supported_interfaces(
                    handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        document=apl_simple,
                        datasources={
                            "myData": {
                                #====================================================================
                                # Set a headline and subhead to display on the screen if there is one
                                #====================================================================
                                "Title": 'Turned on.',
                                "Subtitle": "",
                            }
                        }
                    )
                )

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    # Handler for Hello World Intent.
    # It's still here because it's useful for some copy-paste action
    # Alexa, <skill trigger> hello
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speak_output = "Hello World!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    # Handler for Help Intent.
    # Alexa, <skill trigger> help
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    # Single handler for Cancel and Stop Intent.
    # Useless but it's a default trigger.
    # Alexa, stop
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input: HandlerInput) -> Response:
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    # Handler for Fallback Intent.
    # When Alexa doesn't understand what you say (so pretty often), that's what it'll return
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    # Handler for Session End.
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Register the handlers
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()


# Create the web app and run it
app = Flask(__name__)

skill_adapter = SkillAdapter(
    skill=sb.create(), skill_id=1, app=app)

@app.route("/", methods=["POST"])
def invoke_skill():
    return skill_adapter.dispatch_request()

app.run(host="0.0.0.0", port=8080)
