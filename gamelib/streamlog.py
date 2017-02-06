"""Redirect stream to a logger.

@Author: Stephen J. Bush
@Date: 07.29.16
@Source: http://www.electricmonk.nl/log/2011/08/14/
"""


class StreamLogger():
    """Stream-like object that logs instead."""

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        """Prevent errors during unittesting."""
        pass
