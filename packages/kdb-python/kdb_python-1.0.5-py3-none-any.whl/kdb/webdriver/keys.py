from selenium.webdriver.common.keys import Keys as SeleniumKeys

from kdb.common.utils import OS


class Keys:
    """
    Set of special keys.
    """

    NULL = '<keys.NULL>'
    CANCEL = '<keys.CANCEL>'  # ^break
    HELP = '<keys.HELP>'
    BACKSPACE = '<keys.BACKSPACE>'
    BACK_SPACE = BACKSPACE
    TAB = '<keys.TAB>'
    CLEAR = '<keys.CLEAR>'
    RETURN = '<keys.RETURN>'
    ENTER = '<keys.ENTER>'
    SHIFT = '<keys.SHIFT>'
    LEFT_SHIFT = SHIFT
    CONTROL = '<keys.CONTROL>'
    LEFT_CONTROL = CONTROL
    ALT = '<keys.ALT>'
    LEFT_ALT = ALT
    PAUSE = '<keys.PAUSE>'
    ESCAPE = '<keys.ESCAPE>'
    SPACE = '<keys.SPACE>'
    PAGE_UP = '<keys.PAGE_UP>'
    PAGE_DOWN = '<keys.PAGE_DOWN>'
    END = '<keys.END>'
    HOME = '<keys.HOME>'
    LEFT = '<keys.LEFT>'
    ARROW_LEFT = LEFT
    UP = '<keys.UP>'
    ARROW_UP = UP
    RIGHT = '<keys.RIGHT>'
    ARROW_RIGHT = RIGHT
    DOWN = '<keys.DOWN>'
    ARROW_DOWN = DOWN
    INSERT = '<keys.INSERT>'
    DELETE = '<keys.DELETE>'
    SEMICOLON = '<keys.SEMICOLON>'
    EQUALS = '<keys.EQUALS>'

    NUMPAD0 = '<keys.NUMPAD0>'  # number pad keys
    NUMPAD1 = '<keys.NUMPAD1>'
    NUMPAD2 = '<keys.NUMPAD2>'
    NUMPAD3 = '<keys.NUMPAD3>'
    NUMPAD4 = '<keys.NUMPAD4>'
    NUMPAD5 = '<keys.NUMPAD5>'
    NUMPAD6 = '<keys.NUMPAD6>'
    NUMPAD7 = '<keys.NUMPAD7>'
    NUMPAD8 = '<keys.NUMPAD8>'
    NUMPAD9 = '<keys.NUMPAD9>'
    MULTIPLY = '<keys.MULTIPLY>'
    ADD = '<keys.ADD>'
    SEPARATOR = '<keys.SEPARATOR>'
    SUBTRACT = '<keys.SUBTRACT>'
    DECIMAL = '<keys.DECIMAL>'
    DIVIDE = '<keys.DIVIDE>'

    F1 = '<keys.F1>'  # function  keys
    F2 = '<keys.F2>'
    F3 = '<keys.F3>'
    F4 = '<keys.F4>'
    F5 = '<keys.F5>'
    F6 = '<keys.F6>'
    F7 = '<keys.F7>'
    F8 = '<keys.F8>'
    F9 = '<keys.F9>'
    F10 = '<keys.F10>'
    F11 = '<keys.F11>'
    F12 = '<keys.F12>'

    META = '<keys.META>'
    COMMAND = '<keys.COMMAND>'

    @staticmethod
    def get_cmd_ctrl_key():
        return Keys.COMMAND if OS.is_mac_platform() else Keys.CONTROL


MODIFIER_KEYS = (
    Keys.SHIFT,
    Keys.LEFT_SHIFT,
    Keys.CONTROL,
    Keys.LEFT_CONTROL,
    Keys.ALT,
    Keys.LEFT_ALT,

    Keys.META,
    Keys.COMMAND,
)


