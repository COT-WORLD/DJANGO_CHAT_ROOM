from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import logout
from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm
from django.views.generic import ListView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class HomePageListView(ListView):
    template_name = "chat/home.html"
    model = Room

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get(
            "q") if self.request.GET.get("q") != None else ""
        context["rooms"] = Room.objects.filter(Q(topic__name__icontains=q) | Q(
            name__icontains=q) | Q(description__icontains=q))
        context["topics"] = Topic.objects.all()[0:5]
        context["topics_count"] = Topic.objects.all().count()
        context["room_messages"] = Message.objects.filter(
            Q(room__topic__name__icontains=q))
        return context

class RoomPageView(View):
    model = Room
    template_name = "chat/room.html"

    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        messages = room.message_set.all()
        participants = room.participants.all()
        return render(request, "chat/room.html", {"room": room, "messages": messages, "participants": participants})

    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

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
            return HttpResponseForbidden("You aren't allowed here!")
        topics = Topic.objects.all()
        form = RoomForm(instance=room)
        return render(request, self.template_name, {"form": form, "topics": topics, 'room': room})

    def post(self, request, **kwargs):
        room = Room.objects.get(id=self.kwargs['pk'])
        if request.user != room.host:
            return HttpResponseForbidden("You aren't allowed here!")
        topic, created = Topic.objects.get_or_create(
            name=request.POST.get('topic'))
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect(self.success_url)

class DeleteRoomView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = "chat/delete.html"
    context_object_name = "obj"
    success_url = "/"
    login_url = reverse_lazy('account_login')

    def delete(self, request):
        if self.get_object().host == request.user:
            self.get_object().delete()
            return redirect(self.success_url)
        else:
            HttpResponseForbidden("Can't delete other's room")

class DeleteMessageView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "chat/delete.html"
    context_object_name = "obj"
    success_url = "/"
    login_url = reverse_lazy('account_login')

    def delete(self, request):
        if self.get_object().user == request.user:
            self.get_object().delete()
            return redirect(self.success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's message")

class UserProfileListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "chat/profile.html"
    login_url = reverse_lazy('account_login')

    def get_context_data(self, **kwargs):
        context = super(UserProfileListView, self).get_context_data(**kwargs)
        user = User.objects.get(id=self.kwargs['pk'])
        context["user"] = user
        context["room_messages"] = user.message_set.all()
        context["rooms"] = user.room_set.all()
        context["topics"] = Topic.objects.all()[0:5]
        context["topics_count"] = Topic.objects.all().count()
        return context

class UpdateUser(LoginRequiredMixin, View):
    template_name = "chat/update-user.html"
    login_url = reverse_lazy('account_login')

    def get(self, request):
        user = request.user
        form = UserForm(instance=user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        user = request.user
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
        else:
            for error in form.errors:
                messages.error(request, form.errors[error])
            return redirect(request.path, messages)

class TopicsPage(ListView):
    template_name = "chat/topics.html"
    context_object_name = "topics"

    def get_queryset(self):
        self.topics = self.request.GET.get(
            "q") if self.request.GET.get("q") != None else ""
        return Topic.objects.filter(name__icontains=self.topics)

class ActivityPage(ListView):
    model = Message
    template_name = "chat/activity.html"
    context_object_name = "room_messages"

class LogoutUser(View):
    def get(self, request):
        logout(request)
        return redirect('home')