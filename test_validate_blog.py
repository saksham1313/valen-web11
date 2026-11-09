"""Regression coverage for daily reservations and explicitly requested additions."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

spec=spec_from_file_location('blog_validator',Path(__file__).with_name('validate-blog.py'))
validator=module_from_spec(spec)
spec.loader.exec_module(validator)

class PublishingLimitTests(unittest.TestCase):
    def setUp(self):
        self.daily={'date':'2026-11-09','slug':'daily','status':'published_verified'}
        self.extra={'date':'2026-11-09','slug':'extra','status':'prepared','publicationMode':'user_requested_additional','authorization':{'source':'explicit_user_request','date':'2026-11-09','reason':'User requested another article today.'}}

    def test_existing_daily_history_remains_valid(self):
        validator.validate_history([self.daily])

    def test_second_daily_reservation_is_rejected(self):
        duplicate={**self.daily,'slug':'second','status':'deployment_pending'}
        with self.assertRaisesRegex(AssertionError,'Multiple daily'):
            validator.validate_history([self.daily,duplicate])

    def test_explicit_extra_is_accepted(self):
        validator.validate_history([self.daily,self.extra])

    def test_extra_without_explicit_authorization_is_rejected(self):
        self.extra.pop('authorization')
        with self.assertRaisesRegex(AssertionError,'explicit user authorization'):
            validator.validate_history([self.daily,self.extra])

    def test_authorization_for_another_date_is_rejected(self):
        self.extra['authorization']['date']='2026-11-08'
        with self.assertRaisesRegex(AssertionError,'match its IST date'):
            validator.validate_history([self.daily,self.extra])

    def test_second_extra_is_rejected(self):
        another={**deepcopy(self.extra),'slug':'third'}
        with self.assertRaisesRegex(AssertionError,'Multiple extra'):
            validator.validate_history([self.daily,self.extra,another])

    def test_duplicate_slug_is_always_rejected(self):
        self.extra['slug']='daily'
        with self.assertRaisesRegex(AssertionError,'Duplicate slug'):
            validator.validate_history([self.daily,self.extra])

    def test_extra_does_not_replace_daily_publication(self):
        with self.assertRaisesRegex(AssertionError,'follow an existing daily'):
            validator.validate_history([self.extra])

    def test_failed_daily_attempt_can_be_retried(self):
        failed={**self.daily,'slug':'failed','status':'failed'}
        validator.validate_history([failed,self.daily])

    def test_unknown_mode_cannot_skip_daily_limit(self):
        self.extra['publicationMode']='skip'
        with self.assertRaisesRegex(AssertionError,'Unknown publication mode'):
            validator.validate_history([self.daily,self.extra])

if __name__=='__main__':
    unittest.main()
