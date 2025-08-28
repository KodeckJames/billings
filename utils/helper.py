import africastalking
from typing import Dict, Any, Optional


class VoiceHelper:
    """Helper class for Africa's Talking Voice API operations"""
    
    def __init__(self, api_key: str, username: str, virtual_number: str):
        """
        Initialize the VoiceHelper with Africa's Talking credentials
        
        Args:
            api_key (str): Your Africa's Talking API key
            username (str): Your Africa's Talking username (usually 'sandbox' for testing)
            virtual_number (str): Your virtual phone number
        """
        self.api_key = api_key
        self.username = username
        self.virtual_number = virtual_number
        
        # Initialize Africa's Talking
        africastalking.initialize(username, api_key)
        self.voice = africastalking.Voice
    
    def saySomething(self, options: Dict[str, str]) -> str:
        """
        Generate XML to make the system say something
        
        Args:
            options (dict): Dictionary containing 'speech' key with text to speak
            
        Returns:
            str: XML string for Say action
        """
        speech = options.get('speech', '')
        return f"<Say>{speech}</Say>"
    
    def ongea(self, textPrompt: str, finishOnKey: str = "#", 
              timeout: int = 10, callbackUrl: str = "") -> str:
        """
        Generate XML for collecting digits with a spoken prompt
        
        Args:
            textPrompt (str): Text to speak to the caller
            finishOnKey (str): Key that finishes digit collection (default: "#")
            timeout (int): Timeout in seconds (default: 10)
            callbackUrl (str): URL to call when digits are collected
            
        Returns:
            str: XML string for Say and CollectDigits actions
        """
        xml = f"<Say>{textPrompt}</Say>"
        xml += f"<CollectDigits timeout='{timeout}' finishOnKey='{finishOnKey}' callbackUrl='{callbackUrl}'/>"
        return xml
    
    def recordAudio(self, options: Dict[str, str]) -> str:
        """
        Generate XML for recording audio
        
        Args:
            options (dict): Dictionary with:
                - 'introductionText': Text to speak before recording
                - 'audioProcessingUrl': URL to send recording data
                
        Returns:
            str: XML string for Say and Record actions
        """
        intro_text = options.get('introductionText', 'Please record your message')
        processing_url = options.get('audioProcessingUrl', '')
        
        xml = f"<Say>{intro_text}</Say>"
        xml += f"<Record finishOnKey='#' maxLength='60' playBeep='true' callbackUrl='{processing_url}'/>"
        return xml
    
    def collectDigits(self, prompt: str, numDigits: int = 1, 
                     timeout: int = 10, finishOnKey: str = "#", 
                     callbackUrl: str = "") -> str:
        """
        Generate XML for collecting a specific number of digits
        
        Args:
            prompt (str): Text to speak to prompt user
            numDigits (int): Number of digits to collect (default: 1)
            timeout (int): Timeout in seconds (default: 10)
            finishOnKey (str): Key that finishes collection (default: "#")
            callbackUrl (str): URL to call when digits are collected
            
        Returns:
            str: XML string for Say and CollectDigits actions
        """
        xml = f"<Say>{prompt}</Say>"
        xml += f"<CollectDigits timeout='{timeout}' finishOnKey='{finishOnKey}' numDigits='{numDigits}' callbackUrl='{callbackUrl}'/>"
        return xml
    
    def playAudio(self, audio_url: str) -> str:
        """
        Generate XML to play an audio file
        
        Args:
            audio_url (str): URL of the audio file to play
            
        Returns:
            str: XML string for Play action
        """
        return f"<Play>{audio_url}</Play>"
    
    def dial(self, phone_number: str, record: bool = False, 
             sequentially: bool = False, caller_id: str = "") -> str:
        """
        Generate XML to dial another number
        
        Args:
            phone_number (str): Phone number to dial
            record (bool): Whether to record the call (default: False)
            sequentially (bool): Whether to dial numbers sequentially (default: False)
            caller_id (str): Caller ID to use (default: empty)
            
        Returns:
            str: XML string for Dial action
        """
        record_attr = 'record="true"' if record else ''
        sequential_attr = 'sequential="true"' if sequentially else ''
        caller_id_attr = f'callerId="{caller_id}"' if caller_id else ''
        
        attributes = ' '.join(filter(None, [record_attr, sequential_attr, caller_id_attr]))
        if attributes:
            return f"<Dial {attributes}><Number>{phone_number}</Number></Dial>"
        else:
            return f"<Dial><Number>{phone_number}</Number></Dial>"
    
    def redirect(self, url: str) -> str:
        """
        Generate XML to redirect the call to another URL
        
        Args:
            url (str): URL to redirect to
            
        Returns:
            str: XML string for Redirect action
        """
        return f"<Redirect>{url}</Redirect>"
    
    def reject(self) -> str:
        """
        Generate XML to reject the call
        
        Returns:
            str: XML string for Reject action
        """
        return "<Reject/>"
    
    def hangup(self) -> str:
        """
        Generate XML to hang up the call
        
        Returns:
            str: XML string for Hangup action
        """
        return "<Hangup/>"
    
    def make_call(self, to_number: str, from_number: str = None, 
                  callback_url: str = "") -> Dict[str, Any]:
        """
        Make an outbound call using Africa's Talking Voice API
        
        Args:
            to_number (str): Phone number to call
            from_number (str): Phone number to call from (optional)
            callback_url (str): URL for call events (optional)
            
        Returns:
            dict: Response from Africa's Talking API
        """
        try:
            if from_number is None:
                from_number = self.virtual_number
                
            recipients = [to_number]
            response = self.voice.call(from_number, recipients)
            return response
        except Exception as e:
            return {"error": str(e)}
    
    def upload_media(self, media_url: str, phone_number: str = None) -> Dict[str, Any]:
        """
        Upload media file to Africa's Talking servers
        
        Args:
            media_url (str): URL of the media file to upload
            phone_number (str): Phone number associated with the media (optional)
            
        Returns:
            dict: Response from Africa's Talking API
        """
        try:
            if phone_number is None:
                phone_number = self.virtual_number
                
            response = self.voice.upload_media_file(media_url, phone_number)
            return response
        except Exception as e:
            return {"error": str(e)}