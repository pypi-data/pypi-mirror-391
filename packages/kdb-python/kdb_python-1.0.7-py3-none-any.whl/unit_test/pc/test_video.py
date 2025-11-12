from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def video_test():
    # add command to the report
    report.add_comment("Test video")
    # start browser
    kdb_driver.start_browser()
    # loads login page in the current browser session.
    kdb_driver.open_url('https://bitmovin.com/demos/player-ui-styling')

    report.add_comment(">>> Playing the video")
    # play a video
    kdb_driver.video.play('id=bitmovinplayer-video-player-container')
    # verify the video is playing
    kdb_driver.video.is_playing('id=bitmovinplayer-video-player-container')
    # verify the video  is playing with state not pause
    kdb_driver.video.is_paused('id=bitmovinplayer-video-player-container', reverse=True, timeout=1)
    kdb_driver.screen_shot()

    report.add_comment(">>> Pause the video")
    # pause the video
    kdb_driver.video.pause('id=bitmovinplayer-video-player-container')
    # verify the video paused
    kdb_driver.video.is_paused('id=bitmovinplayer-video-player-container')
    # verify the video paused
    kdb_driver.video.is_playing('id=bitmovinplayer-video-player-container', reverse=True, timeout=1, extra_time=1)
    kdb_driver.screen_shot()

    report.add_comment(">>> Muted the video")
    # play a video
    kdb_driver.video.play('id=bitmovinplayer-video-player-container', extra_time=1, timeout=1)
    # muted the video
    kdb_driver.video.muted('id=bitmovinplayer-video-player-container')
    # verify the video muted
    kdb_driver.video.is_muted('id=bitmovinplayer-video-player-container', timeout=5)
    # muted the video mute
    kdb_driver.video.is_unmuted('id=bitmovinplayer-video-player-container', reverse=True, timeout=1)
    kdb_driver.screen_shot()

    report.add_comment(">>> Unmuted the video")
    # muted the video unmute
    kdb_driver.video.unmuted('id=bitmovinplayer-video-player-container')
    # muted the video unmute
    kdb_driver.video.is_unmuted('id=bitmovinplayer-video-player-container')
    # verify the video unmuted
    kdb_driver.video.is_muted('id=bitmovinplayer-video-player-container', reverse=True, timeout=0, extra_time=1)
    kdb_driver.screen_shot()

    report.add_comment(">>> Set and verify volume for the video")
    # set volume for the video
    kdb_driver.video.volume('id=bitmovinplayer-video-player-container', 6)
    # verify volume of the video is 6
    kdb_driver.video.verify_volume('id=bitmovinplayer-video-player-container', 6)
    # verify volume of the video is not 3.
    kdb_driver.video.verify_volume('id=bitmovinplayer-video-player-container', 3, reverse=True, timeout=0)
    # set volume for the video
    kdb_driver.video.volume('id=bitmovinplayer-video-player-container', 3)
    # verify volume of the video is 3
    kdb_driver.video.verify_volume('id=bitmovinplayer-video-player-container', 3)
    # verify volume of the video is not 8.
    kdb_driver.video.verify_volume('id=bitmovinplayer-video-player-container', 8, reverse=True, timeout=0)
    kdb_driver.screen_shot()

    report.add_comment(">>> Set track_time")
    # pause the video to verify track_time
    kdb_driver.video.pause('id=bitmovinplayer-video-player-container')
    # set current time of the video is 20 second
    kdb_driver.video.track_time('id=bitmovinplayer-video-player-container', 20)
    # verify todo
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
