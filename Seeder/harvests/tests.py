import json
import os
import shutil
import tempfile
from hashlib import md5
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone

from source.constants import SOURCE_FREQUENCY_PER_YEAR
from harvests.cron import cleanup_expired_chunked_uploads
from harvests.scheduler import get_dates_for_timedelta
from harvests.models import Attachment, Harvest, TopicCollection
from harvests.views import INTERNAL_TC_CUSTOM_SEEDS_UPLOADS_SESSION_KEY
from chunked_upload.constants import COMPLETE
from chunked_upload.models import ChunkedUpload

TODAY = datetime.today()


class TopicCollectionTests(TestCase):
    def setUp(self):
        if User.objects.filter(username='pedro').count() == 0:
            User.objects.create_superuser('pedro', '', 'password')
        user = User.objects.get(username='pedro')
        self.c = Client()
        self.c.login(username='pedro', password='password')

        for i, freq in enumerate([['1'], ['2', '4'], ['6', '12'], ['4', '12']]):
            TopicCollection(pk=i, owner=user,
                            title_cs="CS TC {}".format(i + 1),
                            title_en="EN TC {}".format(i + 1),
                            scheduled_on=TODAY, all_open=True,
                            target_frequency=freq).save()
        Harvest(status=Harvest.STATE_PLANNED, title="Harvest 1",
                scheduled_on=TODAY, topic_collection_frequency=['4']).save()

    def test_topic_collections_appear_in_harvest_urls(self):
        url = reverse('harvests:shortcut_urls_by_date',
                      kwargs={'h_date': TODAY})
        res = self.c.get(url)
        content = res.content.decode('utf-8')
        self.assertIn("TT-cs-tc-2", content)
        self.assertIn("TT-cs-tc-4", content)
        self.assertNotIn("TT-cs-tc-1", content)
        self.assertNotIn("TT-cs-tc-3", content)

    def test_topic_collections_accessible_from_harvest_urls(self):
        url = reverse('harvests:shortcut_urls_by_date',
                      kwargs={'h_date': TODAY})
        res = self.c.get(url)
        urls = [u.rstrip('<br>')
                for u in res.content.decode('utf-8').splitlines()
                if len(u) > 0]
        for url in urls:
            r = self.c.get(url)
            self.assertEqual(200, r.status_code)


