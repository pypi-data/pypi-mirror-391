# Copyright 2025 f0reachARR
# Licensed under the Apache License, Version 2.0

"""Example test to demonstrate the MermaidGanttGenerator functionality."""

from colcon_gha_visualize.mermaid_generator import MermaidGanttGenerator
import time


def test_basic_chart_generation():
    """Test basic chart generation with sequential jobs."""
    generator = MermaidGanttGenerator()

    base_time = time.time()

    # Add sequential jobs
    generator.add_job("job1", base_time, base_time + 5, "SUCCESS")
    generator.add_job("job2", base_time + 5, base_time + 10, "SUCCESS")
    generator.add_job("job3", base_time + 10, base_time + 15, "FAILED")

    chart = generator.generate_chart("Sequential Jobs")
    print("\n=== Sequential Jobs Chart ===")
    print(chart)

    stats = generator.get_parallelism_stats()
    print(f"\nStats: {stats}")
    assert stats["max_parallelism"] == 1
    assert stats["lane_count"] == 1


def test_parallel_jobs():
    """Test chart generation with parallel jobs."""
    generator = MermaidGanttGenerator()

    base_time = time.time()

    # Add parallel jobs that overlap
    generator.add_job("pkg_a", base_time, base_time + 10, "SUCCESS")
    generator.add_job("pkg_b", base_time + 2, base_time + 12, "SUCCESS")
    generator.add_job("pkg_c", base_time + 3, base_time + 8, "SUCCESS")
    generator.add_job("pkg_d", base_time + 5, base_time + 15, "FAILED")
    generator.add_job("pkg_e", base_time + 11, base_time + 20, "SUCCESS")

    chart = generator.generate_chart("Parallel Jobs")
    print("\n=== Parallel Jobs Chart ===")
    print(chart)

    stats = generator.get_parallelism_stats()
    print(f"\nStats: {stats}")
    print(f"Max parallelism: {stats['max_parallelism']}")
    print(f"Lanes needed: {stats['lane_count']}")


def test_complex_scenario():
    """Test with a more complex scenario."""
    generator = MermaidGanttGenerator()

    base_time = time.time()

    # Simulate a realistic build scenario
    jobs = [
        ("std_msgs", base_time, base_time + 5, "SUCCESS"),
        ("geometry_msgs", base_time + 1, base_time + 6, "SUCCESS"),
        ("sensor_msgs", base_time + 1.5, base_time + 7, "SUCCESS"),
        ("nav_msgs", base_time + 6, base_time + 10, "SUCCESS"),
        ("tf2", base_time + 2, base_time + 8, "SUCCESS"),
        ("tf2_ros", base_time + 8, base_time + 14, "SUCCESS"),
        ("nav_core", base_time + 10, base_time + 16, "SUCCESS"),
        ("costmap_2d", base_time + 3, base_time + 12, "FAILED"),
        ("move_base", base_time + 16, base_time + 22, "ABORTED"),
    ]

    for job_id, start, end, result in jobs:
        generator.add_job(job_id, start, end, result)

    chart = generator.generate_chart("ROS Package Build")
    print("\n=== Complex Build Scenario ===")
    print(chart)

    # Save to file
    generator.save_to_file("/tmp/build_timeline.md", "ROS Package Build")
    print("\nChart saved to /tmp/build_timeline.md")

    stats = generator.get_parallelism_stats()
    print(f"\nStats: {stats}")


if __name__ == "__main__":
    print("Testing MermaidGanttGenerator...")

    test_basic_chart_generation()
    print("\n" + "=" * 60)

    test_parallel_jobs()
    print("\n" + "=" * 60)

    test_complex_scenario()
    print("\n" + "=" * 60)

    print("\nAll tests completed!")
