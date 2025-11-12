class TestStatus:
    PASSED = "passed"
    FAILED = "failed"
    SKIP = "skip"
    WARN = "warn"


class InfoMessage:
    ACTION_SUCCESS = "%s successfully."


class ErrorMessage:
    INVALID_ARGUMENT = "The %s argument is invalid."
    START_APPIUM_ERROR = "Can't start appium server with port %s."
    FIND_DEVICE_TIMEOUT = "Not found free device on %d seconds."
    CREATE_LOCK_FILE_TIMEOUT = "Can not create %s file on %d seconds."
    DEVICE_NOT_FOUND = "The %s device is not found."


class AppiumCommand:
    __COMMON_PARAM = ' --relaxed-security'

    # __APPIUM_ANDROID_PARAM = ' -bp %d --chromedriver-port %d --suppress-adb-kill-server'
    __APPIUM_ANDROID_PARAM = ' --allow-insecure chromedriver_autodownload'
    # START_APPIUM_ANDROID = '/usr/local/bin/node /usr/local/bin/appium -a %s -p %d' + __COMMON_PARAM + __APPIUM_ANDROID_PARAM
    START_APPIUM_ANDROID = 'appium -a %s -p %d' + __COMMON_PARAM + __APPIUM_ANDROID_PARAM
    START_APPIUM_ANDROID_WIN = 'appium -a %s -p %d' + __COMMON_PARAM + __APPIUM_ANDROID_PARAM
    # START_APPIUM_ANDROID_WIN = 'appium -p %d' + __COMMON_PARAM + __APPIUM_ANDROID_PARAM

    __APPIUM_IOS_PARAM = ' --driver-xcuitest-webdriveragent-port %d --tmp %s'
    START_APPIUM_IOS = 'appium -a %s -p %d' + __APPIUM_IOS_PARAM + __COMMON_PARAM

    GET_PROCESS_ID_BY_PORT = "ps -ef | grep %s | grep -v grep | grep %d | awk '{print $2}'"
    GET_PROCESS_ID_BY_PORT_WIN = "for /f \"tokens=5\" %%a in ('netstat -aon ^| findstr /R \"%d.*[^*]LISTENING\"') do @echo %%~nxa"

    KILL_PROCESS = "kill -9 %s"
    KILL_PROCESS_WIN = "taskkill /f /pid %s"

    SERVER_TIME_FORMAT = "%Y%m%d%H%M%S"
    GET_SERVER_TIME = "echo `date +%s`" % SERVER_TIME_FORMAT
    GET_DATA_LINES_FROM_FILE = "head -%d %s"
    CREATE_LOCK_FILE_IF_NOT_EXISTS = "[ ! -f %s ] && echo `date +%s` > %s && echo 'true' || echo 'false'"
    REMOVE_FILE = "rm %s"

    SERVER_TIME_FORMAT_WIN = "%date:~-4%%date:~4,2%%date:~7,2%%time:~0,2%%time:~3,2%%time:~6,2%"
    GET_SERVER_TIME_WIN = "echo %s" % SERVER_TIME_FORMAT_WIN
    GET_DATA_LINES_FROM_FILE_WIN = "type %s | more"
    CREATE_LOCK_FILE_IF_NOT_EXISTS_WIN = "if not exist %s (echo %s > %s && echo true) else (echo false)"
    REMOVE_FILE_WIN = "del %s"