class HarvestUrlTest(TestCase):

    DATE = datetime.today()
    GENERATE_FREQUENCIES = [
        ['0'], ['1'], ['2'], ['4'], ['6'], ['12'], ['52'], ['365'],
        ['2', '4'],
        ['6', '12'],
        ['1', '365'],
    ]

    def setUp(self):
        User.objects.create_user('pedro', 'pedro@seeder.com', 'password')
        self.c = Client()
        self.c.login(username='pedro', password='password')
        # Topic collections
        self.topic_collections = [
            TopicCollection(title_cs="CS Topic C {}".format(i + 1),
                            title_en="EN Topic C {}".format(i + 1),
                            owner=User.objects.get(username='pedro'),
                            scheduled_on=self.DATE,
                            all_open=True,)
            for i in range(5)
        ]
        for tc in self.topic_collections:
            tc.save()
        # Various different frequencies and frequency combinations
        self.harvests = [
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest {}".format(i + 1),
                    scheduled_on=self.DATE,
                    target_frequency=freq)
            for i, freq in enumerate(self.GENERATE_FREQUENCIES)
        ]
        # Simple harvests on different dates, shouldn't be returned
        self.harvests.extend([
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest (diff. day) {}".format(i + 1),
                    scheduled_on=self.DATE + timedelta(days=i),
                    target_frequency=['1'])
            for i in (-3, -1, 1, 3)
        ])
        # Fewer harvests on a different date, primarily for url testing
        self.harvests.extend([
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest (other) {}".format(i + 1),
                    scheduled_on=self.DATE + timedelta(weeks=4),
                    target_frequency=freq)
            for i, freq in enumerate(self.GENERATE_FREQUENCIES[2:6])
        ])
        # Harvests with topic collections
        self.tt_harvests = [
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest (TC) {}".format(i + 1),
                    scheduled_on=self.DATE + timedelta(weeks=1),
                    target_frequency=freq)
            for i, freq in enumerate(self.GENERATE_FREQUENCIES[:5])
        ]
        for i, h in enumerate(self.tt_harvests):
            h.save()
            h.topic_collections.add(self.topic_collections[i])
            h.save()
        for h in self.harvests:
            h.save()

    def test_url_dates_do_match(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE,
            'shortcut': 'V1',
        })
        res = self.c.get(get_url)
        self.assertNotEqual(404, res.status_code)
        self.assertEqual(200, res.status_code)

    def test_url_dates_do_not_match(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE + timedelta(days=1),
            'shortcut': 'V1',
        })
        res = self.c.get(get_url)
        self.assertEqual(404, res.status_code)

    def test_url_valid_shortcuts(self):
        shortcuts = (
            'V1', 'V2', 'V4', 'V6', 'V12', 'V52', 'V365',
            'ArchiveIt', 'VNC', 'Tests', 'Totals', 'OneShot')
        # TODO + TT-...
        for shortcut in shortcuts:
            get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(200, res.status_code)

    def test_url_invalid_shortcuts(self):
        shortcuts = (
            'V0M', 'V1M', 'V12M', 'V3', 'V11', 'Archiveit', 'archiveit', 'vnc',
            'tests', 'totals', 'oneshot', 'TT', 'tt', 'TT-', 'tt-', '12345')
        for shortcut in shortcuts:
            get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(404, res.status_code)

    def test_harvest_urls(self, h_date=DATE):
        get_url = reverse('harvests:shortcut_urls_by_date', kwargs={
            'h_date': h_date,
        })
        res = self.c.get(get_url)
        self.assertEqual(200, res.status_code)
        urls = res.context['urls']

        harvest_ids = []
        # Try accessing all the returned urls
        for url in urls:
            r = self.c.get(url)
            self.assertEqual(200, r.status_code)
            harvest_ids.extend(r.context['harvest_ids'])
        # Make sure all harvests for that date appear
        correct_harvest_ids = [
            h.pk for h in Harvest.objects.filter(scheduled_on=h_date)
        ]
        self.assertListEqual(sorted(correct_harvest_ids),
                             sorted(set(harvest_ids)))
        return res

    def test_harvest_urls_other(self):
        res = self.test_harvest_urls(h_date=self.DATE + timedelta(weeks=4))
        self.assertNotEqual(0, len(res.context['urls']))

    def test_harvest_urls_with_tts(self):
        res = self.test_harvest_urls(h_date=self.DATE + timedelta(weeks=1))
        self.assertNotEqual(0, len(res.context['urls']))

    def test_harvest_urls_no_harvests(self):
        res = self.test_harvest_urls(h_date=self.DATE + timedelta(days=-365))
        self.assertEqual(0, len(res.context['urls']))

    def test_harvests_by_frequency(self):
        for freq, _ in SOURCE_FREQUENCY_PER_YEAR:
            # 'V0' is not valid
            if freq == 0:
                continue
            shortcut = 'V{:d}'.format(freq)
            get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(200, res.status_code)
            harvest_ids = res.context['harvest_ids']
            harvests = Harvest.objects.filter(pk__in=harvest_ids)
            for h in harvests:
                self.assertEqual(self.DATE, h.scheduled_on)
                self.assertTrue(str(freq) in h.target_frequency)

    def test_harvests_with_tts(self):
        # TODO: fails now but TT-{slug} will be deprecated with #593
        for h in self.tt_harvests:
            shortcut = 'TT-{}'.format(h.topic_collections.all()[0].slug)
            get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': h.scheduled_on,
                'h_date2': h.scheduled_on,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(200, res.status_code)
            harvest_ids = res.context['harvest_ids']
            self.assertIn(h.pk, harvest_ids)

    def test_harvests_totals(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE,
            'shortcut': 'Totals',
        })
        res = self.c.get(get_url)
        self.assertEqual(200, res.status_code)
        harvest_ids = res.context['harvest_ids']
        correct_harvest_ids = [
            h.pk for h in Harvest.objects.filter(scheduled_on=self.DATE)
        ]
        self.assertListEqual(correct_harvest_ids, harvest_ids)

    def test_harvests_totals_no_harvests(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE + timedelta(days=-365),
            'h_date2': self.DATE + timedelta(days=-365),
            'shortcut': 'Totals',
        })
        res = self.c.get(get_url)
        self.assertEqual(200, res.status_code)
        self.assertListEqual([], res.context['harvest_ids'])
        self.assertListEqual([], res.context['urls'])

    def test_harvests_oneshot(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE,
            'shortcut': 'OneShot',
        })
        res = self.c.get(get_url)
        self.assertEqual(200, res.status_code)
        harvest_ids = res.context['harvest_ids']
        harvests = Harvest.objects.filter(pk__in=harvest_ids)
        for h in harvests:
            self.assertEqual(self.DATE, h.scheduled_on)
            self.assertTrue('0' in h.target_frequency)


