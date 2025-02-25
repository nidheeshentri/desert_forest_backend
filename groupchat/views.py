from django.shortcuts import render



def index(request):
    return render(request, "groupchat/index.html")


def room(request, room_name):
    return render(request, "groupchat/room.html", {"room_name": room_name})