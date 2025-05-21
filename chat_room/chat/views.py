from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import logout
from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count
from django.db.models import Count, Prefetch
from chat.models import Room, Topic, Message, User
import bleach


def home_view(request):
    q = request.GET.get('q', '').strip()

    rooms = (
        Room.objects
        .filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
        .select_related('topic', 'host')
        .prefetch_related(
            Prefetch('participants', queryset=User.objects.only('id', 'username'))
        )
        .annotate(participant_count=Count('participants'))
        .only('id', 'name', 'description', 'topic_id', 'host_id', 'created_at').order_by('-created_at')[:8]
    )

    topics = (
        Topic.objects
        .annotate(room_count=Count('room'))
        .order_by('-room_count')[:5]
    )

    topics_count = Topic.objects.count()
    room_messages = (
        Message.objects
        .filter(Q(room__topic__name__icontains=q))
        .select_related('room', 'room__topic', 'user')
        .only('id', 'body', 'room_id', 'user_id', 'created_at')[:8]
    )

    context = {
        'rooms': rooms,
        'topics': topics,
        'topics_count': topics_count,
        'room_messages': room_messages,
    }
    return render(request, 'chat/home.html', context)


@login_required(login_url='account_login')
def room_view(request, pk):
    room = get_object_or_404(Room, id=pk)

    if request.method == "POST":
        if request.user.is_authenticated:
            body = request.POST.get('body')
            if body:
                allowed_tags = ['p', 'b', 'i', 'ul',
                                'ol', 'li', 'a', 'strong', 'em']
                allowed_attrs = {'a': ['href', 'title', 'rel']}
                sanitized_body = bleach.clean(
                    body, tags=allowed_tags, attributes=allowed_attrs)
                Message.objects.create(
                    user=request.user,
                    room=room,
                    body=sanitized_body
                )
                room.participants.add(request.user)
            return redirect('room', pk=room.id)

    messages = room.message_set.select_related(
        'user').all().order_by('created_at')

    participants = room.participants.all()

    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages,
        'participants': participants
    })


class CreateRoom(LoginRequiredMixin, View):
    model = Topic
    form_class = RoomForm()
    template_name = "chat/room_form.html"
    login_url = reverse_lazy('account_login')

    def get(self, request):
        topics = self.model.objects.all()
        form = self.form_class
        return render(request, self.template_name, {"form": form, "topics": topics})

    def post(self, request):
        topic, created = Topic.objects.get_or_create(
            name=request.POST.get('topic'))
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect("home")


class UpdateRoomView(LoginRequiredMixin, View):
    template_name = "chat/room_form.html"
    login_url = reverse_lazy('account_login')
    success_url = "/"

    def get(self, request, **kwargs):
        room = Room.objects.get(id=self.kwargs['pk'])
        if request.user != room.host:
            return HttpResponseForbidden("You aren't allowed to perform this operation!")
        topics = Topic.objects.all()
        form = RoomForm(instance=room)
        return render(request, self.template_name, {"form": form, "topics": topics, 'room': room})

    def post(self, request, **kwargs):
        room = Room.objects.get(id=self.kwargs['pk'])
        if request.user != room.host:
            return HttpResponseForbidden("You aren't allowed to perform this operation!")
        topic, created = Topic.objects.get_or_create(
            name=request.POST.get('topic'))
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        # exit()
        room.save()
        return redirect(self.success_url)


@login_required(login_url='account_login')
def delete_room(request, pk):
    room = get_object_or_404(Room, id=pk)
    if request.user != room.host:
        return HttpResponseForbidden("Cannot delete someone else's room")

    if request.method == "POST":
        room.delete()
        return redirect('home')


@login_required(login_url='account_login')
def delete_message(request, pk):
    message = get_object_or_404(Message, id=pk)
    if request.user != message.user:
        return HttpResponseForbidden("Cannot delete someone else's message")

    if request.method == "POST":
        room_id = message.room.id
        message.delete()
        return redirect('room', pk=room_id)


@login_required(login_url='account_login')
def user_profile_view(request, pk):
    user = get_object_or_404(
        User.objects.prefetch_related(
            Prefetch('message_set',
                     queryset=Message.objects.select_related('room')),
            Prefetch('room_set', queryset=Room.objects.select_related('topic'))
        ),
        id=pk
    )

    context = {
        'user': user,
        'room_messages': user.message_set.all()[:8],
        'rooms': user.room_set.annotate(participant_count=Count('participants')),
        'topics': Topic.objects.annotate(room_count=Count('room')).all()[:5],
        'topics_count': Topic.objects.count()
    }
    return render(request, 'chat/profile.html', context)


@login_required(login_url='account_login')
def update_user(request):
    user = request.user
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'chat/update-user.html', {'form': form})
    else:
        form = UserForm(instance=user)
    return render(request, 'chat/update-user.html', {'form': form})


def topics_page(request):
    q = request.GET.get("q", "")
    topics = Topic.objects.filter(name__icontains=q).annotate(
        room_count=Count('room')).order_by('-room_count')
    return render(request, "chat/topics.html", {"topics": topics})


def activity_page(request):
    room_messages = Message.objects.select_related('room', 'user').all()
    return render(request, 'chat/activity.html', {'room_messages': room_messages})


def logout_user(request):
    logout(request)
    return redirect('home')
