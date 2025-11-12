from kdb.common.constants import InfoMessage
from kdb.common.utils import TimeUtil
from kdb.config.settings import DriverSettings
from kdb.webdriver import actions
from kdb.webdriver.actions import video
from kdb.webdriver.common import log_start, report_passed_test_step, report_failed_test_step


class VideoElement:
    """
    Class for action video
    """

    def __init__(self, driver):
        self._driver = driver

    def __new__(cls, driver):
        """
        Classic singleton in Python, we check whether an instance is already created.
        If it is created, we return it; otherwise, we create a new instance, assign it to a class attribute,
        and return it.
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(VideoElement, cls).__new__(cls)
        else:
            cls.instance._driver = driver
        return cls.instance

    def play(self, locator, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
        Play a video
        """
        log_start(self.play.__name__, (locator, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.play, self._driver, locator, timeout)
            report_passed_test_step(self.play.__name__, (locator, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % "Play video")
        except Exception as ex:
            report_failed_test_step(self._driver, self.play.__name__, (locator, timeout), start_time, str(ex))

    def pause(self, locator, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
        Pause a video
        """
        log_start(self.pause.__name__, (locator, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.pause, self._driver, locator, timeout)
            report_passed_test_step(self.pause.__name__, (locator, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % "Pause video")
        except Exception as ex:
            report_failed_test_step(self._driver, self.pause.__name__, (locator, timeout), start_time, str(ex))

    def muted(self, locator, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
        Muted a video
        """
        log_start(self.muted.__name__, (locator, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.muted, self._driver, locator, timeout)
            report_passed_test_step(self.muted.__name__, (locator, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % "Muted video")
        except Exception as ex:
            report_failed_test_step(self._driver, self.muted.__name__, (locator, timeout), start_time, str(ex))

    def unmuted(self, locator, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
        Unmuted a video
        """
        log_start(self.unmuted.__name__, (locator, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.unmuted, self._driver, locator, timeout)
            report_passed_test_step(self.unmuted.__name__, (locator, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % "Unmuted video")
        except Exception as ex:
            report_failed_test_step(self._driver, self.unmuted.__name__, (locator, timeout), start_time, str(ex))

    def volume(self, locator, value, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
        Change volume for video
        """

        log_start(self.volume.__name__, (locator, value, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.volume, self._driver, locator, timeout, value)
            report_passed_test_step(self.volume.__name__, (locator, value, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % "Volume video " + str(value))
        except Exception as ex:
            report_failed_test_step(self._driver, self.volume.__name__, (locator, value, timeout), start_time, str(ex))

    def track_time(self, locator, value, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
        Track time video
        """
        log_start(self.track_time.__name__, (locator, value, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.track_time, self._driver, locator, timeout, value)
            report_passed_test_step(self.track_time.__name__, (locator, value, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Track time video " + str(value)))
        except Exception as ex:
            report_failed_test_step(self._driver, self.track_time.__name__, (locator, value, timeout), start_time,
                                    str(ex))

    def is_playing(self, locator, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
         Verify video is playing
        """
        log_start(self.is_playing.__name__, (locator, reverse, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.is_playing, self._driver, locator, timeout, reverse)
            report_passed_test_step(self.is_playing.__name__, (locator, reverse, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % "Verify video is playing ")
        except AssertionError:
            report_failed_test_step(self._driver, self.is_playing.__name__, (locator, reverse, timeout), start_time,
                                    "The video is not playing: " + locator)
        except Exception as ex:
            report_failed_test_step(self._driver, self.is_playing.__name__, (locator, reverse, timeout), start_time,
                                    str(ex))

    def is_paused(self, locator, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):

        """
        Verify video was paused
        """
        log_start(self.is_paused.__name__, (locator, reverse, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.is_paused, self._driver, locator, timeout, reverse)
            report_passed_test_step(self.is_paused.__name__, (locator, reverse, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % "Verify video paused ")
        except AssertionError:
            report_failed_test_step(self._driver, self.is_paused.__name__, (locator, reverse, timeout), start_time,
                                    "The video is not pause: " + locator)
        except Exception as ex:
            report_failed_test_step(self._driver, self.is_paused.__name__, (locator, reverse, timeout), start_time,
                                    str(ex))

    def is_muted(self, locator, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
        Verify video was muted
        """
        log_start(self.is_muted.__name__, (locator, reverse, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.is_muted, self._driver, locator, timeout, reverse)
            report_passed_test_step(self.is_muted.__name__, (locator, reverse, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % "Verify video muted ")
        except AssertionError:
            report_failed_test_step(self._driver, self.is_muted.__name__, (locator, reverse, timeout), start_time,
                                    "The video is not muted: " + locator)
        except Exception as ex:
            report_failed_test_step(self._driver, self.is_muted.__name__, (locator, reverse, timeout), start_time,
                                    str(ex))

    def is_unmuted(self, locator, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
        Verify video was unmuted
        """
        log_start(self.is_unmuted.__name__, (locator, reverse, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.is_unmuted, self._driver, locator, timeout, reverse)
            report_passed_test_step(self.is_unmuted.__name__, (locator, reverse, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % "Verify video unmuted ")
        except AssertionError:
            report_failed_test_step(self._driver, self.is_unmuted.__name__, (locator, reverse, timeout), start_time,
                                    "The video is not unmuted: " + locator)
        except Exception as ex:
            report_failed_test_step(self._driver, self.is_unmuted.__name__, (locator, reverse, timeout), start_time,
                                    str(ex))

    def verify_volume(self, locator, value, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT):
        """
        Verify volume of video
        """
        log_start(self.verify_volume.__name__, (locator, value, reverse, timeout))
        start_time = TimeUtil.current_time_ms()
        try:
            actions.perform(video.verify_volume, self._driver, locator, timeout, value, reverse)
            report_passed_test_step(self.verify_volume.__name__, (locator, value, reverse, timeout), start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Verify volume is " + str(value)))
        except AssertionError:
            report_failed_test_step(self._driver, self.verify_volume.__name__, (locator, value, reverse, timeout),
                                    start_time,
                                    "The video is not match with volume = %s. %s" % (value, (locator, value, reverse)))
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_volume.__name__, (locator, value, reverse, timeout),
                                    start_time, str(ex))
