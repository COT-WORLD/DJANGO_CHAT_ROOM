import os
import pytest
import dj_database_url


@pytest.fixture(scope="session")
def django_db_setup():
    from django.conf import settings

    test_db_url = os.environ.get(
        "EXTERNAL_DATABASE_TEST_URL",
        ""
    )

    parsed_db = dj_database_url.parse(test_db_url)

    settings.DATABASES["default"] = {
        **parsed_db,
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
        "OPTIONS": {},
        "TIME_ZONE": None,
        "TEST": {
            "NAME": None,
            "CHARSET": None,
            "COLLATION": None,
            "MIRROR": None,
        },
    }