@override_settings(CHUNKED_UPLOAD_MAX_BYTES=524288000)
class InternalTopicCollectionChunkedUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('pedro', '', 'password')
        self.c = Client()
        self.c.login(username='pedro', password='password')
        self.topic = TopicCollection.objects.order_by("pk").first()
        if not self.topic:
            self.topic = TopicCollection(owner=self.user)
        self.topic.owner = self.user
        self.topic.title_cs = "Chunk upload topic cs"
        self.topic.title_en = "Chunk upload topic en"
        self.topic.annotation_cs = "annotation cs"
        self.topic.annotation_en = "annotation en"
        self.topic.custom_seeds = "https://old.example.com\n"
        self.topic.all_open = True
        self.topic.save()

        self.media_root = tempfile.mkdtemp(prefix="seeder-test-media-")
        self.override_media = override_settings(MEDIA_ROOT=self.media_root)
        self.override_media.enable()
        self.addCleanup(self.override_media.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

    def _chunk_upload_url(self):
        return reverse(
            "harvests:internal_collection_custom_seeds_chunk_upload",
            kwargs={"pk": self.topic.pk},
        )

    def _chunk_complete_url(self):
        return reverse(
            "harvests:internal_collection_custom_seeds_chunk_complete",
            kwargs={"pk": self.topic.pk},
        )

    def _edit_url(self):
        return reverse(
            "harvests:internal_collection_edit",
            kwargs={"pk": self.topic.pk},
        )

    def _post_chunk(
            self, content, filename="custom-seeds.txt", content_type="text/plain",
            total=None, upload_id=None):
        total_bytes = total if total is not None else len(content)
        data = {
            "file": SimpleUploadedFile(filename, content, content_type=content_type),
            "filename": filename,
            "offset": "0",
        }
        if upload_id:
            data["upload_id"] = upload_id
        return self.c.post(
            self._chunk_upload_url(),
            data,
            HTTP_CONTENT_RANGE=f"bytes 0-{len(content) - 1}/{total_bytes}",
        )

    def _complete_upload(self, upload_id, md5_hex):
        return self.c.post(
            self._chunk_complete_url(),
            data={"upload_id": upload_id, "md5": md5_hex},
        )

    def _edit_payload(self, **kwargs):
        payload = {
            "owner": str(self.user.pk),
            "collection_alias": self.topic.collection_alias or "",
            "title_cs": self.topic.title_cs,
            "title_en": self.topic.title_en,
            "annotation_cs": self.topic.annotation_cs,
            "annotation_en": self.topic.annotation_en,
            "date_from": self.topic.date_from.strftime("%Y-%m-%d"),
            "date_to": "",
            "aggregation_with_same_type": "on",
            "all_open": "on",
            "target_frequency": [],
            "custom_seeds": self.topic.custom_seeds or "",
            "custom_sources": [],
            "files_to_delete": [],
            "custom_seeds_upload_id": "",
        }
        payload.update(kwargs)
        return payload

    def test_chunk_upload_happy_path(self):
        content = b"https://example.com\nhttps://example.org\n"
        response = self._post_chunk(content)
        self.assertEqual(200, response.status_code)
        payload = json.loads(response.content.decode("utf-8"))
        upload_id = payload["upload_id"]
        self.assertTrue(upload_id)
        self.assertEqual(len(content), payload["offset"])

        complete = self._complete_upload(upload_id, md5(content).hexdigest())
        self.assertEqual(200, complete.status_code)
        chunked_upload = ChunkedUpload.objects.get(upload_id=upload_id)
        self.assertEqual(COMPLETE, chunked_upload.status)

    def test_unauthenticated_upload_is_denied(self):
        anon = Client()
        response = anon.post(
            self._chunk_upload_url(),
            data={
                "file": SimpleUploadedFile(
                    "custom-seeds.txt", b"https://example.com\n",
                    content_type="text/plain"),
                "filename": "custom-seeds.txt",
                "offset": "0",
            },
            HTTP_CONTENT_RANGE="bytes 0-19/20",
        )
        self.assertEqual(302, response.status_code)
        self.assertIn("/seeder/auth/login/", response.url)

    def test_invalid_extension_is_rejected(self):
        response = self._post_chunk(
            b"https://example.com\n",
            filename="custom-seeds.csv",
            content_type="text/plain",
        )
        self.assertEqual(400, response.status_code)
        payload = json.loads(response.content.decode("utf-8"))
        self.assertIn("Only .txt files are allowed", payload["detail"])

    def test_too_large_upload_is_rejected(self):
        response = self._post_chunk(
            b"https://example.com\n",
            total=524288001,
        )
        self.assertEqual(400, response.status_code)
        payload = json.loads(response.content.decode("utf-8"))
        self.assertIn("Size of file exceeds the limit", payload["detail"])

    def test_checksum_mismatch_is_rejected(self):
        content = b"https://example.com\n"
        response = self._post_chunk(content)
        self.assertEqual(200, response.status_code)
        upload_id = json.loads(response.content.decode("utf-8"))["upload_id"]

        complete = self._complete_upload(upload_id, "wrong-md5")
        self.assertEqual(400, complete.status_code)
        payload = json.loads(complete.content.decode("utf-8"))
        self.assertIn("md5 checksum does not match", payload["detail"])

    def test_form_submit_with_valid_upload_replaces_custom_seeds(self):
        new_seeds = b"https://new.example.com\nhttps://newer.example.com\n"
        upload = self._post_chunk(new_seeds)
        upload_id = json.loads(upload.content.decode("utf-8"))["upload_id"]
        self._complete_upload(upload_id, md5(new_seeds).hexdigest())

        response = self.c.post(
            self._edit_url(),
            data=self._edit_payload(custom_seeds_upload_id=upload_id),
        )
        self.assertEqual(302, response.status_code)

        self.topic.refresh_from_db()
        self.assertEqual(new_seeds.decode("utf-8"), self.topic.custom_seeds)
        self.assertFalse(ChunkedUpload.objects.filter(upload_id=upload_id).exists())

        backup_dir = os.path.join(self.media_root, "seeds", "backup")
        self.assertTrue(os.path.isdir(backup_dir))
        self.assertTrue(os.listdir(backup_dir))

    def test_upload_submit_invalidates_stale_frozen_cache(self):
        self.topic.seeds_frozen = "https://old.example.com"
        self.topic.save(update_fields=["seeds_frozen"])

        new_seeds = b"https://new1.example.com\nhttps://new2.example.com\n"
        upload = self._post_chunk(new_seeds)
        upload_id = json.loads(upload.content.decode("utf-8"))["upload_id"]
        self._complete_upload(upload_id, md5(new_seeds).hexdigest())

        response = self.c.post(
            self._edit_url(),
            data=self._edit_payload(custom_seeds_upload_id=upload_id),
        )
        self.assertEqual(302, response.status_code)

        self.topic.refresh_from_db()
        self.assertEqual("", self.topic.seeds_frozen)
        self.assertSetEqual(
            {"https://new1.example.com", "https://new2.example.com"},
            self.topic.get_seeds(),
        )

    def test_invalid_upload_id_does_not_apply_other_changes(self):
        attachment = Attachment.objects.create(
            topic_collection=self.topic,
            file=SimpleUploadedFile(
                "keep.txt", b"keep me", content_type="text/plain"),
        )

        old_title = self.topic.title_cs
        response = self.c.post(
            self._edit_url(),
            data=self._edit_payload(
                title_cs="Should not persist",
                files_to_delete=[str(attachment.pk)],
                custom_seeds_upload_id="missing-upload",
            ),
        )
        self.assertEqual(302, response.status_code)

        self.topic.refresh_from_db()
        self.assertEqual(old_title, self.topic.title_cs)
        self.assertTrue(Attachment.objects.filter(pk=attachment.pk).exists())

    def test_consumed_upload_cannot_be_reused(self):
        new_seeds = b"https://new.example.com\n"
        upload = self._post_chunk(new_seeds)
        upload_id = json.loads(upload.content.decode("utf-8"))["upload_id"]
        self._complete_upload(upload_id, md5(new_seeds).hexdigest())

        first = self.c.post(
            self._edit_url(),
            data=self._edit_payload(custom_seeds_upload_id=upload_id),
        )
        self.assertEqual(302, first.status_code)

        original_title = self.topic.title_cs
        second = self.c.post(
            self._edit_url(),
            data=self._edit_payload(
                title_cs="Should not save on reuse",
                custom_seeds_upload_id=upload_id,
            ),
        )
        self.assertEqual(302, second.status_code)

        self.topic.refresh_from_db()
        self.assertEqual(original_title, self.topic.title_cs)

    def test_backup_filename_is_sanitized(self):
        self.topic.title_cs = "../../unsafe title"
        self.topic.title_en = "../../unsafe title"
        self.topic.save(update_fields=["title_cs", "title_en"])

        backup_url = self.topic.backup_custom_seeds()
        self.assertNotIn("..", backup_url)

        backup_dir = os.path.abspath(os.path.join(
            self.media_root, "seeds", "backup"))
        backup_files = os.listdir(backup_dir)
        self.assertTrue(backup_files)

        backup_path = os.path.abspath(os.path.join(backup_dir, backup_files[0]))
        self.assertEqual(
            backup_dir, os.path.commonpath([backup_dir, backup_path]))

    def test_starting_new_upload_prunes_old_topic_uploads_in_session(self):
        first_content = b"https://one.example.com\n"
        first_upload = self._post_chunk(first_content)
        first_upload_id = json.loads(first_upload.content.decode("utf-8"))[
            "upload_id"]

        second_content = b"https://two.example.com\n"
        second_upload = self._post_chunk(second_content)
        second_upload_id = json.loads(second_upload.content.decode("utf-8"))[
            "upload_id"]

        self.assertNotEqual(first_upload_id, second_upload_id)
        self.assertFalse(
            ChunkedUpload.objects.filter(upload_id=first_upload_id).exists()
        )
        self.assertTrue(
            ChunkedUpload.objects.filter(upload_id=second_upload_id).exists()
        )

        bindings = self.c.session.get(
            INTERNAL_TC_CUSTOM_SEEDS_UPLOADS_SESSION_KEY, {})
        self.assertNotIn(first_upload_id, bindings)
        self.assertIn(second_upload_id, bindings)

    def test_cleanup_expired_chunked_uploads_removes_old_files(self):
        old_content = b"https://old.example.com\n"
        old_upload = ChunkedUpload.objects.create(
            user=self.user,
            filename="old.txt",
            file=SimpleUploadedFile(
                "old.txt", old_content, content_type="text/plain"),
            offset=len(old_content),
            status=COMPLETE,
        )
        old_upload_id = old_upload.upload_id
        old_file_path = old_upload.file.path
        old_created = timezone.now() - timedelta(days=2)
        ChunkedUpload.objects.filter(pk=old_upload.pk).update(
            created_on=old_created)

        fresh_content = b"https://fresh.example.com\n"
        fresh_upload = ChunkedUpload.objects.create(
            user=self.user,
            filename="fresh.txt",
            file=SimpleUploadedFile(
                "fresh.txt", fresh_content, content_type="text/plain"),
            offset=len(fresh_content),
            status=COMPLETE,
        )
        fresh_upload_id = fresh_upload.upload_id

        self.assertTrue(os.path.exists(old_file_path))
        cleanup_expired_chunked_uploads()

        self.assertFalse(
            ChunkedUpload.objects.filter(upload_id=old_upload_id).exists()
        )
        self.assertFalse(os.path.exists(old_file_path))
        self.assertTrue(
            ChunkedUpload.objects.filter(upload_id=fresh_upload_id).exists()
        )
        self.assertTrue(os.path.exists(fresh_upload.file.path))

    def test_form_submit_with_upload_also_saves_other_changes(self):
        new_seeds = b"https://new.example.com\n"
        upload = self._post_chunk(new_seeds)
        upload_id = json.loads(upload.content.decode("utf-8"))["upload_id"]
        self._complete_upload(upload_id, md5(new_seeds).hexdigest())

        response = self.c.post(
            self._edit_url(),
            data=self._edit_payload(
                custom_seeds_upload_id=upload_id,
                title_cs="Changed title while importing",
            ),
        )
        self.assertEqual(302, response.status_code)

        self.topic.refresh_from_db()
        self.assertEqual("Changed title while importing", self.topic.title_cs)
        self.assertEqual(new_seeds.decode("utf-8"), self.topic.custom_seeds)

    def test_decode_error_preserves_custom_seeds(self):
        old_custom_seeds = self.topic.custom_seeds
        binary_data = b"\xff\xfe\xfd\xfc"
        upload = self._post_chunk(binary_data)
        upload_id = json.loads(upload.content.decode("utf-8"))["upload_id"]
        self._complete_upload(upload_id, md5(binary_data).hexdigest())

        response = self.c.post(
            self._edit_url(),
            data=self._edit_payload(custom_seeds_upload_id=upload_id),
        )
        self.assertEqual(302, response.status_code)

        self.topic.refresh_from_db()
        self.assertEqual(old_custom_seeds, self.topic.custom_seeds)
        self.assertTrue(ChunkedUpload.objects.filter(upload_id=upload_id).exists())

    def test_edit_without_upload_keeps_existing_behavior(self):
        self.topic.custom_seeds = "x" * (1000 * 1000 + 10)
        self.topic.save(update_fields=["custom_seeds"])

        response = self.c.post(
            self._edit_url(),
            data=self._edit_payload(
                title_cs="Chunk upload topic cs edited",
                custom_seeds_upload_id="",
            ),
        )
        self.assertEqual(302, response.status_code)
        self.topic.refresh_from_db()
        self.assertEqual("Chunk upload topic cs edited", self.topic.title_cs)

    def test_edit_without_changes_skips_save_for_large_custom_seeds(self):
        self.topic.custom_seeds = "x" * (1000 * 1000 + 10)
        self.topic.seeds_frozen = "https://frozen.example.com"
        self.topic.save(update_fields=["custom_seeds", "seeds_frozen"])
        self.topic.refresh_from_db()
        old_last_changed = self.topic.last_changed
        old_seeds_frozen = self.topic.seeds_frozen

        response = self.c.post(
            self._edit_url(),
            data=self._edit_payload(custom_seeds_upload_id=""),
        )
        self.assertEqual(302, response.status_code)

        self.topic.refresh_from_db()
        self.assertEqual(old_last_changed, self.topic.last_changed)
        self.assertEqual(old_seeds_frozen, self.topic.seeds_frozen)


class ScheduleTest(TestCase):
    """
    Tests scheduling functionality
    """

    def test_timedelta_scheduler(self):
        scheduled = get_dates_for_timedelta(
            timedelta(days=10),
            datetime(2012, 1, 1),
            datetime(2012, 1, 22)
        )
        self.assertEqual(
            scheduled,
            [
                datetime(2012, 1, 1),
                datetime(2012, 1, 11),
                datetime(2012, 1, 21)
            ]
        )
