import os
import asyncio
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import Response

from utils.helper import VoiceHelper

load_dotenv()
app = FastAPI(title="Africa's Talking Voice API", version="1.0.0")

# Load environment variables
AT_apiKey = os.getenv("AFRICASTALKING_API_KEY")
AT_username = os.getenv("AFRICASTALKING_USERNAME") 
AT_virtualNumber = os.getenv("VIRTUAL_NUMBER")
APP_URL = os.getenv("APP_URL", "https://your-domain.com")  # Change this to your domain

ATVoice = VoiceHelper(AT_apiKey, AT_username, AT_virtualNumber)


async def maybe_await(result):
    """Helper function to handle both sync and async results"""
    if hasattr(result, "__await__"):
        return await result
    return result


def create_xml_response(content: str) -> str:
    """Helper function to create XML response"""
    return f"<?xml version='1.0' encoding='UTF-8'?><Response>{content}</Response>"


@app.post("/voice")
async def voice_entry(
    sessionId: Optional[str] = Form(None),
    callerNumber: Optional[str] = Form(None)
):
    """Entry point for incoming voice calls"""
    try:
        print(f"Incoming call - Session: {sessionId}, Caller: {callerNumber}")
        
        response_content = (
            "<Say>Welcome to Ongea Emergency Services! "
            "Press 1 for English or 2 for Swahili.</Say>"
            f"<CollectDigits timeout='10' finishOnKey='#' numDigits='1' "
            f"callbackUrl='{APP_URL}/voice/language'/>"
        )
        
        xml_response = create_xml_response(response_content)
        return Response(content=xml_response, media_type="text/xml")
        
    except Exception as e:
        print(f"Error in voice_entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/voice/language")
async def language_selection(
    dtmfDigits: Optional[str] = Form(None),
    sessionId: Optional[str] = Form(None),
    callerNumber: Optional[str] = Form(None)
):
    """Handle language selection"""
    try:
        pressed_key = dtmfDigits
        print(f"Language selection - Key: {pressed_key}")
        
        if not pressed_key or pressed_key not in ["1", "2"]:
            call_actions = await maybe_await(
                ATVoice.saySomething({
                    "speech": "Invalid selection. Please try again."
                })
            )
        else:
            # For now, proceed in English regardless of selection
            call_actions = await maybe_await(
                ATVoice.ongea(
                    textPrompt="Welcome to Ongea Emergency Services. Press 1 to report hunger, press 2 to report water shortage, press 3 for medical emergency.",
                    finishOnKey="#",
                    timeout=10,
                    callbackUrl=f"{APP_URL}/service/selection"
                )
            )
        
        xml_response = create_xml_response(call_actions)
        return Response(content=xml_response, media_type="text/xml")
        
    except Exception as e:
        print(f"Error in language_selection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/service/selection")
async def service_selection(
    dtmfDigits: Optional[str] = Form(None),
    sessionId: Optional[str] = Form(None),
    callerNumber: Optional[str] = Form(None)
):
    """Handle main service selection"""
    try:
        pressed_key = dtmfDigits
        print(f"Service selection - Key: {pressed_key}")
        
        if not pressed_key:
            return Response(content="", status_code=204)
        
        call_actions = None
        
        if pressed_key == "1":
            # Hunger reporting
            call_actions = await maybe_await(
                ATVoice.ongea(
                    textPrompt="Thank you for reporting hunger. Please select your region: Press 1 for Nairobi, 2 for Turkana, 3 for Kiambu.",
                    finishOnKey="#",
                    timeout=15,
                    callbackUrl=f"{APP_URL}/hunger/region"
                )
            )
        elif pressed_key == "2":
            # Water shortage reporting  
            call_actions = await maybe_await(
                ATVoice.ongea(
                    textPrompt="Thank you for reporting water shortage. Please select your region: Press 1 for Nairobi, 2 for Turkana, 3 for Kiambu.",
                    finishOnKey="#",
                    timeout=15,
                    callbackUrl=f"{APP_URL}/water/region"
                )
            )
        elif pressed_key == "3":
            # Medical emergency
            call_actions = await maybe_await(
                ATVoice.ongea(
                    textPrompt="Medical emergency reported. Please select your region: Press 1 for Nairobi, 2 for Turkana, 3 for Kiambu.",
                    finishOnKey="#", 
                    timeout=15,
                    callbackUrl=f"{APP_URL}/emergency/region"
                )
            )
        else:
            call_actions = await maybe_await(
                ATVoice.saySomething({
                    "speech": "Invalid selection. Please press 1, 2, or 3."
                })
            )
        
        xml_response = create_xml_response(call_actions)
        return Response(content=xml_response, media_type="text/xml")
        
    except Exception as e:
        print(f"Error in service_selection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/hunger/region")
