#
# File: logger.py
#
# Create a log for the nodeserver. In the setup method call with:
#   self.logger = setup_log(self.poly.sandbox,self.poly.name)
#

import logging
import logging.handlers
import time

def setup_log(path,name):
   # Log Location
   LOG_FILENAME = path + "/" + name + ".log"
   LOG_LEVEL = logging.DEBUG  # Could be e.g. "DEBUG" or "WARNING"

   #### Logging Section ################################################################################
   LOGGER = logging.getLogger(name)
   LOGGER.setLevel(LOG_LEVEL)
   # Set the log level to LOG_LEVEL
   # Make a handler that writes to a file, 
   # making a new file at midnight and keeping 30 backups
   HANDLER = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=30)
   # Format each log message like this
   FORMATTER = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
   # Attach the formatter to the handler
   HANDLER.setFormatter(FORMATTER)
   # Attach the handler to the logger
   LOGGER.addHandler(HANDLER)
   return LOGGER
