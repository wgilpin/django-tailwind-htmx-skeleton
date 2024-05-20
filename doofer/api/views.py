""" API views for the doofer app. """

# pylint: disable=no-member

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login, logout

from doofer.api.serializers import NoteSerializer
from doofer.models import Note


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_notes(request):
    """Get all notes for current user"""
    notes = Note.objects.filter(user=request.user.id)
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def note_detail(request, id_):
    """Get or update a note"""

    try:
        note = Note.objects.get(id=id_)
    except Note.DoesNotExist:
        return Response(status=404)
    if request.method == "DELETE":
        note.delete()
        return Response(status=204)
    if request.method == "GET":
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    # it's a PUT request
    serialiser = NoteSerializer(note, data=request.data)
    if serialiser.is_valid():
        serialiser.save()
        return Response(serialiser.data, status=200)
    return Response(serialiser.errors, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def note_create(request):
    """create note"""
    serialiser = NoteSerializer(data=request.data)
    if serialiser.is_valid():
        serialiser.save()
        return Response(serialiser.data, status=201)
    return Response(serialiser.errors, status=400)


@api_view(["POST"])
@permission_classes([AllowAny])
def auth_login(request):
    """login the user given username and password"""
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        print("User logged in to API")

        # Return success response
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"message": "Login successful", "key": token.key}, status=200)
    else:
        # Return error response
        return Response({"message": "Invalid credentials!"}, status=401)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_all(request):
    """Get all notes for current user"""
    # TODO: remove this debug code
    print(request.path)
    for key, value in request.headers.items():
        print(f"{key}: {value}")

    notes = Note.objects.all()
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)