async def hunger_region_selection(
    dtmfDigits: Optional[str] = Form(None),
    sessionId: Optional[str] = Form(None),
    callerNumber: Optional[str] = Form(None)
):
    """Handle hunger region selection"""
    region_responses = {
        "1": "Thank you. Nairobi region office has been notified about the hunger situation. They will contact you shortly.",
        "2": "Thank you. Turkana region office has been notified about the hunger situation. They will contact you shortly.", 
        "3": "Thank you. Kiambu region office has been notified about the hunger situation. They will contact you shortly."
    }
    
    return await handle_region_response(dtmfDigits, region_responses)


@app.post("/water/region")
async def water_region_selection(
    dtmfDigits: Optional[str] = Form(None),
    sessionId: Optional[str] = Form(None),
    callerNumber: Optional[str] = Form(None)
):
    """Handle water shortage region selection"""
    region_responses = {
        "1": "Thank you. Nairobi water department has been notified about the water shortage. They will address this issue.",
        "2": "Thank you. Turkana water department has been notified about the water shortage. They will address this issue.",
        "3": "Thank you. Kiambu water department has been notified about the water shortage. They will address this issue."
    }
    
    return await handle_region_response(dtmfDigits, region_responses)


@app.post("/emergency/region")
async def emergency_region_selection(
    dtmfDigits: Optional[str] = Form(None),
    sessionId: Optional[str] = Form(None),
    callerNumber: Optional[str] = Form(None)
):
    """Handle emergency region selection - proceeds to record audio"""
    try:
        pressed_key = dtmfDigits
        
        if pressed_key in ["1", "2", "3"]:
            regions = {"1": "Nairobi", "2": "Turkana", "3": "Kiambu"}
            region_name = regions[pressed_key]
            
            call_actions = await maybe_await(
                ATVoice.recordAudio({
                    "introductionText": f"Emergency services for {region_name} region activated. Please describe your emergency in detail and press hash when finished.",
                    "audioProcessingUrl": f"{APP_URL}/emergency/recording"
                })
            )
        else:
            call_actions = await maybe_await(
                ATVoice.saySomething({
                    "speech": "Invalid selection. Please press 1, 2, or 3."
                })
            )
        
        xml_response = create_xml_response(call_actions)
        return Response(content=xml_response, media_type="text/xml")
        
    except Exception as e:
        print(f"Error in emergency_region_selection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/emergency/recording")
async def emergency_recording_handler(
    recordingUrl: Optional[str] = Form(None),
    durationInSeconds: Optional[str] = Form(None),
    sessionId: Optional[str] = Form(None),
    callerNumber: Optional[str] = Form(None)
):
    """Handle emergency audio recording"""
    try:
        print(f"Emergency recording received - URL: {recordingUrl}, Duration: {durationInSeconds}s")
        
        # Here you would typically:
        # 1. Save the recording URL to your database
        # 2. Send notifications to emergency services
        # 3. Process the audio if needed
        
        call_actions = await maybe_await(
            ATVoice.saySomething({
                "speech": "Your emergency report has been recorded and sent to the appropriate authorities. Emergency services will respond shortly. Thank you for calling."
            })
        )
        
        xml_response = create_xml_response(call_actions)
        return Response(content=xml_response, media_type="text/xml")
        
    except Exception as e:
        print(f"Error in emergency_recording_handler: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_region_response(pressed_key: Optional[str], responses: dict) -> Response:
    """Generic handler for region responses"""
    try:
        if not pressed_key:
            return Response(content="", status_code=204)
        
        speech_text = responses.get(pressed_key, "Invalid selection. Goodbye.")
        
        call_actions = await maybe_await(
            ATVoice.saySomething({"speech": speech_text})
        )
        
        xml_response = create_xml_response(call_actions)
        return Response(content=xml_response, media_type="text/xml")
        
    except Exception as e:
        print(f"Error in handle_region_response: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Special endpoint for testing - matches your original logic
@app.post("/ongea")
async def ongea_special(
    dtmfDigits: Optional[str] = Form(None)
):
    """Special endpoint that checks for code '2545'"""
    try:
        pressed_key = dtmfDigits
        print(f"DEBUG: Pressed key = {pressed_key}")

        if pressed_key in [None, "undefined"]:
            return Response(content="", status_code=204)

        # Check if the entered digits are exactly "2545"
        if pressed_key == "2545":
            call_actions = await maybe_await(
                ATVoice.ongea(
                    textPrompt="Welcome Back to Medicare Services.",
                    finishOnKey="#",
                    timeout=15,
                    callbackUrl=f"{APP_URL}/emergency/region"
                )
            )
        else:
            call_actions = await maybe_await(
                ATVoice.saySomething({
                    "speech": "The code entered is not valid."
                })
            )

        xml_response = create_xml_response(call_actions)
        return Response(content=xml_response, media_type="text/xml")

    except Exception as e:
        print(f"Error in ongea_special: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "voice_api"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)