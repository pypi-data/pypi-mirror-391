class TestStepLog:

    def __init__(self, action: str, params, duration: int, status, message):
        self.action = action
        self.params = params
        self.duration = duration
        self.status = status
        self.message = message

    def __str__(self, *args, **kwargs):  # real signature unknown
        """ Return str(self). """
        return "{action: %s, params: %s, duration: %u, status: %s, message: %s}" % (
            self.action, self.params, self.duration, self.status, self.message)
