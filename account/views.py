from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, TemplateSerializer, CampaignSerializer, MessageSerializer, ContactSerializer, ContactGroupSerializer
from django.core.mail import send_mail
import random, csv, io, requests, time, json
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from .models import CustomUser, OTP, UserRole, Template, Campaign, Message, Contact, ContactGroup
import environ
from rest_framework import serializers
from django.db.models import Count
from .models import AccessToken

env = environ.Env()

phone_number_id = env("PHONE_NUMBER_ID")
business_id = env("BUSINESS_ID")
whatsapp_business_id = env("WHATSAPP_BUSINESS_ID")
access_token = env("TOKEN")
permanent_token = env("PERMANENT_TOKEN")

# Create your views here.

def generateOTP(digits, chars):
    otp = ""
    for index in range(digits):
        otp+=random.choice(chars)

    return otp

class GetUserData(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user_data = UserSerializer(request.user)
            return Response(user_data.data)
        return Response("Not loggedin")
    
class ForgorPassword(APIView):
    def get(self, request):
        email = request.GET.get("email")
        if email and CustomUser.objects.filter(email = email).exists():
            generated_otp = generateOTP(6,"1234567890")
            user = CustomUser.objects.get(email = email)
            OTP.objects.filter(user = user).delete()
            OTP.objects.create(otp = generated_otp, user = user)
            send_mail(
                'Reset password OTP',
                f'OTP - {generated_otp}',
                'rajendra@gmail.com',
                [email,],
                fail_silently=False,
            )
            return Response({"detail": "Check your mail to get the OTP"})
        return Response({"detail": "Email not found, Enter valid Email"}, HTTP_404_NOT_FOUND)
        
    
    def post(self, request):
        otp = request.data.get("otp")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")
        email = request.data.get("email")
        user = CustomUser.objects.get(email = email)

        otp_obj = OTP.objects.filter(user = user, otp = otp)
        if otp_obj.exists():
            user.set_password(password)
            user.save()
            return Response({"detail": "Password reset Successfull."})
        return Response({"detail": "Invalid OTP. Please enter valid OTP."}, HTTP_400_BAD_REQUEST)
    

class Register(APIView):
    def post(self, request):
        email = request.data.get("email")
        if CustomUser.objects.filter(email = email).exists():
            return Response({"detail": "Email ID already exists"}, HTTP_400_BAD_REQUEST)
        password = request.data.get("password")
        user_role = UserRole.objects.get(role = "Customer Admin")
        user = CustomUser.objects.create(email = email, role = user_role)
        user.set_password(password)
        user.save()

        return Response({"detail": "Registered Successfully"})
    
class TemplateListCreateView(generics.ListCreateAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [permissions.AllowAny]
    
class TemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [permissions.AllowAny]
    
class CampaignListCreateView(generics.ListCreateAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.AllowAny]
    
class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.AllowAny]
    
class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]
    
class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]
    
class ContactListCreateView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]
    
class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]
    
class ContactGroupListCreateView(generics.ListCreateAPIView):
    queryset = ContactGroup.objects.all()
    serializer_class = ContactGroupSerializer
    permission_classes = [permissions.AllowAny]
    
class ContactGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactGroup.objects.all()
    serializer_class = ContactGroupSerializer
    permission_classes = [permissions.AllowAny]


class CreateCampaign(APIView):
    def post(self, request):
        file = request.FILES["file"]
        print(request.data)

        decoded_file = file.read().decode('utf-8')
        csv_reader = csv.reader(io.StringIO(decoded_file))
        contact_group = ContactGroup.objects.create(group_name=request.data.get("campaign_name"))

        campaign_name = request.data.get("campaign_name")
        template_name = request.data.get("template_name")
        template = Template.objects.get(id = request.data.get("template"))

        new_campaign = Campaign.objects.create(name=campaign_name, template=template, to_group=contact_group, status="Running")

        url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
        token = AccessToken.objects.all().last()
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }
        new_campaign.save()
        for contact in csv_reader:
            if contact[0] != "name":
                print(contact[1])
                name = contact[0]
                phone = contact[1]
                new_contact = Contact.objects.create(name = name, phone = phone, contact_group = contact_group
                )

                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone,
                    "type": "template",
                    "template": {
                        "name": template.name,  # Your pre-approved template name
                        "language": {"code": template.language} 
                    }
                }
                
                msg_response = requests.post(url, headers=headers, json=payload)
                payload = msg_response.json()
                # {'messaging_product': 'whatsapp', 'contacts': [{'input': '917305055356', 'wa_id': '917305055356'}], 'messages': [{'id': 'wamid.HBgMOTE3MzA1MDU1MzU2FQIAERgSRDFERkFGREZCMUM1MzYyRjQyAA==', 'message_status': 'accepted'}]}

                try:
                    print(payload.get("messages"))
                    print(payload.get("messages")[0].get("id"))
                    Message.objects.create(
                        campaign = new_campaign,
                        recipient_phone = phone,
                        recipient_name = name,
                        status = "PENDING",
                        response_id = payload.get("messages")[0].get("id")
                    )
                    print("Created")
                except:
                    pass
                

        new_campaign.status = "Completed"
        new_campaign.save()
        return Response({"status: Success"})

