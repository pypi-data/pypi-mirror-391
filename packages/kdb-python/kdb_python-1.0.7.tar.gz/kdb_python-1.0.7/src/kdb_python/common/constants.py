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
    __COMMON_PARAM = ' --enable-heapdump --relaxed-security'

    __APPIUM_ANDROID_PARAM = ' -bp %d --chromedriver-port %d --suppress-adb-kill-server'
    START_APPIUM_ANDROID = '/usr/local/bin/node /usr/local/bin/appium -a %s -p %d' + __APPIUM_ANDROID_PARAM + __COMMON_PARAM
    START_APPIUM_ANDROID_WIN = 'appium -a %s -p %d' + __APPIUM_ANDROID_PARAM + __COMMON_PARAM

    __APPIUM_IOS_PARAM = ' --driver-xcuitest-webdriveragent-port %d --tmp %s'
    START_APPIUM_IOS = '/usr/local/bin/node /usr/local/bin/appium -a %s -p %d' + __APPIUM_IOS_PARAM + __COMMON_PARAM

    GET_PROCESS_ID_BY_PORT = "ps -ef | grep %s | grep -v grep | grep %d | awk '{print $2}'"
    GET_PROCESS_ID_BY_PORT_WIN = "netstat -ano | grep :%d | awk '{print $5}'"

    KILL_PROCESS = "kill -9 %s"
    KILL_PROCESS_WIN = "taskkill /f /pid %s"

    SERVER_TIME_FORMAT = "%Y%m%d%H%M%S"
    GET_SERVER_TIME = "echo `date +%s`" % SERVER_TIME_FORMAT
    GET_DATA_LINES_FROM_FILE = "head -%d %s"
    CREATE_LOCK_FILE_IF_NOT_EXISTS = "[ ! -f %s ] && echo `date +%s` > %s && echo 'true' || echo 'false'"
    REMOVE_FILE = "rm %s"

    SERVER_TIME_FORMAT_WIN = "%date:~-4%%date:~7,2%%date:~4,2%%time:~0,2%%time:~3,2%%time:~6,2%"
    GET_SERVER_TIME_WIN = "echo %s" % SERVER_TIME_FORMAT_WIN
    GET_DATA_LINES_FROM_FILE_WIN = "set /p timeval=< %s && echo %timeval%"
    CREATE_LOCK_FILE_IF_NOT_EXISTS_WIN = "[ ! -f %s ] && echo %s > %s && echo 'true' || echo 'false'"
    REMOVE_FILE_WIN = "del %s"
