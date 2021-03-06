from threading import Thread
from time import sleep

from pyww.core.logger import logger
from pyww.sites.site import NotifyOnType


class Watcher(Thread):
    def __init__(self, browser, interval, notifier):
        logger.info("Initializing watcher")
        super().__init__()
        self._shutdown = False
        self._browser = browser
        self._interval = interval
        self._notifier = notifier

    def _teardown(self):
        logger.info("Tearing down watcher")
        self._browser.close()

    def _watch(self):
        sites_loaded = self._browser.load_sites()
        while sites_loaded and not self._shutdown:
            self._track_changes(self._browser.scrape_sites_by_xpath())
            self._sleep_on_interval()
            if not self._shutdown:
                self._browser.refresh_sites()

    def _evaluate_baseline(self, site, n_elements):
        site_notify_type = site.get_notify_type()
        element_baseline = None
        if (n_elements == 0 and site_notify_type == NotifyOnType.APPEAR) or \
                (n_elements > 0 and site_notify_type == NotifyOnType.DISAPPEAR):
            logger.info("Tracking '%s:%s[%s]' for site '%s'",
                        site.get_watch_type().value, site.get_text(),
                        site_notify_type.value, site.get_url(friendly=True))
            element_baseline = n_elements
            logger.debug("'%s': [baseline=%d]",
                         element_baseline, site.get_url(friendly=True))
        else:
            logger.warning("Unable to establish an accurate baseline with '%s:%s[%s]' for site '%s' - "
                           "Action may have already occurred?", site.get_watch_type().value, site.get_text(),
                           site_notify_type.value, site.get_url(friendly=True))
        site.set_element_baseline(element_baseline)
        return element_baseline

    def _sleep_on_interval(self):
        logger.info("Waiting %ds before refresh", self._interval)
        for _ in range(self._interval):
            if self._shutdown:
                break
            sleep(1)

    def _track_changes(self, scrape_results):
        for site, n_elements in scrape_results:
            site_url = site.get_url(friendly=True)
            site_notify_type = site.get_notify_type()
            element_baseline = site.get_element_baseline()
            if element_baseline is None:
                element_baseline = self._evaluate_baseline(site, n_elements)
                # Unable to track changes if a baseline is not established
                if element_baseline is None:
                    logger.warning(
                        "Skipping tracking '%s'...", site_url)
                    continue

            if (n_elements > element_baseline and site_notify_type == NotifyOnType.APPEAR) or \
                    (n_elements < element_baseline and site_notify_type == NotifyOnType.DISAPPEAR):
                # Action occurred - alert user
                logger.info("ALERT '%s:%s[%s]' in '%s'",
                            site.get_watch_type().value, site.get_text(), site_notify_type.value, site_url)
                logger.debug("'%s': [baseline=%d, [n_elements=%d]",
                             site_url, element_baseline, n_elements)
                self._send_notification(site)
            else:
                # No changes found yet
                logger.info("No changes found in '%s'", site_url)

    def _send_notification(self, site):
        site_item = site.get_item_name()
        logger.info("Sending notification for '%s'", site_item)
        self._notifier.notify(
            site.get_url(friendly=True),
            "Watcher signaled for item '{item}'".format(item=site_item),
            site.get_url()
        )

    def run(self):
        try:
            self._watch()
            self._teardown()
        except Exception as e:
            logger.error(str(e))

    def shut_down(self):
        self._shutdown = True
