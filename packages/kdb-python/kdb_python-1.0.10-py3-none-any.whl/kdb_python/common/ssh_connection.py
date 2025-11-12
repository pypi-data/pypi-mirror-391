import logging
import time

import paramiko


class SSH:
    COMMAND_TIMEOUT = 60

    def __init__(self, address, username=None, password=None):
        self.address = address
        self.username = username
        self.password = password
        self.client = None

    def _connect(self):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.address, username=self.username, password=self.password, timeout=self.COMMAND_TIMEOUT)

    def execute_command(self, command, print_command=True):
        if self.client is None:
            self._connect()

        stdin, stdout, stderr = self.client.exec_command(command, timeout=self.COMMAND_TIMEOUT, get_pty=True)
        if print_command:
            logging.info("Command execution: " + command)
        # stdout.readlines() hangs when run appium server so we use this workaround
        # https://github.com/paramiko/paramiko/issues/109#issuecomment-111621658
        # end_time = time.time() + self.COMMAND_TIMEOUT
        # while not stdout.channel.eof_received:
        #     time.sleep(1)
        #     if time.time() > end_time:
        #         stdout.channel.close()
        #         break

        # stdout.readlines() hangs when start appium server so we use this workaround
        if "appium -a" in command or "ios_webkit_debug_proxy" in command:
            res = []
            end_time = time.time() + self.COMMAND_TIMEOUT
            while time.time() < end_time:
                try:
                    line = stdout.readline()
                    res.append(line)
                    if "Welcome to Appium" in line:
                        return res
                except Exception:
                    break

            return res
        else:
            return stdout.readlines()
