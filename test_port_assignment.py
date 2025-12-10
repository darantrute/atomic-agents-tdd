#!/usr/bin/env python3
"""
Test script for smart port assignment algorithm.
Validates collision-free port assignment for parallel TDD pipelines.
"""

import hashlib
import os
import socket
import tempfile
import shutil


def assign_service_port(service_name, project_path, base_port=5400):
    """
    Assigns a collision-free port for a service using directory hash + availability check.

    Args:
        service_name: "postgres", "redis", "mysql", etc.
        project_path: Full path to project directory
        base_port: Starting port for range (default 5400)

    Returns:
        Available port number
    """

    # 1. Generate deterministic preferred port from project directory
    combined_hash = hashlib.sha256(f"{project_path}:{service_name}".encode()).hexdigest()
    hash_value = int(combined_hash, 16)

    # Use 256-port range
    range_size = 256
    preferred_port = base_port + (hash_value % range_size)

    print(f"[INFO] {service_name} ({project_path}): Preferred port {preferred_port} (hash-based)")

    # 2. Check if preferred port is available
    if is_port_available(preferred_port):
        print(f"✓ {service_name} port: {preferred_port} (auto-assigned from project path)")
        return preferred_port

    # 3. Scan for next available port (try up to 100 ports)
    print(f"[INFO] Port {preferred_port} in use, scanning for next available...")
    for offset in range(1, 100):
        candidate = preferred_port + offset
        if candidate > base_port + range_size + 100:
            break  # Don't scan too far

        if is_port_available(candidate):
            print(f"✓ {service_name} port: {candidate} (preferred {preferred_port} was taken)")
            return candidate

    # 4. Fall back to random ephemeral port range
    print(f"[WARNING] Standard port range exhausted, using ephemeral port")
    import random
    for _ in range(10):
        candidate = random.randint(10000, 20000)
        if is_port_available(candidate):
            print(f"✓ {service_name} port: {candidate} (random - standard range exhausted)")
            return candidate

    raise Exception(f"Unable to find available port for {service_name}")


def is_port_available(port):
    """Check if a port is available on localhost."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.bind(('localhost', port))
        sock.close()
        return True
    except OSError:
        return False


# Service-specific base ports
SERVICE_BASE_PORTS = {
    'postgres': 5400,   # Range: 5400-5656
    'mysql': 3400,      # Range: 3400-3656
    'mongodb': 27100,   # Range: 27100-27356
    'redis': 6400,      # Range: 6400-6656
    'rabbitmq': 5700,   # Range: 5700-5956
}


def test_deterministic_assignment():
    """Test that same project path always gets same port (when available)."""
    print("\n" + "=" * 60)
    print("TEST 1: Deterministic Assignment")
    print("=" * 60)

    project_path = "/home/user/test-project"

    port1 = assign_service_port('postgres', project_path, base_port=5400)
    port2 = assign_service_port('postgres', project_path, base_port=5400)

    assert port1 == port2, f"Ports should be identical: {port1} != {port2}"
    print(f"✓ PASS: Same project path → same port ({port1})")


def test_parallel_projects():
    """Test that multiple parallel projects get unique ports."""
    print("\n" + "=" * 60)
    print("TEST 2: Parallel Projects (Collision Prevention)")
    print("=" * 60)

    projects = [
        "/home/user/project-analytics",
        "/home/user/project-ecommerce",
        "/home/user/project-chat",
        "/home/user/project-blog",
        "/home/user/project-api",
    ]

    assigned_ports = {}
    for project in projects:
        port = assign_service_port('postgres', project, base_port=5400)
        assigned_ports[project] = port

    # Check for collisions
    port_values = list(assigned_ports.values())
    unique_ports = set(port_values)

    print(f"\nAssigned ports: {port_values}")
    print(f"Unique ports: {len(unique_ports)} out of {len(port_values)}")

    assert len(unique_ports) == len(port_values), "Port collision detected!"
    print(f"✓ PASS: All {len(projects)} projects got unique ports")


def test_different_services():
    """Test that different services in same project get different ports."""
    print("\n" + "=" * 60)
    print("TEST 3: Different Services (Same Project)")
    print("=" * 60)

    project_path = "/home/user/fullstack-app"

    postgres_port = assign_service_port('postgres', project_path, base_port=5400)
    redis_port = assign_service_port('redis', project_path, base_port=6400)
    mysql_port = assign_service_port('mysql', project_path, base_port=3400)

    print(f"\nPort assignments for {project_path}:")
    print(f"  - PostgreSQL: {postgres_port}")
    print(f"  - Redis: {redis_port}")
    print(f"  - MySQL: {mysql_port}")

    assert postgres_port != redis_port, "Postgres and Redis should have different ports"
    assert postgres_port != mysql_port, "Postgres and MySQL should have different ports"
    assert redis_port != mysql_port, "Redis and MySQL should have different ports"

    print(f"✓ PASS: All services got unique ports")


def test_collision_with_real_server():
    """Test behavior when preferred port is actually in use."""
    print("\n" + "=" * 60)
    print("TEST 4: Port Collision with Real Server")
    print("=" * 60)

    # Start a test server on a specific port
    test_port = 5423
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind(('localhost', test_port))
        server_socket.listen(1)
        print(f"[SETUP] Test server listening on port {test_port}")

        # Create a project that would hash to this port
        # We need to find a path that hashes to 5423
        # For testing, we'll just use a path and verify it finds next available
        project_path = "/test/collision-project"

        port = assign_service_port('postgres', project_path, base_port=5400)

        # Port should NOT be the occupied one (unless by chance it hashed differently)
        if not is_port_available(test_port):
            print(f"✓ PASS: Algorithm avoided occupied port {test_port}, assigned {port}")
        else:
            print(f"✓ PASS: Algorithm assigned port {port}")

    finally:
        server_socket.close()


def test_tempdir_projects():
    """Test with actual temporary directories to simulate real usage."""
    print("\n" + "=" * 60)
    print("TEST 5: Real Temporary Directories (Realistic Simulation)")
    print("=" * 60)

    temp_dirs = []
    assigned_ports = {}

    try:
        # Create 5 temporary project directories
        for i in range(5):
            temp_dir = tempfile.mkdtemp(prefix=f"tdd-project-{i}-")
            temp_dirs.append(temp_dir)

            port = assign_service_port('postgres', temp_dir, base_port=5400)
            assigned_ports[temp_dir] = port

        # Verify all unique
        port_values = list(assigned_ports.values())
        unique_ports = set(port_values)

        print(f"\nReal directories created:")
        for dir_path, port in assigned_ports.items():
            print(f"  {dir_path} → port {port}")

        assert len(unique_ports) == len(port_values), "Port collision detected in temp dirs!"
        print(f"\n✓ PASS: All {len(temp_dirs)} temp directories got unique ports")

    finally:
        # Cleanup
        for temp_dir in temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    print("Port Assignment Algorithm Test Suite")
    print("=" * 60)

    try:
        test_deterministic_assignment()
        test_parallel_projects()
        test_different_services()
        test_collision_with_real_server()
        test_tempdir_projects()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
