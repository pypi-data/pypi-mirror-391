import logging

from selenium.common.exceptions import JavascriptException

from kdb.common.utils import TimeUtil, WebDriverUtil
from kdb.webdriver.actions.mobile_gestures import tap


def _execute_video_action(driver, element, array_action, value=None):
    """
    Execute a video action/api
    """
    for action in array_action:
        try:
            # add value to action
            if value is not None:
                action = action % value
            script = "return arguments[0].%s;" % action
            return driver.execute_script(script, element)
        except JavascriptException as ex:
            logging.warning("Can't execute Javascript: %s. Error: %s" % (script, str(ex)))
            pass
    else:
        raise JavascriptException("Fail to perform the video actions: %s. Driver capabilities %s" % (
            str(array_action), str(driver.desired_capabilities)))


class VideoApi:
    """
    The video's Api js
    """
    PLAY = ['play()', 'play_video()']  # return {}
    PAUSE = ['pause()', 'pause_video()']  # return None
    MUTED = ['muted=true', 'go_mute()', 'mute(true)', 'setMuted(true)']  # return True
    UNMUTED = ['muted=false', 'go_unmute()', 'mute(false)']  # return False
    VOLUME = ['volume=%s', 'volume=change_sound_volume(%s)', 'setVolume(%s)']  # return value of volume
    TRACK_TIME = ['currentTime=%s', 'seek(%s)']  # return value of current video time
    IS_PLAYING = ['paused==false', 'is_playing()', 'isPlaying()', 'getPlaying()']
    IS_PAUSED = ['paused', 'is_playing()==false', 'isPaused()', 'getPaused()']
    IS_MUTED = ['muted', 'is_muted()', 'getVolume()==0', 'getMuted()']
    IS_UNMUTED = ['muted==false']
    VERIFY_VOLUME = ['volume==%s', 'get_sound_volume()==%s', 'getVolume()==%s']


# using for play function
was_tap_on_video = False


def play(driver, element, extra_time):
    """
    Play a video
    """
    TimeUtil.sleep(extra_time)
    # in chrome, must focus document before play video
    # if WebDriverUtil.is_chrome(driver):
    # Don't click on head tag, cause it Failed:
    # Message: javascript error: {"status":60,"value":"[object HTMLHeadElement] has no size and location"}
    #     ActionChains(driver).click(driver.find_element(By.TAG_NAME, 'head')).perform()
    # We must execute tap native action when play video at first time on iOS
    if WebDriverUtil.is_ios_web(driver):
        global was_tap_on_video
        if not was_tap_on_video:
            tap(driver, element, extra_time=None)
            was_tap_on_video = True
    #
    _execute_video_action(driver, element, VideoApi.PLAY)
    return True


def pause(driver, element, extra_time):
    """
    Pause a video
    """
    TimeUtil.sleep(extra_time)
    _execute_video_action(driver, element, VideoApi.PAUSE)
    return True


def muted(driver, element, extra_time):
    """
    Muted a video
    """
    TimeUtil.sleep(extra_time)
    _execute_video_action(driver, element, VideoApi.MUTED)
    return True


def unmuted(driver, element, extra_time):
    """
    Unmuted a video
    """
    TimeUtil.sleep(extra_time)
    _execute_video_action(driver, element, VideoApi.UNMUTED)
    return True


def volume(driver, element, value, extra_time):
    """
    Change volume for video
    """
    TimeUtil.sleep(extra_time)
    _execute_video_action(driver, element, VideoApi.VOLUME, float(value / 10))
    return True


def track_time(driver, element, value, extra_time):
    """
    Track time video
    """
    TimeUtil.sleep(extra_time)
    _execute_video_action(driver, element, VideoApi.TRACK_TIME, value)
    return True


def is_playing(driver, element, reverse, extra_time):
    """
    Verify video is playing
    """
    TimeUtil.sleep(extra_time)
    return _execute_video_action(driver, element, VideoApi.IS_PLAYING) != reverse


def is_paused(driver, element, reverse, extra_time):
    """
    Verify video was paused
    """
    TimeUtil.sleep(extra_time)
    return _execute_video_action(driver, element, VideoApi.IS_PAUSED) != reverse


def is_muted(driver, element, reverse, extra_time):
    """
    Verify video was muted
    """
    TimeUtil.sleep(extra_time)
    return _execute_video_action(driver, element, VideoApi.IS_MUTED) != reverse


def is_unmuted(driver, element, reverse, extra_time):
    """
    Verify video was unmuted
    """
    TimeUtil.sleep(extra_time)
    return _execute_video_action(driver, element, VideoApi.IS_UNMUTED) != reverse


def verify_volume(driver, element, value, reverse, extra_time):
    """
    Verify volume of video
    """
    TimeUtil.sleep(extra_time)
    return _execute_video_action(driver, element, VideoApi.VERIFY_VOLUME, float(value / 10)) != reverse
