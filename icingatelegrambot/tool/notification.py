import logging
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class NotificationParser():
    def findHostnameFromNotification(notification):
        host_result = re.search("(?:Host: )(.*)", notification)
        if (host_result is None):
            logger.warning("No Host match for ack!")
            return None

        return host_result.group(1)

    def findHostnameAndServicenameFromNotification(notification):
        hostname = NotificationParser.findHostnameFromNotification(notification)

        if(hostname is None):
            return None

        service_result = re.search("(?:Service: )(.*)", notification)

        if (service_result is None):
            logger.warning("No service match for notification!")
            return hostname, None

        servicename = service_result.group(1)

        return hostname, servicename
