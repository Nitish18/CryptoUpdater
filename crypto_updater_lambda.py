import urllib2
import json
import requests

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.f4f81b69-b764-4e33-a102-18f19e46bd9b"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    # custom intents
    if intent_name == "intro":
        return get_intro()

    elif intent_name == "price_coin":
        return get_coin_price(intent)     
        
    # predefined intents
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "CRYPTOUPDATER - Thanks"
    speech_output = "Thank you for using the Crypto Updater skill.  See you next time!"
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "CRYPTOUPDATER"
    speech_output = "Welcome to the Alexa Crypto Updater skill. " \
                    "You can ask me about prices of different Crypto Currencies" 
                    
    reprompt_text = "Please ask me about price of different coins" \
                    "for example bitcoin"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_intro():
    session_attributes = {}
    card_title = "Crypto Updater Status"
    reprompt_text = ""
    should_end_session = False

    speech_output = "Hello, cryptoupdater will basically tell you about latest prices of different crypto currencies like Bitcoin, Etherium, litecoin, etc. You just have to tell coin's name and it will fetch you the latest price in US Dollars."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_coin_price(intent):
    session_attributes = {}
    card_title = "Crypto Updater Status"
    speech_output = "Sorry, could not get you ! Can you please try again !! Try speaking name of the coin of which you want to know the price."
    reprompt_text = "Sorry, could not get you ! Can you please try again !! Try speaking name of the coin of which you want to know the price."
    should_end_session = False

    API_URL = 'https://chasing-coins.com/api/v1/std/coin/'

    if "coin" in intent["slots"]:
        coin_name = intent["slots"]["coin"]["value"]
        coin_code = get_coin_code(coin_name)
        if coin_code:
            API_URL += str(coin_code)
            api_resp = {}
            coin_price = "NA"
            try:
                api_resp = requests.get(API_URL)
                api_json_body = api_resp.json()
                coin_price = api_json_body.get('price',"NA")
            except:
                pass 
            speech_output = "The price of one  " + coin_name + '  is  ' + coin_price + " dollars"
            should_end_session = True
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_coin_code(coin_name):
    # mapping between coin name & it's code
    coin_mapping = {
      "vibe" : "VIBE",
      "request network" : "REQ",
      "power ledger" : "POWR",
      "bitShares" : "BTS",
      "tether" : "USDT",
      "bitcoin gold" : "BTG",
      "nem" : "XEM",
      "tron" : "TRX ",
      "vechain" : "VEN",
      "dash" : "DASH",
      "monero" : "XMR",
      "iota" : "MIOTA",
      "stellar" : "XLM",
      "neo" : "NEO",
      "cardano" : "ADA",
      "litecoin" : "LTC",
      "bitcoin cash" : "BCH",
      "ripple" : "XRP",
      "ethereum" : "ETH ",
      "bitcoin" : "BTC"
    }
    if str(coin_name) in coin_mapping:
        return coin_mapping[coin_name]
    return None    

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
