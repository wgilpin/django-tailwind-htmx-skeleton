""" API views for the doofer app. """

# pylint: disable=no-member

from rest_framework.response import Response

from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login, logout

from doofer.api.serializers import NoteSerializer
from doofer.models import Note


@api_view(["GET"])
def get_notes(request):
    """Get all notes for current user"""
    notes = Note.objects.filter(user=request.user.id)
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
def note_detail(request, id_):
    """Get or update a note"""
    try:
        note = Note.objects.get(id=id_)
    except Note.DoesNotExist:
        return Response(status=404)
    if request.method == "GET":
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    serialiser = NoteSerializer(note, data=request.data)
    if serialiser.is_valid():
        serialiser.save()
        return Response(serialiser.data, status=201)
    return Response(serialiser.errors, status=400)


@api_view(["POST"])
def note_create(request):
    """create note"""
    serialiser = NoteSerializer(data=request.data)
    if serialiser.is_valid():
        serialiser.save()
        return Response(serialiser.data, status=201)
    return Response(serialiser.errors, status=400)


@api_view(["POST"])
def auth_login(request):
    """login the user given username and password"""
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        print("User logged in to API")

        # Return success response
        return Response({"message": "Login successful"}, status=200)
    else:
        # Return error response
        return Response({"message": "Invalid credentials"}, status=401)
