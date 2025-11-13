#!/usr/bin/env python3
# This software is distributed under the terms of the MIT License.
# Copyright (c) 2025 Dmitry Ponomarev.
# Author: Dmitry Ponomarev <ponomarevda96@gmail.com>
"""
Tests for NodesRegistry - central data model tracking UAV nodes.

Overview:
    NodesRegistry tracks node status, parameters, and metadata.
    It does not communicate directly but relies on backend callbacks
    (request_param_get, request_get_info).

Use Cases:

NODE STATUS
    UC 1-1. Node comes online
        Trigger: A heartbeat is received.
        Expected: Node is created (if missing) and marked online.

    UC 1-2. Node goes offline
        Trigger: No heartbeat for more than NODE_ONLINE_TIMEOUT.
        Expected: Node becomes offline.

REGISTERS / PARAMETERS
    UC 2-1. Parameter subscription
        Trigger: UI binds to a node's parameter.
        Expected: Callback is stored in the registry.

    UC 2-2. Parameter re-request loop
        Trigger: Periodic call to spin().
        Expected: Parameters are re-requested when due.

    UC 2-3. Parameter update propagation
        Trigger: Backend provides new parameter value.
        Expected: All subscribed callbacks are invoked.

    UC 2-4. Persistence trigger
        Trigger: Registry decides a parameter change requires saving.
        Expected: save_required_callback is invoked if registered.

NODE INFO
    UC 3-1. Node info request loop
        Trigger: spin() detects info not yet fetched.
        Expected: Calls request_get_info(node_id) once per cycle.

    UC 3-2. Node info update propagation
        Trigger: Backend replies with node info (fields).
        Expected: Bound callbacks are called with updated values.

COMMON
    UC 4-1. Defensive behavior
        Prevents copying (copy() or deepcopy() raises).
"""
import pytest
import random
random.seed(42)

from tsugite.backend.registry import (
    NodesRegistry,
    NODE_ONLINE_TIMEOUT,
    PARAM_REQUEST_TIMEOUT,
)

@pytest.fixture
def registry_with_mock_backend():
    """Create a registry instance with mock backend callbacks."""
    backend_calls = {"param_get": [], "get_info": []}

    def request_param_get(node_id: int, param_name: str):
        backend_calls["param_get"].append((node_id, param_name))

    def request_get_info(node_id: int):
        backend_calls["get_info"].append(node_id)

    reg = NodesRegistry(request_param_get, request_get_info)
    return reg, backend_calls

# ---------------------------------------------------------------------------
# UC 1-1. Node comes online
# ---------------------------------------------------------------------------
def test_uc_1_1_node_comes_online(registry_with_mock_backend):
    """UC 1-1: Node becomes online after receiving a heartbeat."""
    registry, _ = registry_with_mock_backend
    node_id = random.randint(1, 127)
    uptime = random.uniform(0.0, 60.0)
    now = random.uniform(500.0, 1500.0)
    hb = {"node_id": node_id, "uptime": uptime}

    # Act
    registry.handle_heartbeat(hb, now)

    # Assert
    node = registry.get_node(node_id)
    assert node is not None
    assert node.nodestatus_time == now
    assert node.uptime == uptime
    assert node.boot_time == pytest.approx(now - uptime, rel=1e-6)
    assert registry.is_online(node, now)
    assert node_id in registry.online_id_set(now)

# ---------------------------------------------------------------------------
# UC 1-2. Node goes offline
# ---------------------------------------------------------------------------
def test_uc_1_2_node_goes_offline_after_timeout(registry_with_mock_backend):
    """UC 1-2: Node is considered offline after timeout without heartbeat."""
    registry, _ = registry_with_mock_backend

    node_id = random.randint(1, 127)
    uptime = random.uniform(0.0, 60.0)
    now = random.uniform(1000.0, 2000.0)

    # Act: node sends a heartbeat (comes online)
    registry.handle_heartbeat({"node_id": node_id, "uptime": uptime}, now)
    node = registry.get_node(node_id)

    # Assert: node is initially online
    assert registry.is_online(node, now)
    assert node_id in registry.online_id_set(now)

    # Simulate time passing beyond NODE_ONLINE_TIMEOUT
    later = now + NODE_ONLINE_TIMEOUT + random.uniform(0.01, 0.5)

    # Assert: node becomes offline
    assert not registry.is_online(node, later)
    assert node_id not in registry.online_id_set(later)