class CreateTemplate(APIView):
    def post(self, request):
        print(request.FILES)

        data = request.data.dict()

        # Convert button fields (JSON strings) to Python objects
        for key, value in data.items():
            if 'buttons' in key:
                data[key] = json.loads(value)

        print(data)

        url = f"https://graph.facebook.com/v21.0/{whatsapp_business_id}/message_templates"

        # Define the template payload
        template_name = data.get("templateName")
        template_name=template_name.replace(" ", "_")
        payload = {
            "name": template_name,
            "language": "en_US",
            "category": data.get("category"),
            "components": [
                {
                    "type": "HEADER",
                    "format": "TEXT",
                    "text": "Valentines day offer"
                },
                {
                    "type": "BODY",
                    "text": data.get("content")
                },
                {
                    "type": "FOOTER",
                    "text": data.get("footerContent")
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
            new_template = Template()
            new_template.name = template_name
            new_template.language = data.get("language")
            new_template.category = data.get("category")
            new_template.template_type = data.get("templateType")
            new_template.body = data.get("content")
            new_template.headerType = data.get("headerType")
            if (data.get("headerContent") and data.get("headerContent") != "undefined"):
                new_template.header = data.get("headerContent")
            new_template.footer = data.get("footerContent")
            new_template.header_media = request.FILES.get("templateFile")
            if data.get("buttons[0]"):
                new_template.button1 = data.get("buttons[0]")
            if data.get("buttons[1]"):
                new_template.button2 = data.get("buttons[1]")
            if data.get("buttons[2]"):
                new_template.button3 = data.get("buttons[2]")
            if data.get("buttons[3]"):
                new_template.button4 = data.get("buttons[3]")
            new_template.save()
            return Response({"status": "Success"})
        else:
            print("Failed to send message:", response.status_code, response.json())


        return Response({"status": "Error"}, HTTP_400_BAD_REQUEST)


class CampaignStatisticsSerializer(serializers.Serializer):
    campaign_name = serializers.CharField()
    template_name = serializers.CharField()
    start_date = serializers.DateTimeField()
    sent_percentage = serializers.FloatField()
    pending_percentage = serializers.FloatField()
    delivered_percentage = serializers.FloatField()
    read_percentage = serializers.FloatField()
    failed_percentage = serializers.FloatField()

    def __init__(self, campaign, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aggregate message statuses for this campaign
        total_messages = campaign.messages.count()
        if total_messages > 0:
            message_counts = campaign.messages.values('status').annotate(status_count=Count('status'))
            message_statuses = {status['status']: status['status_count'] for status in message_counts}
            
            # Calculate percentages
            self.fields['campaign_name'] = serializers.CharField(default=campaign.name)
            self.fields['template_name'] = serializers.CharField(default=campaign.template.name)
            self.fields['start_date'] = serializers.DateTimeField(default=campaign.created_at)
            
            self.fields['sent_percentage'] = serializers.FloatField(default=self.calculate_percentage(message_statuses, 'SENT', total_messages))
            self.fields['pending_percentage'] = serializers.FloatField(default=self.calculate_percentage(message_statuses, 'PENDING', total_messages))
            self.fields['delivered_percentage'] = serializers.FloatField(default=self.calculate_percentage(message_statuses, 'DELIVERED', total_messages))
            self.fields['read_percentage'] = serializers.FloatField(default=self.calculate_percentage(message_statuses, 'READ', total_messages))
            self.fields['failed_percentage'] = serializers.FloatField(default=self.calculate_percentage(message_statuses, 'FAILED', total_messages))

    def calculate_percentage(self, message_statuses, status, total_messages):
        """Helper method to calculate the percentage of a given status."""
        status_count = message_statuses.get(status, 0)
        return (status_count / total_messages) * 100

class CampaignStatisticsView(generics.GenericAPIView):
    serializer_class = CampaignStatisticsSerializer
    
    def get(self, request, *args, **kwargs):
        campaign_id = kwargs.get('campaign_id')
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return Response({'detail': 'Campaign not found'}, status=404)
        
        # Create and return the statistics serializer
        serializer = self.get_serializer(campaign=campaign)
        return Response(serializer.data)

class CampaignStatisticsListView(generics.ListAPIView):
    serializer_class = CampaignStatisticsSerializer

    def calculate_percentage(self, message_statuses, status, total_messages):
        """Helper method to calculate the percentage of a given status."""
        status_count = message_statuses.get(status, 0)
        if status_count:
            return (status_count / total_messages) * 100
        return 0
    
    def get_queryset(self):
        # Query all campaigns to display statistics for each
        return Campaign.objects.all().order_by("-id")
    
    def list(self, request, *args, **kwargs):
        campaigns = self.get_queryset()
        statistics = []
        
        # Loop through each campaign and gather statistics
        for campaign in campaigns:
            total_messages = campaign.messages.count()
            message_counts = campaign.messages.values('status').annotate(status_count=Count('status'))
            message_statuses = {status['status']: status['status_count'] for status in message_counts}

            # {
            #     id: "1",
            #     title: "Black Friday Sale",
            #     template: "Seasonal Promotion",
            #     status: "Ongoing",
            #     metrics: [
            #         { label: "Sent", value: 10000, percentage: 100, color: "#4338CA" },
            #         { label: "Queued", value: 300, percentage: 3, color: "#6366F1" },
            #         { label: "Delivered", value: 9550, percentage: 95.5, color: "#60A5FA" },
            #         { label: "Read", value: 4701, percentage: 47.01, color: "#34D399" },
            #         { label: "Interaction", value: 209, percentage: 2.09, color: "#10B981" },
            #         { label: "Failed", value: 1, percentage: 0.01, color: "#EF4444" }
            #     ],
            #     additionalInfo: [
            #         { label: "Category", value: "Promotional", bgColor: "bg-pink-100" },
            #         { label: "Template", value: "Seasonal Promotion", bgColor: "bg-green-100" },
            #         { label: "Total Count", value: "10000", bgColor: "bg-blue-100" },
            #         { label: "Budget", value: "5,000.00$", bgColor: "bg-green-100" },
            #         { label: "Start on", value: "24/11/23 00:00" },
            #         { label: "Ended on", value: "27/11/23 23:59" }
            #     ],
            #     responseCount: 2,
            #     performanceTrend: [
            #         { date: "2023-11-24", value: 100 },
            #         { date: "2023-11-25", value: 250 },
            #         { date: "2023-11-26", value: 380 },
            #         { date: "2023-11-27", value: 420 }
            #     ]
            # },

            data = {
                'id': str(campaign.id),
                'title': campaign.name,
                'status': campaign.status,
                'template': campaign.template.name,
                'start_date': campaign.created_at,
                'metrics': [
                    { "label": "Sent", "value": message_statuses.get('SENT', 0), "percentage": self.calculate_percentage(message_statuses, 'SENT', total_messages), "color": "#4338CA" },
                    { "label": "Queued", "value": message_statuses.get('PENDING', 0), "percentage": self.calculate_percentage(message_statuses, 'PENDING', total_messages), "color": "#6366F1" },
                    { "label": "Delivered", "value": message_statuses.get('DELIVERED', 0), "percentage": self.calculate_percentage(message_statuses, 'DELIVERED', total_messages), "color": "#60A5FA" },
                    { "label": "Read", "value": message_statuses.get('READ', 0), "percentage": self.calculate_percentage(message_statuses, 'READ', total_messages), "color": "#34D399" },
                    # { "label": "Interaction", "value": 10, "percentage": 2.09, "color": "#10B981" },
                    { "label": "Failed", "value": message_statuses.get('FAILED', 0), "percentage": self.calculate_percentage(message_statuses, 'FAILED', total_messages), "color": "#EF4444" }
                ],
                "additionalInfo": [
                    { "label": "Category", "value": campaign.template.category, "bgColor": "bg-pink-100" },
                    { "label": "Template", "value": campaign.template.template_type, "bgColor": "bg-green-100" },
                    { "label": "Total Count", "value": str(total_messages), "bgColor": "bg-blue-100" },
                    { "label": "Budget", "value": str(campaign.budget), "bgColor": "bg-green-100" },
                    { "label": "Start on", "value": campaign.template.created_at },
                    { "label": "Ended on", "value": campaign.template.created_at }
                ],
                "responseCount": 2,
                "performanceTrend": [
                    { "date": "2023-11-24", "value": 100 },
                    { "date": "2023-11-25", "value": 250 },
                    { "date": "2023-11-26", "value": 380 },
                    { "date": "2023-11-27", "value": 420 }
                ]
            }
            statistics.append(data)
        
        return Response(statistics)