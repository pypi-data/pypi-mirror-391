# Copyright 2025 f0reachARR
# Licensed under the Apache License, Version 2.0

from colcon_core.event_handler import EventHandlerExtensionPoint
from colcon_core.event.job import JobEnded
from colcon_core.event.job import JobStarted
from colcon_core.event_reactor import EventReactorShutdown
from colcon_core.plugin_system import satisfies_version
from colcon_core.subprocess import SIGINT_RESULT
import time
import os
from enum import Enum
from .mermaid_generator import MermaidGanttGenerator


class JobResult(Enum):
    SUCCESS = 0
    TEST_FAILURE = 1
    ABORTED = 2
    FAILED = 3


class VisualizeEventHandler(EventHandlerExtensionPoint):
    def __init__(self):
        super().__init__()
        satisfies_version(EventHandlerExtensionPoint.EXTENSION_POINT_VERSION, "^1.0")
        self._start_times = {}
        self._end_times = {}
        self._end_results = {}
        self._generator = MermaidGanttGenerator()

    def __call__(self, event):
        data = event[0]

        if isinstance(data, JobStarted):
            self._start_times[data.identifier] = time.monotonic()
        elif isinstance(data, JobEnded):
            self._end_times[data.identifier] = time.monotonic()
            self._end_results[data.identifier] = data.rc
            if not data.rc:
                self._end_results[data.identifier] = JobResult.SUCCESS
            elif data.rc == SIGINT_RESULT:
                self._end_results[data.identifier] = JobResult.ABORTED
            else:
                self._end_results[data.identifier] = JobResult.FAILED

            # Add job to generator
            start_time = self._start_times.get(data.identifier)
            end_time = self._end_times.get(data.identifier)
            result = self._end_results.get(data.identifier)

            if start_time and end_time and result:
                self._generator.add_job(
                    data.identifier,
                    start_time,
                    end_time,
                    result.name if isinstance(result, JobResult) else str(result),
                )
        elif isinstance(data, EventReactorShutdown):
            self._output_chart()

    def _output_chart(self):
        """Output the chart to console and GITHUB_STEP_SUMMARY if available."""
        chart = self._generator.generate_chart(title="Colcon Build Timeline")

        # Output to GitHub Step Summary if environment variable is set
        github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if github_step_summary:
            try:
                with open(github_step_summary, "a") as f:
                    f.write("\n## Build Timeline\n\n")
                    f.write("```mermaid\n")
                    f.write(chart)
                    f.write("\n```\n\n")

                    # Add statistics
                    stats = self._generator.get_parallelism_stats()
                    f.write("### Build Statistics\n\n")
                    f.write(f"- **Max Parallelism**: {stats['max_parallelism']}\n")
                    f.write(f"- **Lanes Used**: {stats['lane_count']}\n")
                    f.write(f"- **Total Jobs**: {len(self._generator.jobs)}\n\n")

                print(f"Chart written to {github_step_summary}")
            except Exception as e:
                print(f"Warning: Failed to write to GITHUB_STEP_SUMMARY: {e}")