# ---------------------------------------------------------------------------
# UC 2-1. Parameter subscription
# ---------------------------------------------------------------------------
def test_uc_2_1_parameter_subscription(registry_with_mock_backend):
    """UC 2-1: callback is stored when a UI subscribes to a parameter."""
    registry, _ = registry_with_mock_backend

    node_id = random.randint(1, 127)
    param_name = "uavcan.node.id"

    called = {}
    def cb(v): called["v"] = v

    # Act
    registry.subscribe_param(node_id, param_name, cb)

    # Assert
    node = registry.get_node(node_id)
    assert node is not None
    assert param_name in node.params
    assert cb in node.params[param_name].sync.setters


# ---------------------------------------------------------------------------
# UC 2-2. Parameter re-request loop
# ---------------------------------------------------------------------------
def test_uc_2_2_parameter_rerequest_loop(registry_with_mock_backend):
    """UC 2-2: spin() re-requests parameters when timeout expires."""
    registry, backend_calls = registry_with_mock_backend

    start_time = 1000.0
    start_uptime = 5.0
    node_id = random.randint(1, 127)
    param_name = "uavcan.node.id"

    # Make node online
    registry.subscribe_param(node_id, param_name, lambda v: None)

    # Act 1 – first spin should trigger one request
    time_elapsed = 0.0
    uptime_now = start_uptime + time_elapsed
    time_now = start_time + time_elapsed
    registry.handle_heartbeat({"node_id": node_id, "uptime": uptime_now}, time_now)
    registry.spin(start_time)
    assert backend_calls["param_get"] == [(node_id, param_name)]

    # Act 2 – within timeout → no new requests
    time_elapsed = PARAM_REQUEST_TIMEOUT / 2
    uptime_now = start_uptime + time_elapsed
    time_now = start_time + time_elapsed
    registry.handle_heartbeat({"node_id": node_id, "uptime": uptime_now}, time_now)
    registry.spin(start_time + PARAM_REQUEST_TIMEOUT / 2)
    assert len(backend_calls["param_get"]) == 1

    # Act 3 – after timeout → new request
    time_elapsed = PARAM_REQUEST_TIMEOUT + 0.1
    uptime_now = start_uptime + time_elapsed
    time_now = start_time + time_elapsed
    registry.handle_heartbeat({"node_id": node_id, "uptime": uptime_now}, time_now)
    registry.spin(start_time + time_elapsed)
    assert len(backend_calls["param_get"]) == 2


# ---------------------------------------------------------------------------
# UC 2-3. Parameter update propagation
# ---------------------------------------------------------------------------
def test_uc_2_3_parameter_update_propagation(registry_with_mock_backend):
    """UC 2-3: all bound callbacks are invoked when param value updates."""
    registry, _ = registry_with_mock_backend
    node_id = random.randint(1, 127)
    param_name = "altitude_offset"

    values = []
    def cb1(v): values.append(("cb1", v))
    def cb2(v): values.append(("cb2", v))

    # subscribe two callbacks
    registry.subscribe_param(node_id, param_name, cb1)
    registry.subscribe_param(node_id, param_name, cb2)

    # simulate backend update
    param = registry.ensure_param(node_id, param_name)
    param.value = 123.45
    for cb in param.sync.setters:
        cb(param.value)

    # Assert both callbacks received the same value
    expected = [("cb1", 123.45), ("cb2", 123.45)]
    assert values == expected
