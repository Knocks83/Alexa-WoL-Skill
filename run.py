import logging
import struct
import json
import socket

# Webserver
from flask import Flask
from flask_ask_sdk.skill_adapter import SkillAdapter

# Alexa thingies
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective)
from ask_sdk_model import Response

# Dotenv thingies
from dotenv import load_dotenv
from os import getenv
from os.path import dirname, realpath


# Load dotenv and get the mac address
load_dotenv(dotenv_path=dirname(realpath(__file__))+'/config.env')
__MAC_ADDRESS__ = getenv('MAC_ADDRESS')


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
        speak_output = "Turning on PC"
        if handler_input.request_envelope.request.locale == 'it-IT':
            speak_output = 'Sto accendendo il PC'
        
        #====================================================================
        # Add a visual with Alexa Layouts
        #====================================================================
        # Import an Alexa Presentation Language (APL) template
        with open(dirname(realpath(__file__))+"/documents/APL_simple.json") as apl_doc:
            apl_simple = json.load(apl_doc)

            if ask_utils.get_supported_interfaces(
                    handler_input).alexa_presentation_apl is not None:
                title = "Turned on."
                if handler_input.request_envelope.request.locale == 'it-IT':
                    title = f'Acceso.'
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        document=apl_simple,
                        datasources={
                            "myData": {
                                #====================================================================
                                # Set a headline and subhead to display on the screen if there is one
                                #====================================================================
                                "Title": title,
                                "Subtitle": "",
                            }
                        }
                    )
                )

        # Send WoL packet
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        mac_arr = __MAC_ADDRESS__.split(':')
        address = struct.pack('BBBBBB', int(mac_arr[0],16),
            int(mac_arr[1],16),
            int(mac_arr[2],16),
            int(mac_arr[3],16),
            int(mac_arr[4],16),
            int(mac_arr[5],16))
        s.sendto(b'\xff' * 6 + address * 16, ("255.255.255.255",9))

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    # Handler for Help Intent.
    # Alexa, <skill trigger> help
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speak_output = "You can just open me, and I'll turn your configured PC on!"
        if handler_input.request_envelope.request.locale == 'it-IT':
            speak_output = 'Puoi solo aprirmi, e io accenderò il PC che hai configurato!'

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
        if handler_input.request_envelope.request.locale == 'it-IT':
            speak_output = 'Arrivederci!'

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
        if handler_input.request_envelope.request.locale == 'it-IT':
            speech = 'Hmm, non ne sono sicuro. Cosa vorresti che faccia?'

        reprompt = "I didn't catch that. What can I help you with?"
        if handler_input.request_envelope.request.locale == 'it-IT':
            reprompt = 'Non ho capito. Come posso aiutarti?'


        return handler_input.response_builder.speak(speech).ask(reprompt).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    # Handler for Session End.
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


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
        if handler_input.request_envelope.request.locale == 'it-IT':
            speak_output = "Scusa, ho riscontrato problemi nell'esecuzione. Riprova."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


# Register the handlers
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

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
