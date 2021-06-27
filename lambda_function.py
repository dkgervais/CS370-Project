#
# Copyright 2019 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
# These materials are licensed under the Amazon Software License in connection with the Alexa Gadgets Program.
# The Agreement is available at https://aws.amazon.com/asl/.
# See the Agreement for the specific terms and conditions of the Agreement.
# Capitalized terms not defined in this file have the meanings given to them in the Agreement.
#
import logging.handlers
import requests
import uuid

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.serialize import DefaultSerializer

from ask_sdk_model import IntentRequest
from ask_sdk_model.ui import PlayBehavior

from ask_sdk_model.interfaces.custom_interface_controller import (
    StartEventHandlerDirective, EventFilter, Expiration, FilterMatchAction,
    StopEventHandlerDirective,
    SendDirectiveDirective,
    Header,
    Endpoint,
    EventsReceivedRequest,
    ExpiredRequest
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
serializer = DefaultSerializer()
skill_builder = SkillBuilder()

# This defines the intent handler for the pi_to_alexa intent
@skill_builder.request_handler(can_handle_func=is_intent_name("pi_to_alexa"))
def pi_to_alexa_intent_handler(handler_input: HandlerInput):
    logger.info("pi_to_alexa intent recieved")
    response_builder = handler_input.response_builder

    system = handler_input.request_envelope.context.system
    api_access_token = system.api_access_token
    api_endpoint = system.api_endpoint

    # Get connected gadget endpoint ID.
    endpoints = get_connected_endpoints(api_endpoint, api_access_token)
    logger.debug("Checking endpoint..")
    if not endpoints:
        logger.debug("No connected gadget endpoints available.")
        return (response_builder
                .speak("Sorry, nothing is connected.")
                .set_should_end_session(True)
                .response)

    endpoint_id = endpoints[0]['endpointId']
    
    session_attr = handler_input.attributes_manager.session_attributes

    # Create a token to be assigned to the EventHandler and store it
    # in session attributes for stopping the EventHandler later.
    token = str(uuid.uuid4())
    session_attr['token'] = token

    # Send the data do the pi
    data = handler_input.request_envelope.request.intent.slots

    # Note that the directive added below passes the data to the pi
    # and waits 5000 ms for a response from it
    return (response_builder
            .add_directive(build_pi_to_alexa_directive(endpoint_id,
                                                     data))
            .add_directive(build_start_event_handler_directive(token, 5000,
                                                               'Custom.MyGadget', 'PiToAlexa',
                                                               FilterMatchAction.SEND_AND_TERMINATE,
                                                               {'data': "The timer expired before data was passed back in an event."}))
            .response)


# This defines the intent handler for the alexa_to_pi intent
@skill_builder.request_handler(can_handle_func=is_intent_name("alexa_to_pi"))
def alexa_to_pi_intent_handler(handler_input: HandlerInput):
    logger.info("alexa_to_pi intent recieved")
    response_builder = handler_input.response_builder

    system = handler_input.request_envelope.context.system
    api_access_token = system.api_access_token
    api_endpoint = system.api_endpoint

    # Get connected gadget endpoint ID.
    endpoints = get_connected_endpoints(api_endpoint, api_access_token)
    logger.debug("Checking endpoint..")
    if not endpoints:
        logger.debug("No connected gadget endpoints available.")
        return (response_builder
                .speak("Sorry, nothing is connected.")
                .set_should_end_session(True)
                .response)

    endpoint_id = endpoints[0]['endpointId']
    
    session_attr = handler_input.attributes_manager.session_attributes


    # Create a token to be assigned to the EventHandler and store it
    # in session attributes for stopping the EventHandler later.
    token = str(uuid.uuid4())
    session_attr['token'] = token

    # Send the data do the pi
    data = handler_input.request_envelope.request.intent.slots

    return (response_builder
            .add_directive(build_alexa_to_pi_directive(endpoint_id,
                                                     data))
            .response)


@skill_builder.request_handler(can_handle_func=is_request_type("CustomInterfaceController.EventsReceived"))
def custom_interface_event_handler(handler_input: HandlerInput):
    logger.info("== Received Custom Event ==")

    request = handler_input.request_envelope.request
    session_attr = handler_input.attributes_manager.session_attributes
    response_builder = handler_input.response_builder

    # Validate event handler token
    if session_attr['token'] != request.token:
        logger.info("EventHandler token doesn't match. Ignoring this event.")
        return (response_builder
                .speak("EventHandler token doesn't match. Ignoring this event.")
                .response)

    custom_event = request.events[0]
    payload = custom_event.payload
    namespace = custom_event.header.namespace
    name = custom_event.header.name

    # This is where we tell the function to simply speak out the payload sent from the Pi
    if namespace == 'Custom.MyGadget' and name == 'PiToAlexa':
        return (response_builder
                .speak(str(payload['data']))
                .set_should_end_session(True)
                .response)

    return response_builder.response


@skill_builder.request_handler(can_handle_func=is_request_type("CustomInterfaceController.Expired"))
def custom_interface_expiration_handler(handler_input):
    logger.info("== Custom Event Expiration Input ==")

    request = handler_input.request_envelope.request
    response_builder = handler_input.response_builder
    session_attr = handler_input.attributes_manager.session_attributes
    endpoint_id = session_attr['endpointId']

    # When the EventHandler expires, speak and end the skill session.
    return (response_builder
            .add_directive(build_stop_led_directive(endpoint_id))
            .speak(request.expiration_payload['data'])
            .set_should_end_session(True)
            .response)






@skill_builder.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    logger.info("Session ended with reason: " +
                handler_input.request_envelope.request.reason.to_str())
    return handler_input.response_builder.response


@skill_builder.exception_handler(can_handle_func=lambda i, e: True)
def error_handler(handler_input, exception):
    logger.info("==Error==")
    logger.error(exception, exc_info=True)
    return (handler_input.response_builder
            .speak("I'm sorry, something went wrong!").response)


@skill_builder.global_request_interceptor()
def log_request(handler_input):
    # Log the request for debugging purposes.
    logger.info("==Request==\r" +
                str(serializer.serialize(handler_input.request_envelope)))


@skill_builder.global_response_interceptor()
def log_response(handler_input, response):
    # Log the response for debugging purposes.
    logger.info("==Response==\r" + str(serializer.serialize(response)))
    logger.info("==Session Attributes==\r" +
                str(serializer.serialize(handler_input.attributes_manager.session_attributes)))





# Get the ids for the gadgets that are connected to the Alexa device
def get_connected_endpoints(api_endpoint, api_access_token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(api_access_token)
    }

    api_url = api_endpoint + "/v1/endpoints"
    endpoints_response = requests.get(api_url, headers=headers)

    if endpoints_response.status_code == requests.codes['ok']:
        return endpoints_response.json()["endpoints"]

def build_start_event_handler_directive(token, duration_ms, namespace,
                                        name, filter_match_action, expiration_payload):
    return StartEventHandlerDirective(
        token=token,
        event_filter=EventFilter(
            filter_expression={
                'and': [
                    {'==': [{'var': 'header.namespace'}, namespace]},
                    {'==': [{'var': 'header.name'}, name]}
                ]
            },
            filter_match_action=filter_match_action
        ),
        expiration=Expiration(
            duration_in_milliseconds=duration_ms,
            expiration_payload=expiration_payload))


# Build the directive to send data to the pi
def build_alexa_to_pi_directive(endpoint_id, data):
    return SendDirectiveDirective(
        header=Header(namespace='Custom.MyGadget', name='AlexaToPi'),
        endpoint=Endpoint(endpoint_id=endpoint_id),
        payload={
            'data': data
        }
    )

# Build the directive to send data to the pi with expectation that
# pi will send data back
def build_pi_to_alexa_directive(endpoint_id, data):
    return SendDirectiveDirective(
        header=Header(namespace='Custom.MyGadget', name='PiToAlexa'),
        endpoint=Endpoint(endpoint_id=endpoint_id),
        payload={
            'data': data
        }
    )

lambda_handler = skill_builder.lambda_handler()
