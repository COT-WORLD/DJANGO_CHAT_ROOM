from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from chat.models import Topic, Room, Message
from faker import Faker
import os
import random
from django.contrib.auth import get_user_model

fake = Faker()
User = get_user_model()

TOPIC_NAMES = [
    "Artificial Intelligence", "Machine Learning", "Web Development", "APIs",
    "Cloud Computing", "Databases", "Cybersecurity", "DevOps", "Python", "JavaScript"
]

USER_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ivan", "Jasmine"
]


@receiver(post_migrate)
def initialize_project_data(sender, **kwargs):
    setup_google_social_app_and_superuser()
    seed_initial_data()


def setup_google_social_app_and_superuser():

    domain = os.environ.get("APP_DOMAIN", "localhost:8000")
    site, _ = Site.objects.get_or_create(
        id=settings.SITE_ID,
        defaults={"domain": domain, "name": "Localhost"}
    )

    if not settings.SOCIALACCOUNT_PROVIDERS.get("google"):
        return

    existing_apps = SocialApp.objects.filter(provider="google", sites=site)
    if existing_apps.exists():
        return

    google_app = SocialApp.objects.create(
        provider="google",
        name="Google",
        client_id=os.environ["CLIENT_ID"],
        secret=os.environ["CLIENT_SECRET"],
    )
    google_app.sites.add(site)
    print("✅ Google SocialApp created and linked to site.")

    # Create superuser if not exists
    if not User.objects.filter(email=os.environ["DJANGO_SUPER_USER_EMAIL"]).exists():
        User.objects.create_superuser(
            username=os.environ["DJANGO_SUPER_USER_USERNAME"],
            email=os.environ["DJANGO_SUPER_USER_EMAIL"],
            password=os.environ["DJANGO_SUPER_USER_PASSWORD"],
        )


def seed_initial_data():
    if Room.objects.exists():
        return  # Avoid reseeding if data exists

    print("🌱 Seeding users...")
    users = create_users()
    print("🌱 Seeding topics...")
    topics = create_topics()
    print("🏗 Creating rooms...")
    rooms, room_participant_map = create_rooms(users, topics)
    print("💬 Creating messages...")
    create_messages(room_participant_map)
    print("✅ Seeding completed.")


def create_users():
    users = []
    for name in USER_NAMES:
        if not User.objects.filter(username=name.lower()).exists():
            user = User.objects.create_user(
                username=name.lower(),
                first_name=name,
                email=f"{name.lower()}@gmail.com",
                password="password123"
            )
            user.bio = fake.sentence()
            user.save()
            users.append(user)
    return users


def create_topics():
    topic_objs = [Topic(name=name) for name in TOPIC_NAMES]
    Topic.objects.bulk_create(topic_objs, ignore_conflicts=True)
    return list(Topic.objects.all())


def create_rooms(users, topics):
    rooms = []
    room_participant_map = {}

    for i, user in enumerate(users):
        topic = random.choice(topics)
        room = Room(
            host=user,
            topic=topic,
            name=f"{topic.name} Discussion {i}",
            description=f"Discussion on {topic.name.lower()} and its applications.",
        )
        rooms.append(room)

    Room.objects.bulk_create(rooms)
    created_rooms = list(Room.objects.all())[-len(rooms):]

    through_model = Room.participants.through
    through_entries = []

    for room in created_rooms:
        host = room.host
        participants = random.sample(
            [u for u in users if u.id != host.id], k=random.randint(2, 5)
        )
        full_participants = participants + [host]
        room_participant_map[room.id] = full_participants

        for user in full_participants:
            through_entries.append(through_model(
                user_id=user.id, room_id=room.id))

    through_model.objects.bulk_create(through_entries)
    return created_rooms, room_participant_map


def create_messages(room_participant_map):
    messages = []
    through_model = Room.participants.through
    extra_through_entries = []

    for room_id, participants in room_participant_map.items():
        for _ in range(random.randint(3, 7)):
            user = random.choice(participants)
            msg_body = fake.sentence(nb_words=15)
            tag = "(by room creator)" if user.id == participants[-1].id else "(by participant)"

            if not through_model.objects.filter(user_id=user.id, room_id=room_id).exists():
                extra_through_entries.append(
                    through_model(user_id=user.id, room_id=room_id)
                )
                room_participant_map[room_id].append(user)

            messages.append(
                Message(user_id=user.id, room_id=room_id,
                        body=f"{msg_body} {tag}")
            )

    through_model.objects.bulk_create(
        extra_through_entries, ignore_conflicts=True)
    Message.objects.bulk_create(messages)