KEYS_MAPPING: dict = {
    Keys.NULL: SeleniumKeys.NULL,
    Keys.CANCEL: SeleniumKeys.CANCEL,
    Keys.HELP: SeleniumKeys.HELP,
    Keys.BACKSPACE: SeleniumKeys.BACKSPACE,
    Keys.BACK_SPACE: SeleniumKeys.BACK_SPACE,
    Keys.TAB: SeleniumKeys.TAB,
    Keys.CLEAR: SeleniumKeys.CLEAR,
    Keys.RETURN: SeleniumKeys.RETURN,
    Keys.ENTER: SeleniumKeys.ENTER,
    Keys.SHIFT: SeleniumKeys.SHIFT,
    Keys.LEFT_SHIFT: SeleniumKeys.LEFT_SHIFT,
    Keys.CONTROL: SeleniumKeys.CONTROL,
    Keys.LEFT_CONTROL: SeleniumKeys.LEFT_CONTROL,
    Keys.ALT: SeleniumKeys.ALT,
    Keys.LEFT_ALT: SeleniumKeys.LEFT_ALT,
    Keys.PAUSE: SeleniumKeys.PAUSE,
    Keys.ESCAPE: SeleniumKeys.ESCAPE,
    Keys.SPACE: SeleniumKeys.SPACE,
    Keys.PAGE_UP: SeleniumKeys.PAGE_UP,
    Keys.PAGE_DOWN: SeleniumKeys.PAGE_DOWN,
    Keys.END: SeleniumKeys.END,
    Keys.HOME: SeleniumKeys.HOME,
    Keys.LEFT: SeleniumKeys.LEFT,
    Keys.ARROW_LEFT: SeleniumKeys.ARROW_LEFT,
    Keys.UP: SeleniumKeys.UP,
    Keys.ARROW_UP: SeleniumKeys.ARROW_UP,
    Keys.RIGHT: SeleniumKeys.RIGHT,
    Keys.ARROW_RIGHT: SeleniumKeys.ARROW_RIGHT,
    Keys.DOWN: SeleniumKeys.DOWN,
    Keys.ARROW_DOWN: SeleniumKeys.ARROW_DOWN,
    Keys.INSERT: SeleniumKeys.INSERT,
    Keys.DELETE: SeleniumKeys.DELETE,
    Keys.SEMICOLON: SeleniumKeys.SEMICOLON,
    Keys.EQUALS: SeleniumKeys.EQUALS,

    Keys.NUMPAD0: SeleniumKeys.NUMPAD0,
    Keys.NUMPAD1: SeleniumKeys.NUMPAD1,
    Keys.NUMPAD2: SeleniumKeys.NUMPAD2,
    Keys.NUMPAD3: SeleniumKeys.NUMPAD3,
    Keys.NUMPAD4: SeleniumKeys.NUMPAD4,
    Keys.NUMPAD5: SeleniumKeys.NUMPAD5,
    Keys.NUMPAD6: SeleniumKeys.NUMPAD6,
    Keys.NUMPAD7: SeleniumKeys.NUMPAD7,
    Keys.NUMPAD8: SeleniumKeys.NUMPAD8,
    Keys.NUMPAD9: SeleniumKeys.NUMPAD9,
    Keys.MULTIPLY: SeleniumKeys.MULTIPLY,
    Keys.ADD: SeleniumKeys.ADD,
    Keys.SEPARATOR: SeleniumKeys.SEPARATOR,
    Keys.SUBTRACT: SeleniumKeys.SUBTRACT,
    Keys.DECIMAL: SeleniumKeys.DECIMAL,
    Keys.DIVIDE: SeleniumKeys.DIVIDE,

    Keys.F1: SeleniumKeys.F1,
    Keys.F2: SeleniumKeys.F2,
    Keys.F3: SeleniumKeys.F3,
    Keys.F4: SeleniumKeys.F4,
    Keys.F5: SeleniumKeys.F5,
    Keys.F6: SeleniumKeys.F6,
    Keys.F7: SeleniumKeys.F7,
    Keys.F8: SeleniumKeys.F8,
    Keys.F9: SeleniumKeys.F9,
    Keys.F10: SeleniumKeys.F10,
    Keys.F11: SeleniumKeys.F11,
    Keys.F12: SeleniumKeys.F12,

    Keys.META: SeleniumKeys.META,
    Keys.COMMAND: SeleniumKeys.COMMAND
}


def is_modifier_key(key):
    return key in MODIFIER_KEYS


def is_special_key(key):
    return key in KEYS_MAPPING.keys()
