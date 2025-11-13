# Copyright 2025 Cotality
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""CLIP Job Management Service."""
from __future__ import annotations

import enum
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from logging import getLogger
from typing import Any, List, Optional

import pandas as pd
from dataclasses_json import DataClassJsonMixin

from ....core.clgxtyping import PlatformType
from ....core.interfaces.database import DatabaseClient
from ....core.interfaces.database_types import ColumnDefinition, DataTypeEnum
from ....core.interfaces.table import Table
from ....core.utils.misc import datetime_to_int
from ....core.utils.system import available_memory_and_cpu
from ..typing import (
    COTALITY_APP_ROLE,
    STORAGE_INPUT_SUFFIX,
    STORAGE_OUTPUT_SUFFIX,
    ClipLookupAction,
    ClipMetrics,
    ClipSummaryMetrics,
    InputMetrics,
    RunStatus,
)

logger = getLogger(__name__)


class ClipJobStatus(str, enum.Enum):
    """Enumeration for clip job status."""

    UNKNOWN = "unknown"
    UPLOAD_DATA = "upload_data"
    SUBMITTED = "submitted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

    def __str__(self):
        """Return string.

        Returns:
            str: String
        """
        return str(self.value)


class Columns(enum.Enum):
    """Column names for the CLIP job management table."""

    JOB_ID = "job_id"
    INPUT_TABLE = "input_table"
    STATUS = "status"
    STEP = "step"
    # Timing
    STARTED_AT = "started_at"
    COMPLETED_AT = "completed_at"
    UPDATED_AT = "updated_at"
    ELAPSED_TIME_IN_SECONDS = "elapsed_time_in_seconds"
    # Message
    MESSAGE = "message"
    MESSAGE_DETAILS = "message_details"
    # Clip Job
    CLIP_JOB_ID = "clip_job_id"
    CLIP_JOB_RAW_STATUS = "clip_job_raw_status"
    CLIP_JOB_STATUS = "clip_job_status"
    # DMZ Storage
    STORAGE_URL_PREFIX = "storage_url_prefix"
    STORAGE_PREFIX = "storage_prefix"
    STORAGE_INPUT_URL = "storage_input_url"
    STORAGE_OUTPUT_URL = "storage_output_url"
    STORAGE_DOWNLOAD_PATH = "storage_download_path"

    # Metrics
    CLIP_METRICS = "clip_metrics"

    def __str__(self):
        """Return string.

        Returns:
            str: String
        """
        return str(self.value)


@dataclass(init=True, frozen=False)
class ClipJob(DataClassJsonMixin):
    """CLIP job dataclass model.

    This dataclass represents the structure of CLIP job data
    with business-friendly field names that map to database columns.
    """

    # === PRIMARY KEY ===
    job_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    input_table: str = ""  # Input table name
    status: RunStatus = RunStatus.UNKNOWN  # Job status
    step: ClipLookupAction = ClipLookupAction.INITIALIZE  # Current processing step

    # Timing
    started_at: int = datetime_to_int()
    updated_at: int = datetime_to_int()  # Job update time
    completed_at: int = 0  # Job completion time
    elapsed_time_in_seconds: int = (
        0  # Job elapsed time in seconds (Maps to elapsed_time_in_seconds)
    )

    # Message
    message: str = ""  # Job message
    message_details: str = ""  # Job message details

    # Clip Job
    clip_job_id: str = ""
    clip_job_raw_status: str = ""
    clip_job_status: ClipJobStatus = ClipJobStatus.UNKNOWN

    # Storage
    storage_url_prefix: str = ""  # Storage URL prefix
    storage_prefix: str = ""  # Storage prefix
    storage_input_url: str = ""  # Storage input URL
    storage_output_url: str = ""  # Storage output URL
    storage_download_path: str = ""  # Storage download path

    # Metrics
    clip_metrics: ClipMetrics = field(default_factory=ClipMetrics)  # Clip metrics

    def set_storage_attributes(self, url_prefix: str, storage_prefix: str) -> None:
        """Set storage URLs based on the provided prefix and suffixes.

        Args:
            url_prefix (str): The base URL prefix for storage.
            storage_prefix (str): The storage location prefix.
        """
        self.storage_url_prefix = url_prefix
        self.storage_prefix = storage_prefix
        self.storage_input_url = (
            f"{self.storage_url_prefix}/{self.storage_prefix}/{STORAGE_INPUT_SUFFIX}"
        )
        self.storage_output_url = (
            f"{self.storage_url_prefix}/{self.storage_prefix}/{STORAGE_OUTPUT_SUFFIX}"
        )
        self.storage_download_path = f"{self.storage_prefix}/{STORAGE_OUTPUT_SUFFIX}"


class ClipJobTable(Table[ClipJob]):
    """CLIP Job Management Table extending the base Table class.

    This class provides a pre-configured Table for CLIP job data
    with built-in schema and specialized methods.
    """

    def __init__(
        self, database_client: DatabaseClient, database_name: str, schema_name: str
    ):
        """Initialize the ClipJobTable.

        Args:
            database_client (DatabaseClient): Database client instance
            database_name (str): Name of the database
            schema_name (str): Name of the schema
        """
        super().__init__(
            database_client=database_client,
            dataclass_type=ClipJob,
            database_name=database_name,
            schema_name=schema_name,
            table_name=_TABLE_NAME,
            columns=_SCHEMA.copy(),  # Copy to prevent external modification
            description="CLIP job management and tracking table",
            app_role=COTALITY_APP_ROLE,
        )
        super().create(if_not_exists=True)

    @property
    def table(self) -> Table:
        """Get the Clip job table.

        Returns:
            Table: Clip job table
        """
        return self

    def select(
        self,
        where_clause: str = "",
        params: Optional[List[Any]] = None,
        order_by: Optional[str] = None,
        table_name: Optional[str] = None,
    ) -> List[T] | T | None:
        data = super().select(where_clause, params, order_by, table_name)

        # map the json values to the defined dataclasess
        def _map(j):
            j.step = ClipLookupAction(j.step)
            j.status = RunStatus(j.status)

            if j.clip_metrics:
                metrics = json.loads(j.clip_metrics)
                clip_metric = ClipMetrics(
                    input_metrics=InputMetrics(**metrics.get("input_metrics")),
                    clip_summary_metric=ClipSummaryMetrics(
                        **metrics.get("clip_summary_metric")
                    ),
                )
            else:
                clip_metric = ClipMetrics()

            j.clip_metrics = clip_metric
            return j

        if isinstance(data, list):
            return list([_map(j) for j in data])
        elif data:
            return _map(data)

    def init_job(self, input_table: str) -> None:
        """Initialize a clip job entry for a new input table.

        If an entry for the input table already exists, this function does nothing.

        Args:
            input_table (str): Input table name without database & schema
        """

    def update(self, clip_job: ClipJob, event_callback=None) -> None:
        """Update an existing ClipJob record in the database.

        Args:
            clip_job (ClipJob): The ClipJob instance to update.
            event_callback (callable, optional): Optional callback function to be called after update.
                The callback function should accept a single argument of type ClipJob.
        """
        # Update message if empty based on the step and status
        if not clip_job.message:
            clip_job.message = (
                f"Job status:{clip_job.status.name}, Step: {clip_job.step.name}."
            )
        clip_job.updated_at = datetime_to_int()
        available_memory_mb, total_memory_gb, cpu_count, _ = available_memory_and_cpu()
        clip_job.clip_metrics.clip_status_summary.available_memory_mb = (
            available_memory_mb
        )
        clip_job.clip_metrics.clip_status_summary.total_memory_gb = total_memory_gb
        clip_job.clip_metrics.clip_status_summary.cpu_count = cpu_count
        try:
            if callable(event_callback):
                event_callback(clip_job)
        except Exception as ex:
            logger.error("Error occurred in event callback: %s", ex)
        super().update(clip_job)

    def get_job_summary(self, input_tables: List[str]) -> pd.DataFrame:
        """Get the latest job summary for a specific input table.

        Args:
            input_tables (List[str]): The names of the input tables to filter jobs.
        Returns:
            pd.DataFrame: DataFrame containing the latest job summary for the input table.
        """
        quotation = self._database_client.config.string_quotation
        input_tables_str = ",".join(
            f"{quotation}{table}{quotation}" for table in input_tables
        )
        sql = _JOBS_SUMMARY_SQL[self._database_client.config.db_type].format(
            clip_job_table=self.table_name, input_tables=input_tables_str
        )
        return self._database_client.query_to_pandas(query_sql=sql)

    def get_latest_jobs(
        self, input_table: str, status: Optional[RunStatus | List[RunStatus]] = None
    ) -> List[ClipJob] | ClipJob | None:
        """Get the latest job for a specific input table within the last 4 days.

        Args:
            input_table (str): The name of the input table to filter jobs.
            status (Optional[RunStatus | List[RunStatus]], optional): The status or list of statuses to filter jobs.
                Defaults to None.

        Returns:
            List[ClipJob] | ClipJob | None: The latest ClipJob(s) for the input table.
        """
        four_days_ago = datetime_to_int(datetime.now() - timedelta(days=4))
        if status:
            if isinstance(status, list):
                status_placeholders = ",".join(["?" for _ in status])
                status_values = [s.value for s in status]
                jobs = self.select(
                    where_clause=f"{Columns.INPUT_TABLE} = ? AND {Columns.STATUS} IN ({status_placeholders}) AND {Columns.UPDATED_AT} >= ?",
                    params=[input_table] + status_values + [four_days_ago],
                    order_by=f"{Columns.UPDATED_AT} DESC",
                )
            else:
                jobs = self.select(
                    where_clause=f"{Columns.INPUT_TABLE} = ? AND {Columns.STATUS} = ? AND {Columns.UPDATED_AT} >= ?",
                    params=[input_table, status.value, four_days_ago],
                    order_by=f"{Columns.UPDATED_AT} DESC",
                )
        else:
            jobs = self.select(
                where_clause=f"{Columns.INPUT_TABLE} = ? AND {Columns.UPDATED_AT} >= ?",
                params=[input_table, four_days_ago],
                order_by=f"{Columns.UPDATED_AT} DESC",
            )

        return jobs

    def lock(self, input_table: str, minimum_idle_in_minutes: int = 60) -> ClipJob:
        """Lock a job record for update.

        Args:
            input_table (str): The input table name to identify the job to lock.
            minimum_idle_in_minutes (int): Minimum idle time in minutes to consider a job stale.
            If the current running job is idle for more than this duration, it will be considered stale
            this and a new job will be created. Default is 60 minutes.
        Returns:
            ClipJob: Current Clip job for this input table.
        """
        _, _, input_table_only = self._database_client.parse_table(input_table)
        logger.info("Requesting lock for clip input table: %s", input_table_only)
        running_and_failed_jobs = self.get_latest_jobs(
            input_table_only, status=[RunStatus.RUNNING, RunStatus.FAILED]
        )

        latest_job = None
        if running_and_failed_jobs and not isinstance(running_and_failed_jobs, list):
            latest_job = running_and_failed_jobs
        elif (
            running_and_failed_jobs
            and isinstance(running_and_failed_jobs, list)
            and len(running_and_failed_jobs) > 0
        ):
            latest_job = running_and_failed_jobs[0]

        now = datetime_to_int()
        # No running job for this table, start new one

        if not latest_job:
            job = self._new_job(input_table_only)
            self.insert(job)
        else:
            job = latest_job
            job.message = ""

            # See this job has stalled (no update for a while), mark it as running and return
            if (
                now - job.updated_at
            ) < minimum_idle_in_minutes * 60 and job.status == RunStatus.RUNNING:
                job = ClipJob(
                    input_table=input_table_only,
                    status=RunStatus.REJECTED,
                    updated_at=now,
                    started_at=now,
                    message=f"Previous job {job.job_id} is still running. New job rejected.",
                )
                self.insert(job)
            # Only allow to resume if the previous job is in polling state
            elif job.step < ClipLookupAction.POLL_JOB:
                job.status = RunStatus.FAILED
                job.message = f"Job {job.job_id} has stalled at step {job.step}. Marking it as failed."
                self.release(job)
                self.update(job)
                job = self._new_job(input_table_only)
                self.insert(job)
            elif (
                job.step >= ClipLookupAction.DOWNLOAD_RESULTS
                and job.status == RunStatus.FAILED
            ):
                job.status = RunStatus.RUNNING

        if job.status == RunStatus.RUNNING:
            logger.info(
                "Lock granted for job %s for input table %s. Step: %s",
                job.job_id,
                job.input_table,
                job.step,
            )
        else:
            logger.warning(
                "Lock denied for job %s for input table %s with status %s. Job details: %s",
                job.job_id,
                job.input_table,
                job.status,
                job.to_json(indent=2),
            )
        return job

    def release(self, clip_job: ClipJob):
        """Release a previously locked job by updating its status.

        Args:
            clip_job (ClipJob): The ClipJob instance to update.
        """

        def _to_datetime(value):
            """Convert various timestamp representations to a datetime object.

            Supported formats:
              - int/str epoch seconds (e.g. 1690000000)
              - int/str epoch milliseconds (e.g. 1690000000000)
              - YYYYMMDDHHMMSS strings (e.g. '20251022180539' or 20251022180539)
              - ISO 8601 string (fallback)
            Returns None if conversion fails.
            """
            if value is None:
                return None
            s = str(value)
            # YYYYMMDDHHMMSS
            if s.isdigit() and len(s) == 14:
                try:
                    return datetime.strptime(s, "%Y%m%d%H%M%S")
                except Exception:
                    pass
            # Try epoch numeric
            try:
                iv = int(float(s))
            except Exception:
                iv = None
            if iv is not None:
                # milliseconds vs seconds heuristic
                if iv > 10**12:  # likely milliseconds
                    return datetime.fromtimestamp(iv / 1000.0)
                else:
                    return datetime.fromtimestamp(iv)
            # ISO format fallback
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return None

        try:
            now = datetime_to_int()
            clip_job.updated_at = now
            clip_job.completed_at = now

            # Convert started and completed times to datetime and compute delta
            started_dt = _to_datetime(clip_job.started_at)
            completed_dt = _to_datetime(clip_job.completed_at)

            if started_dt is not None and completed_dt is not None:
                elapsed = int((completed_dt - started_dt).total_seconds())
            else:
                # Fallback numeric difference (best-effort)
                try:
                    elapsed = int(int(clip_job.completed_at) - int(clip_job.started_at))
                except Exception:
                    elapsed = 0

            # Ensure non-negative
            clip_job.elapsed_time_in_seconds = max(elapsed, 0)

            if clip_job.status in [RunStatus.RUNNING, RunStatus.SUCCEEDED]:
                logger.info(
                    "Released job %s for input table %s. Job details: %s",
                    clip_job.job_id,
                    clip_job.input_table,
                    clip_job.to_json(indent=2),
                )
            else:
                logger.error(
                    "Released job %s for input table %s with status %s. Job details: %s",
                    clip_job.job_id,
                    clip_job.input_table,
                    clip_job.status,
                    clip_job.to_json(indent=2),
                )
            self.update(clip_job)
        except Exception as e:
            logger.exception("Failed to release job %s: %s", clip_job.job_id, str(e))
            raise

    # ========== Private Methods ============
    def _new_job(self, input_table: str) -> ClipJob:
        """Create a new ClipJob instance.

        Args:
            input_table (str): The input table name for the new job.
        Returns:
            ClipJob: New ClipJob instance.
        """
        now = datetime_to_int()
        return ClipJob(
            input_table=input_table,
            step=ClipLookupAction.INITIALIZE,
            status=RunStatus.RUNNING,
            updated_at=now,
            started_at=now,
        )


# ============ Private +============
_TABLE_NAME = "clip_jobs"

# Private schema definition - class-level constant
_SCHEMA = [
    ColumnDefinition(
        name=Columns.JOB_ID.value,
        data_type=DataTypeEnum.TEXT,
        description="Job ID",
        nullable=False,
        primary_key=True,
    ),
    ColumnDefinition(
        name=Columns.INPUT_TABLE.value,
        data_type=DataTypeEnum.TEXT,
        description="Input table name",
        nullable=False,
    ),
    ColumnDefinition(
        name=Columns.STATUS.value,
        data_type=DataTypeEnum.TEXT,
        description="Job status",
        nullable=False,
    ),
    ColumnDefinition(
        name=Columns.STEP.value,
        data_type=DataTypeEnum.TEXT,
        description="Job step",
        nullable=False,
    ),
    # Timing
    ColumnDefinition(
        name=Columns.STARTED_AT.value,
        data_type=DataTypeEnum.INT64,
        description="Job start time",
        nullable=True,
    ),
    ColumnDefinition(
        name=Columns.COMPLETED_AT.value,
        data_type=DataTypeEnum.INT64,
        description="Job completion time",
        nullable=True,
    ),
    ColumnDefinition(
        name=Columns.UPDATED_AT.value,
        data_type=DataTypeEnum.INT64,
        description="Job update time",
        nullable=False,
    ),
    ColumnDefinition(
        name=Columns.ELAPSED_TIME_IN_SECONDS.value,
        data_type=DataTypeEnum.INT64,
        description="Job elapsed time in seconds",
        nullable=True,
    ),
    # Message
    ColumnDefinition(
        name=Columns.MESSAGE.value,
        data_type=DataTypeEnum.TEXT,
        description="Job message",
        nullable=True,
    ),
    ColumnDefinition(
        name=Columns.MESSAGE_DETAILS.value,
        data_type=DataTypeEnum.TEXT,
        description="Job message details",
        nullable=True,
    ),
    # Clip Job
    ColumnDefinition(
        name=Columns.CLIP_JOB_ID.value,
        data_type=DataTypeEnum.TEXT,
        description="Clip job ID",
        nullable=True,
    ),
    ColumnDefinition(
        name=Columns.CLIP_JOB_RAW_STATUS.value,
        data_type=DataTypeEnum.TEXT,
        description="Raw Clip job raw status",
        nullable=True,
    ),
    ColumnDefinition(
        name=Columns.CLIP_JOB_STATUS.value,
        data_type=DataTypeEnum.TEXT,
        description="Raw Clip job Enum status",
        nullable=True,
    ),
    # Storage
    ColumnDefinition(
        name=Columns.STORAGE_URL_PREFIX.value,
        data_type=DataTypeEnum.TEXT,
        description="Storage URL prefix",
        nullable=True,
    ),
    ColumnDefinition(
        name=Columns.STORAGE_PREFIX.value,
        data_type=DataTypeEnum.TEXT,
        description="Storage location",
        nullable=True,
    ),
    ColumnDefinition(
        name=Columns.STORAGE_INPUT_URL.value,
        data_type=DataTypeEnum.TEXT,
        description="Storage input URL",
        nullable=True,
    ),
    ColumnDefinition(
        name=Columns.STORAGE_OUTPUT_URL.value,
        data_type=DataTypeEnum.TEXT,
        description="Storage output URL",
        nullable=True,
    ),
    ColumnDefinition(
        name=Columns.STORAGE_DOWNLOAD_PATH.value,
        data_type=DataTypeEnum.TEXT,
        description="Storage download path",
        nullable=True,
    ),
    # Metrics
    ColumnDefinition(
        name=Columns.CLIP_METRICS.value,
        data_type=DataTypeEnum.TEXT,
        description="Clip metrics",
        nullable=True,
    ),
]


# ========== CLIP JOBS TABLE SUMMARY SQL ============
_JOB_SUMMARY_SNOWFLAKE_SQL = """
SELECT
      {input_table} as input_table_name,
      {status} AS last_clip_run_status,
      {completed_at} AS last_clip_run_date
