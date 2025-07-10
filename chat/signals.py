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
from dummy_text_generator import generate_sentence
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
        bio = generate_sentence(lang='en', topic=random.choice([
            "technology", "programming", "software development", "education"
        ]))
        User.objects.create_superuser(
            username=os.environ["DJANGO_SUPER_USER_USERNAME"],
            first_name=os.environ["DJANGO_SUPER_USER_USERNAME"],
            last_name=os.environ["DJANGO_SUPER_USER_USERNAME"],
            email=os.environ["DJANGO_SUPER_USER_EMAIL"],
            password=os.environ["DJANGO_SUPER_USER_PASSWORD"],
            bio=bio,
        )


def seed_initial_data():
    if Room.objects.exists():
        return  # Avoid reseeding if data exists

    print("🌱 Seeding users...")
    users = create_users()
    print("🌱 Seeding topics...")
    topics = create_topics()
    print("🏗 Creating rooms...")
    rooms = create_rooms(users, topics)
    print("💬 Creating messages...")
    add_messages_and_participants(rooms, users)
    print("✅ Seeding completed.")


def create_users():
    users = []
    for name in USER_NAMES:
        if not User.objects.filter(username=name.lower()).exists():
            bio = generate_sentence(lang='en', topic=random.choice([
                "technology", "programming", "software development", "education"
            ]))
            user = User.objects.create_user(
                username=name.lower(),
                first_name=name,
                last_name=name,
                email=f"{name.lower()}@gmail.com",
                password="password123"
            )
            user.bio = bio
            user.save()
            users.append(user)
        else:
            users.append(User.objects.get(username=name.lower()))
    return users


def create_topics():
    topic_objs = [Topic(name=name) for name in TOPIC_NAMES]
    Topic.objects.bulk_create(topic_objs, ignore_conflicts=True)
    return list(Topic.objects.all())


def create_rooms(users, topics):
    rooms = []
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
    # Return only newly created rooms
    return list(Room.objects.all())[-len(rooms):]


def add_messages_and_participants(rooms, users):
    through_model = Room.participants.through
    through_entries = []
    messages = []

    for room in rooms:
        # Always include the host as a participant and message writer
        participants = set([room.host])

        # Randomly select other users (excluding host) as message writers/participants
        num_other_participants = random.randint(2, 5)
        other_participants = random.sample(
            [u for u in users if u != room.host], k=num_other_participants
        )
        participants.update(other_participants)

        # Guarantee host writes at least one message
        host_message = generate_sentence(lang='en', topic=room.topic.name)
        messages.append(
            Message(user_id=room.host.id, room_id=room.id, body=host_message)
        )
        through_entries.append(
            through_model(user_id=room.host.id, room_id=room.id)
        )

        # Each other participant writes 1-3 messages
        for participant in other_participants:
            through_entries.append(
                through_model(user_id=participant.id, room_id=room.id)
            )
            num_messages = random.randint(1, 3)
            for _ in range(num_messages):
                message_body = generate_sentence(
                    lang='en', topic=room.topic.name)
                messages.append(
                    Message(user_id=participant.id,
                            room_id=room.id, body=message_body)
                )

    through_model.objects.bulk_create(through_entries, ignore_conflicts=True)
    Message.objects.bulk_create(messages)
