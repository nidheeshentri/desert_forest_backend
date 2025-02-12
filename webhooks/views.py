from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from account.models import Message
import environ, requests

env = environ.Env()
phone_number_id = env("PHONE_NUMBER_ID")
access_token = env("TOKEN")
auto_reply_text = env("AUTOREPLYTEXT")

# Create your views here.

class WebhooksView(APIView):
    def get(self, request):
        print(request.GET)
        print("GET request")
        print(request.GET["hub.challenge"])
        return Response(int(request.GET["hub.challenge"]))

    def post(self, request):
        payload = json.loads(request.body)
        print(payload)
        # Process the payload
        for entry in payload.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # Handle incoming messages
                if 'messages' in value:
                    for message in value['messages']:
                        message_id = message.get('id')
                        status_type = message.get('status')
                        timestamp = message.get('timestamp')
                        from_number = message.get('from')
                        to_number = value['metadata'].get('phone_number_id')
                        timestamp = message.get('timestamp')
                        text = message.get('text', {}).get('body') if message.get('type') == 'text' else None
                        print("============================================================")
                        print("Messages")
                        print("message_id -", message_id)
                        print("status_type -", status_type)
                        print("timestamp -", timestamp)
                        print("from_number -", from_number)
                        print("to_number -", to_number)
                        print("text -", text)
                        print("============================================================")
                        new_message = Message.objects.create(
                            recipient_phone = from_number,
                            recipient_name = from_number,
                            response_id = message_id,
                            response_text = text,
                            from_admin = False
                        )
                        url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"

                        # Define the template payload
                        payload = {
                            "messaging_product": "whatsapp",
                            "to": from_number,
                            "text": { "body": auto_reply_text },
                        }

                        # Set the headers
                        token = AccessToken.objects.all().last()
                        headers = {
                            "Authorization": f"Bearer {token.token}",
                            "Content-Type": "application/json"
                        }

                        # Send the POST request
                        response = requests.post(url, headers=headers, data=json.dumps(payload))

                        # Handle the response
                        if response.status_code == 200:
                            print("Message sent successfully")
                        else:
                            print("Something went wrong, try with new token.")
                # Handle message status updates
                if 'statuses' in value:
                    for status in value['statuses']:
                        message_id = status.get('id')
                        status_type = status.get('status')
                        timestamp = status.get('timestamp')

                        try:
                            message = Message.objects.get(response_id=message_id)
                            message.status = status_type.upper()
                            message.save()
                            print("===========================================")
                            print("Success msg saved")
                            print("===========================================")
                        except:
                            print("===========================================")
                            print("Error msg not saved")
                            print("===========================================")
                            pass

        return Response({"status": "Success"})

def save_message(message, metadata):
    message_id = message.get('id')
    from_number = message.get('from')
    to_number = metadata.get('phone_number_id')
    timestamp = message.get('timestamp')
    text = message.get('text', {}).get('body') if message.get('type') == 'text' else None
    
    # Save to database
    WhatsAppMessage.objects.create(
        message_id=message_id,
        from_number=from_number,
        to_number=to_number,
        timestamp=timezone.datetime.fromtimestamp(int(timestamp), tz=timezone.utc),
        text=text
    )

def save_message_status(status):
    # Extract relevant data
    message_id = status.get('id')
    status_type = status.get('status')
    timestamp = status.get('timestamp')
    
    # Find the corresponding message
    try:
        message = Message.objects.get(response_id=message_id)
        message.status = status_type
        message.save()
    except:
        print("===========================================")
        print("Error msg not saved")
        print("===========================================")