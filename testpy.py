import random, csv, io, requests, time, json

permanent_token = "EAAQKtFCxj3EBO8Ulz7nRX6VNZAVhndnRWedYCN7nLcK6TJDiNfzyHZAXyNWJQiMFnMQNPhZC6qONQ3btRnMuc5ZBdYMAP2ZAfxDTQo6MlSDNGQul4qn2TK9jv2TSWDBcE8hiZCAdElqell4nGO4cLkj8f1vi7eCC6eYXakHv4ldSXesEVnWyt7dEZCIfSf5kBZCCQGsSQA28bCHtNy0B3SZBRipZAzhrUZD"
whatsapp_business_id = "547994715063675"

url = f"https://graph.facebook.com/v21.0/{whatsapp_business_id}/message_templates"

# Define the template payload
payload = {
    "name": "template_for_otp_authentication",
    "language": "en_US",
    "category": "AUTHENTICATION",
    "components": [
        {
            "type": "HEADER",
            "format": "TEXT",
            "text": "OTP"
        },
        {
            "type": "BODY",
            "text": "Your OTP is 654321"
        },
        {
            "type": "FOOTER",
            "text": "Thank you"
        }
    ]
}

# Set the headers
headers = {
    "Authorization": f"Bearer {permanent_token}",
    "Content-Type": "application/json"
}

# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Handle the response
if response.status_code == 200:
    print("Message sent successfully:", response.json())
else:
    print("Failed to send message:", response.status_code, response.json())