FROM {{clip_job_table}}
WHERE {input_table} IN ({{input_tables}})
QUALIFY ROW_NUMBER()
    OVER (
    PARTITION BY {input_table}
    ORDER BY {completed_at} DESC NULLS LAST
    ) = 1;
""".strip().format(
    input_table=Columns.INPUT_TABLE.value,
    status=Columns.STATUS.value,
    completed_at=Columns.COMPLETED_AT.value,
)

_JOB_SUMMARY_BIGQUERY_SQL = """
WITH RankedJobs AS (
  SELECT
    {input_table} AS input_table_name,
    {status} AS last_clip_run_status,
    {completed_at} AS last_clip_run_date,
    ROW_NUMBER() OVER (
      PARTITION BY {input_table}
      ORDER BY {completed_at} DESC NULLS LAST
    ) AS rn
  FROM
    {{clip_job_table}}
  WHERE
    {input_table} IN ({{input_tables}})
)
SELECT
  input_table_name,
  last_clip_run_status,
  last_clip_run_date
FROM
  RankedJobs
WHERE
  rn = 1;
""".strip().format(
    input_table=Columns.INPUT_TABLE.value,
    status=Columns.STATUS.value,
    completed_at=Columns.COMPLETED_AT.value,
)

_JOBS_SUMMARY_SQL = {
    PlatformType.SNOWFLAKE: _JOB_SUMMARY_SNOWFLAKE_SQL,
    PlatformType.DATABRICKS: _JOB_SUMMARY_SNOWFLAKE_SQL,
    PlatformType.BIGQUERY: _JOB_SUMMARY_BIGQUERY_SQL,
}

# ========== CLIP METRIC BY JOB ID SQL ============
_CLIP_METRIC_BY_JOB_ID_SNOWFLAKE_SQL = """
SELECT {clip_metric} FROM {{full_table_name}} WHERE job_id = ?
""".strip().format(
    clip_metric=Columns.CLIP_METRICS.value,
)

_CLIP_METRIC_BY_JOB_ID_SQL = {
    PlatformType.SNOWFLAKE: _CLIP_METRIC_BY_JOB_ID_SNOWFLAKE_SQL,
    PlatformType.DATABRICKS: _CLIP_METRIC_BY_JOB_ID_SNOWFLAKE_SQL,
    PlatformType.BIGQUERY: _CLIP_METRIC_BY_JOB_ID_SNOWFLAKE_SQL,
}
