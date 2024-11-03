import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    ShowTheme
)
from planetarium.serializers import (AstronomyShowListSerializer,
                                     AstronomyShowDetailSerializer)

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def sample_astronomy_show(**params):
    defaults = {
        "title": "Sample Astronomy Show",
        "description": "Sample Description",
    }
    defaults.update(params)
    return AstronomyShow.objects.create(**defaults)


def sample_show_session(**params):
    planetarium_dome = PlanetariumDome.objects.create(
        name="Celestial Vault", rows=20, seats_in_row=20
    )

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "astronomy_show": None,
        "planetarium_dome": planetarium_dome,
    }
    defaults.update(params)

    return ShowSession.objects.create(**defaults)


def image_upload_url(astronomy_show_id):
    return reverse(
        "planetarium:astronomyshow-upload-image",
        args=[astronomy_show_id]
    )


def detail_url(astronomy_show_id):
    return reverse(
        "planetarium:astronomyshow-detail",
        args=[astronomy_show_id]
    )


class UnauthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_astronomy_shows(self):
        sample_astronomy_show()
        res = self.client.get(ASTRONOMY_SHOW_URL)

        astronomy_shows = AstronomyShow.objects.order_by("id")
        serializer = AstronomyShowListSerializer(astronomy_shows, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_astronomy_shows_by_themes(self):
        theme1 = ShowTheme.objects.create(name="Theme 1")
        theme2 = ShowTheme.objects.create(name="Theme 2")

        astronomy_show1 = sample_astronomy_show(title="Astronomy Show 1")
        astronomy_show2 = sample_astronomy_show(title="Astronomy Show 2")

        astronomy_show1.themes.add(theme1)
        astronomy_show2.themes.add(theme2)

        astronomy_show3 = sample_astronomy_show(
            title="Astronomy Show without themes"
        )

        res = self.client.get(
            ASTRONOMY_SHOW_URL, {"themes": f"{theme1.id},{theme2.id}"}
        )

        serializer1 = AstronomyShowListSerializer(astronomy_show1)
        serializer2 = AstronomyShowListSerializer(astronomy_show2)
        serializer3 = AstronomyShowListSerializer(astronomy_show3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_astronomy_show_by_title(self):
        astronomy_show1 = sample_astronomy_show(title="Astronomy Show 1")
        astronomy_show2 = sample_astronomy_show(title="Astronomy Show 2")
        astronomy_show3 = sample_astronomy_show(title="No data")

        res = self.client.get(ASTRONOMY_SHOW_URL, {"title": "astronomy show"})

        serializer1 = AstronomyShowListSerializer(astronomy_show1)
        serializer2 = AstronomyShowListSerializer(astronomy_show2)
        serializer3 = AstronomyShowListSerializer(astronomy_show3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_retrieve_astronomy_show_detail(self):
        astronomy_show = sample_astronomy_show()
        astronomy_show.themes.add(ShowTheme.objects.create(name="Show Theme"))

        url = detail_url(astronomy_show.id)
        res = self.client.get(url)

        serializer = AstronomyShowDetailSerializer(astronomy_show)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_astronomy_show_forbidden(self):
        payload = {
            "title": "Astronomy Show",
            "description": "Description",
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_astronomy_show(self):
        payload = {
            "title": "Astronomy Show",
            "description": "Description",
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astronomy_show = AstronomyShow.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(astronomy_show, key))

    def test_create_astronomy_show_with_themes(self):
        theme1 = ShowTheme.objects.create(name="Black Holes")
        theme2 = ShowTheme.objects.create(name="Stars")
        payload = {
            "title": "Galaxy",
            "themes": [theme1.id, theme2.id],
            "description": "About stars and black holes"
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        astronomy_show = AstronomyShow.objects.get(id=res.data["id"])
        themes = astronomy_show.themes.all()
        self.assertEqual(themes.count(), 2)
        self.assertIn(theme1, themes)
        self.assertIn(theme2, themes)


class AstronomyShowImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.astronomy_show = sample_astronomy_show()
        self.show_session = sample_show_session(
            astronomy_show=self.astronomy_show
        )

    def tearDown(self):
        self.astronomy_show.image.delete()

    def test_upload_image_to_astronomy_show(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.astronomy_show.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.astronomy_show.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.astronomy_show.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_astronomy_show_list_should_not_work(self):
        url = ASTRONOMY_SHOW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "description": "Description",
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astronomy_show = AstronomyShow.objects.get(title="Title")
        self.assertFalse(astronomy_show.image)

    def test_image_url_is_shown_on_astronomy_show_detail(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.astronomy_show.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_astronomy_show_list(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        self.astronomy_show.refresh_from_db()

        res = self.client.get(ASTRONOMY_SHOW_URL)

        results = res.data.get("results", [])
        self.assertIn("image", results[0].keys())

    def test_put_astronomy_show_not_allowed(self):
        astronomy_show = sample_astronomy_show(title="Unique Show Title")
        url = detail_url(astronomy_show.id)

        res = self.client.put(url, {
            "title": "New Astronomy Show",
            "description": "New description",
        })

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        astronomy_show.refresh_from_db()
        self.assertEqual(astronomy_show.title, "Unique Show Title")
        self.assertNotEqual(astronomy_show.description, "New description")

    def test_delete_astronomy_show_not_allowed(self):
        astronomy_show = sample_astronomy_show(title="Unique Delete Test Show")
        url = detail_url(astronomy_show.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.assertTrue(AstronomyShow.objects.filter(
            id=astronomy_show.id).exists()
            )
