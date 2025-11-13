"""This module provides custom logging filters for the CHIME logger.

Classes:
    PipelineFilter: Ensures log records have a 'pipeline' attribute.
    ResourceNameFilter: Ensures log records have an 'resource_name' attribute.
    ResourceTypeFilter: Ensures log records have an 'resource_type' attribute.
    SiteFilter: Ensures log records have an 'site' attribute.
    LokiSiteValidityFilter: Drops records to Loki when site is invalid/unknown.
"""

import logging
import os


class PipelineFilter(logging.Filter):
    """Logging filter that ensures each log record has a 'pipeline' attribute.

    If the 'pipeline' attribute is missing, it sets it to the value of the
    'CHIME_LOGGER_PIPELINE_NAME' environment variable, or 'unknown_pipeline'
    if the environment variable is not set.
    """

    def filter(self, record):
        """Ensures that each log record has a 'pipeline' attribute.

        If the 'pipeline' attribute is missing from the log record, this method sets it
        to the value of the 'CHIME_LOGGER_PIPELINE_NAME' environment variable, or
        'unknown_pipeline' if the environment variable is not set.

        Args:
            record (logging.LogRecord): The log record to filter.

        Returns:
            bool: Always returns True to allow the record to be processed.
        """
        if not hasattr(record, "pipeline"):
            record.pipeline = os.getenv(
                "CHIME_LOGGER_PIPELINE_NAME", "unknown_pipeline"
            )
        return True


class ResourceNameFilter(logging.Filter):
    """Logging filter that ensures each log record has an 'resource_name' attribute.

    If the 'resource_name' attribute is missing, it sets it to 'unknown_name'.
    """

    def filter(self, record):
        """Ensures that each log record has an 'resource_name' attribute.

        If the 'resource_name' attribute is missing from the log record, this method sets it
        to 'unknown_name'.

        Args:
            record (logging.LogRecord): The log record to filter.

        Returns:
            bool: Always returns True to allow the record to be processed.
        """
        if not hasattr(record, "resource_name"):
            record.resource_name = "unknown_name"
        return True


class ResourceTypeFilter(logging.Filter):
    """Logging filter that ensures each log record has an 'resource_type' attribute.

    If the 'resource_type' attribute is missing, it sets it to 'unknown_type'.
    """

    def filter(self, record):
        """Ensures that each log record has an 'resource_type' attribute.

        If the 'resource_type' attribute is missing from the log record, this method sets it
        to 'unknown_type'.

        Args:
            record (logging.LogRecord): The log record to filter.

        Returns:
            bool: Always returns True to allow the record to be processed.
        """
        if not hasattr(record, "resource_type"):
            record.resource_type = "unknown_type"
        return True


class SiteFilter(logging.Filter):
    """Logging filter that ensures each log record has an 'site' attribute.

    If the 'site' attribute is missing or falsy, it sets it to 'unknown_site'.
    """

    def filter(self, record):
        """Ensures that each log record has an 'site' attribute.

        If the 'site' attribute is missing from the log record or is falsy (e.g. None/''),
        this method sets it to 'unknown_site'.

        Args:
            record (logging.LogRecord): The log record to filter.

        Returns:
            bool: Always returns True to allow the record to be processed.
        """
        if not hasattr(record, "site") or not getattr(record, "site"):
            record.site = "unknown_site"
        return True


class LokiSiteValidityFilter(logging.Filter):
    """Drops records headed to Loki when site is invalid or unknown.

    This is intended to be added only to the Loki handler. It returns False
    (dropping the record for that handler) when `record.site` is missing,
    resolves to 'unknown_site', or is not in the allowed set.
    Other handlers still process the record.
    """

    ALLOWED_SITES = {"chime", "kko", "gbo", "hco"}

    def filter(self, record):
        """Ensures that each log record has a valid 'site' attribute.

        Args:
            record (logging.LogRecord): The log record to filter.

        Returns:
            bool: Always returns True to allow the record to be processed.
        """
        site = getattr(record, "site", None)
        if (
            not site
            or site == "unknown_site"
            or str(site).lower() not in self.ALLOWED_SITES
        ):
            return False
        return True
