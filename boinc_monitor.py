#!/usr/bin/env python
# A quick and dirty script to start and stop bionc according to cpu load.
# When the number of running processes is greater than STOP_BIONC_THRESHOLD,
# then boinc activity will be suspended. When the number of running processes
# is less than START_BIONIC_THRESHOLD, boinc activity will resume.
import logging
import logging.handlers
import os
import sys
import time

# Defaults
STATE_BOINC_RUNNING = 0
STATE_BOINC_STOPPED = 1
STOP_BOINC_THRESHOLD = 35 # Stop boinc when num running processes > 35
START_BOINC_THRESHOLD = 10 # Start boinc when num running processes < 10
START_BOINC_COMMAND = "boinccmd --set_run_mode always"
STOP_BOINC_COMMAND = "boinccmd --set_run_mode never"
MONITOR_INTERVAL = 10 # How often to check (in seconds)

LOG_FILENAME = "/tmp/boinc_monitor.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"


# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
  def __init__(self, logger, level):
    """Needs a logger and a logger level."""
    self.logger = logger
    self.level = level

  def write(self, message):
    # Only log if there is a message (not just a new line)
    if message.rstrip() != "":
      self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

logger.info("Starting boinc_monitor.py")
current_state = STATE_BOINC_RUNNING

# Note: Linux specific
def GetNumProcsRunning():
  with open("/proc/stat") as f:
    for line in f:
      if line.startswith("procs_running"):
        return int(line.split()[1])

while True:
  running_procs = GetNumProcsRunning()

  if current_state == STATE_BOINC_RUNNING:
    if running_procs > STOP_BOINC_THRESHOLD:
      logger.info("Stopping boinc")
      os.system(STOP_BOINC_COMMAND)
      current_state = STATE_BOINC_STOPPED

  if current_state == STATE_BOINC_STOPPED:
    if running_procs < START_BOINC_THRESHOLD:
      logger.info("Starting boinc")
      os.system(START_BOINC_COMMAND)
      current_state = STATE_BOINC_RUNNING

  time.sleep(MONITOR_INTERVAL)


