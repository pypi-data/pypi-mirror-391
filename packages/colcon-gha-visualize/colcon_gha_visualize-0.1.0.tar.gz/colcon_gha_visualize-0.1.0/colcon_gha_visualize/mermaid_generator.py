# Copyright 2025 f0reachARR
# Licensed under the Apache License, Version 2.0

from typing import Dict, List


class JobInfo:
    """Job execution information."""

    def __init__(
        self, identifier: str, start_time: float, end_time: float, result: str
    ):
        self.identifier = identifier
        self.start_time = start_time
        self.end_time = end_time
        self.result = result
        self.duration = end_time - start_time


class MermaidGanttGenerator:
    """Generate Mermaid gantt chart from job execution data."""

    def __init__(self):
        self.jobs: List[JobInfo] = []

    def add_job(self, identifier: str, start_time: float, end_time: float, result: str):
        """Add a job to the timeline."""
        job = JobInfo(identifier, start_time, end_time, result)
        self.jobs.append(job)

    def _allocate_lanes(self) -> Dict[str, int]:
        """
        Allocate lanes for jobs to avoid overlapping.
        Returns a dictionary mapping job identifier to lane number.
        """
        if not self.jobs:
            return {}

        # Sort jobs by start time
        sorted_jobs = sorted(self.jobs, key=lambda j: j.start_time)

        # Track end time of each lane
        lane_end_times: List[float] = []
        job_to_lane: Dict[str, int] = {}

        for job in sorted_jobs:
            # Find the first available lane
            assigned_lane = None
            for lane_idx, lane_end_time in enumerate(lane_end_times):
                if job.start_time >= lane_end_time:
                    # This lane is available
                    assigned_lane = lane_idx
                    lane_end_times[lane_idx] = job.end_time
                    break

            if assigned_lane is None:
                # Need a new lane
                assigned_lane = len(lane_end_times)
                lane_end_times.append(job.end_time)

            job_to_lane[job.identifier] = assigned_lane

        return job_to_lane

    def _format_time(self, timestamp: float, base_time: float) -> str:
        """Convert timestamp to HH:MM:SS format relative to base_time."""
        seconds = int(timestamp - base_time)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _get_task_status(self, result: str) -> str:
        """Map job result to Mermaid gantt chart status."""
        status_map = {
            "SUCCESS": "done",
            "FAILED": "active",
            "ABORTED": "crit",
            "TEST_FAILURE": "active",
        }
        return status_map.get(result, "active")

    def generate_chart(self, title: str = "Job Execution Timeline") -> str:
        """
        Generate Mermaid gantt chart code.

        Returns:
            Mermaid chart markdown string
        """
        if not self.jobs:
            return "gantt\n    title No Jobs\n"

        # Allocate lanes
        job_to_lane = self._allocate_lanes()

        # Get base time (earliest start)
        base_time = min(job.start_time for job in self.jobs)

        # Group jobs by lane
        lanes: Dict[int, List[JobInfo]] = {}
        for job in self.jobs:
            lane = job_to_lane[job.identifier]
            if lane not in lanes:
                lanes[lane] = []
            lanes[lane].append(job)

        # Generate Mermaid code
        lines = [
            "gantt",
            f"    title {title}",
            "    dateFormat HH:mm:ss",
            "    axisFormat %H:%M:%S",
        ]

        # Add sections (lanes) and tasks
        for lane_idx in sorted(lanes.keys()):
            lines.append(f"    section Lane {lane_idx + 1}")

            # Sort jobs in this lane by start time
            lane_jobs = sorted(lanes[lane_idx], key=lambda j: j.start_time)

            for job in lane_jobs:
                start_time = self._format_time(job.start_time, base_time)
                duration_ms = int(job.duration * 1000)
                status = self._get_task_status(job.result)

                # Mermaid gantt chart task format:
                # task_name : [status,] start_time, duration
                lines.append(
                    f"    {job.identifier} : {status}, {start_time}, {duration_ms}ms"
                )

        return "\n".join(lines)

    def save_to_file(self, filepath: str, title: str = "Job Execution Timeline"):
        """Save the generated chart to a file."""
        chart = self.generate_chart(title)

        # Wrap in markdown code block
        content = f"```mermaid\n{chart}\n```\n"

        with open(filepath, "w") as f:
            f.write(content)

    def get_parallelism_stats(self) -> Dict[str, int]:
        """
        Calculate parallelism statistics.

        Returns:
            Dictionary with max_parallelism and lane_count
        """
        if not self.jobs:
            return {"max_parallelism": 0, "lane_count": 0}

        job_to_lane = self._allocate_lanes()
        lane_count = max(job_to_lane.values()) + 1 if job_to_lane else 0

        # Calculate maximum parallelism at any point in time
        time_points = []
        for job in self.jobs:
            time_points.append((job.start_time, 1))  # Job starts
            time_points.append((job.end_time, -1))  # Job ends

        time_points.sort()
        max_parallelism = 0
        current_parallelism = 0

        for _, delta in time_points:
            current_parallelism += delta
            max_parallelism = max(max_parallelism, current_parallelism)

        return {"max_parallelism": max_parallelism, "lane_count": lane_count}
