"""
Tests for the student model, which contains our user logic
"""
import logging

from django.test import TestCase
from mock import Mock, patch

from student.models import unique_id_for_user
from student.views import process_survey_link, _cert_info
from django.contrib.auth.models import User
from comment_client.utils import settings
from django.test.utils import override_settings

COURSE_1 = 'edX/toy/2012_Fall'
COURSE_2 = 'edx/full/6.002_Spring_2012'

log = logging.getLogger(__name__)


@override_settings(MITX_FEATURES={'ENABLE_DISCUSSION_SERVICE': True})
class DiscussionServiceUserTest(TestCase):
    """
    Test that saving a user also sends the info to the
    discussion service aka comment_client aka forum
    """
    @patch('comment_client.utils.requests')
    def test_update_user_information2(self, mock_requests):
        prefix = settings.PREFIX
        api_key = settings.API_KEY
        User.objects.create(username="test", email="aa@b.com")
        mock_requests.request.assert_called_with('put',
                                                 '%s/users/1' % prefix,
                                                 data={'username': 'test', 'api_key': api_key,
                                                       'external_id': '1', 'email': 'aa@b.com'}, timeout=5)


class CourseEndingTest(TestCase):
    """Test things related to course endings: certificates, surveys, etc"""

    def test_process_survey_link(self):
        username = "fred"
        user = Mock(username=username)
        id = unique_id_for_user(user)
        link1 = "http://www.mysurvey.com"
        self.assertEqual(process_survey_link(link1, user), link1)

        link2 = "http://www.mysurvey.com?unique={UNIQUE_ID}"
        link2_expected = "http://www.mysurvey.com?unique={UNIQUE_ID}".format(UNIQUE_ID=id)
        self.assertEqual(process_survey_link(link2, user), link2_expected)

    def test_cert_info(self):
        user = Mock(username="fred")
        survey_url = "http://a_survey.com"
        course = Mock(end_of_course_survey_url=survey_url)

        self.assertEqual(_cert_info(user, course, None),
                         {'status': 'processing',
                          'show_disabled_download_button': False,
                          'show_download_url': False,
                          'show_survey_button': False, })

        cert_status = {'status': 'unavailable'}
        self.assertEqual(_cert_info(user, course, cert_status),
                         {'status': 'processing',
                          'show_disabled_download_button': False,
                          'show_download_url': False,
                          'show_survey_button': False})

        cert_status = {'status': 'generating', 'grade': '67'}
        self.assertEqual(_cert_info(user, course, cert_status),
                         {'status': 'generating',
                          'show_disabled_download_button': True,
                          'show_download_url': False,
                          'show_survey_button': True,
                          'survey_url': survey_url,
                          'grade': '67'
                          })

        cert_status = {'status': 'regenerating', 'grade': '67'}
        self.assertEqual(_cert_info(user, course, cert_status),
                         {'status': 'generating',
                          'show_disabled_download_button': True,
                          'show_download_url': False,
                          'show_survey_button': True,
                          'survey_url': survey_url,
                          'grade': '67'
                          })

        download_url = 'http://s3.edx/cert'
        cert_status = {'status': 'downloadable', 'grade': '67',
                       'download_url': download_url}
        self.assertEqual(_cert_info(user, course, cert_status),
                         {'status': 'ready',
                          'show_disabled_download_button': False,
                          'show_download_url': True,
                          'download_url': download_url,
                          'show_survey_button': True,
                          'survey_url': survey_url,
                          'grade': '67'
                          })

        cert_status = {'status': 'notpassing', 'grade': '67',
                       'download_url': download_url}
        self.assertEqual(_cert_info(user, course, cert_status),
                         {'status': 'notpassing',
                          'show_disabled_download_button': False,
                          'show_download_url': False,
                          'show_survey_button': True,
                          'survey_url': survey_url,
                          'grade': '67'
                          })

        # Test a course that doesn't have a survey specified
        course2 = Mock(end_of_course_survey_url=None)
        cert_status = {'status': 'notpassing', 'grade': '67',
                       'download_url': download_url}
        self.assertEqual(_cert_info(user, course2, cert_status),
                         {'status': 'notpassing',
                          'show_disabled_download_button': False,
                          'show_download_url': False,
                          'show_survey_button': False,
                          'grade': '67'
                          })
