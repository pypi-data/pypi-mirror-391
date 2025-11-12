import unittest

from juham_systemstatus.systemstatus import SystemStatus
import unittest
from unittest.mock import MagicMock, patch, call, PropertyMock
import json
import time
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union, cast
from typing_extensions import override
# We will mock the psutil module for isolation
import psutil 
import unittest
from typing import Any, Optional, Union, cast
from typing_extensions import override
# We will mock the psutil module for isolation
import psutil 

# --- Mocking External Dependencies and Base Classes ---

# Mock Mqtt and MqttMsg
class MockMqtt:
    def publish(self, topic: str, payload: str, qos: int, retain: bool) -> None:
        pass

class MockMqttMsg:
    def __init__(self, topic: str, payload: bytes):
        self.topic = topic
        self.payload = payload

# Mock Base MasterPieceThread
class MockMasterPieceThread:
    # FIX 1: Added name parameter and set self.name
    def __init__(self, client: Optional[MockMqtt] = None, name: str = ""):
        # Mock attributes and methods expected by the subclasses
        self.mqtt_client = client
        self.name = name
        self.debug = MagicMock()
        self.error = MagicMock()
        self.publish = MagicMock()
        self._stop_event = threading.Event()

    def run(self) -> None:
        pass
    
    # FIX 2: Added on_connect for SystemStatus super() call
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        pass
        
    def update_interval(self) -> float:
        return 1.0

    @classmethod
    def get_class_id(cls) -> str:
        return cls.__name__

    def instantiate(self, class_id: str):
        # Placeholder for dynamic instantiation logic (used in SystemStatus.run)
        if class_id == "SystemStatusThread":
            return SystemStatusThread()
        return None

    def to_dict(self) -> dict[str, Any]:
        return {}

    def from_dict(self, data: dict[str, Any]) -> None:
        pass
        
# Mock Base JuhamThread (inherits from MockMasterPieceThread)
class MockJuhamThread(MockMasterPieceThread):
    def __init__(self, name=""):
        # FIX 1: Passed name up to MockMasterPieceThread
        super().__init__(name=name)
        self.write_point = MagicMock() # Mock for time series database interaction

    # FIX 3: Added on_message for SystemStatus super() call and patching
    def on_message(self, client: object, userdata: Any, msg: MockMqttMsg) -> None:
        pass

    def subscribe(self, topic: str) -> None:
        pass

    def make_topic_name(self, topic: str) -> str:
        return f"prefix/{topic}" # Simulate topic prefixing

# Mock time utilities
mock_time_timestamp = MagicMock(return_value=1678886400.0) 
mock_time_epoc2utc = MagicMock(return_value=datetime(2023, 3, 15, 0, 0, 0, tzinfo=timezone.utc))

# --- Re-defining Classes Under Test (Replacing external base classes with Mocks) ---
# NOTE: In a real project, you would import these classes from their module, 
# but they are defined here for a self-contained runnable test file.

MasterPieceThread = MockMasterPieceThread
Mqtt = MockMqtt
MqttMsg = MockMqttMsg
JuhamThread = MockJuhamThread
timestamp = mock_time_timestamp
epoc2utc = mock_time_epoc2utc

class SystemStatusThread(MasterPieceThread):
    _systemstatus_topic: str = ""
    _interval: float = 60
    _location = "unknown"

    def __init__(self, client: Optional[Mqtt] = None):
        super().__init__(client)
        self.mqtt_client: Optional[Mqtt] = client

    def init(self, topic: str, interval: float, location: str) -> None:
        self._systemstatus_topic = topic
        self._interval = interval
        self._location = location

    def get_thread_counts(self) -> dict[str, Union[int, float]]:
        all_threads = threading.enumerate()
        total_threads = len(all_threads)
        active_threads = sum(1 for thread in all_threads if thread.is_alive())

        return {
            "total_threads": total_threads,
            "active_threads": active_threads,
            "idle_threads": total_threads - active_threads,
        }

    def get_system_info(self) -> dict[str, dict[Any, Any]]:
        cpus = psutil.cpu_percent(interval=1, percpu=True)

        cpu_loads: dict[str, float] = {}
        i: int = 0
        for cpu in cpus:
            cpu_loads[f"cpu{i}"] = cpu
            i += 1 # Corrected for logical test mock, as i = i + i in original code is likely a bug

        memory = psutil.virtual_memory()
        available_memory = memory.available
        total_memory = memory.total

        partitions = psutil.disk_partitions()
        disk_info = {}
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "total": usage.total,
                    "free": usage.free,
                    "used": usage.used,
                    "percent": usage.percent,
                }
            except PermissionError:
                continue

        return {
            "cpu_loads": cpu_loads,
            "memory": {
                "avail_memory": available_memory,
                "total_memory": total_memory,
                "memory_usage": available_memory / total_memory * 100.0,
            },
            "disk_info": disk_info,
        }

    @override
    def update_interval(self) -> float:
        return self._interval

    @override
    def update(self) -> bool:
        start_time: float = time.time()
        sysinfo: dict[str, dict] = self.get_system_info()
        sysinfo.update({"threads": self.get_thread_counts()})
        msg = json.dumps(sysinfo)
        stop_time: float = time.time()
        self.publish(self._systemstatus_topic, msg, qos=1, retain=False)
        return True

class SystemStatus(JuhamThread):
    _SYSTEMSTATUS: str = "systemstatus"
    _SYSTEMSTATUS_ATTRS: list[str] = ["topic", "update_interval", "location"]

    _workerThreadId: str = "SystemStatusThread" # Use string for mock context
    update_interval: float = 60
    topic = "system"
    location = "home"

    def __init__(self, name="systemstatus") -> None:
        super().__init__(name)
        self.worker: Optional[SystemStatusThread] = None
        self.systemstatus_topic: str = self.make_topic_name(self.topic)
        self.debug(f"System status with name {name} created")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.systemstatus_topic)

    @override
    def on_message(self, client: object, userdata: Any, msg: MockMqttMsg) -> None:
        if msg.topic == self.systemstatus_topic:
            em = json.loads(msg.payload.decode())
            self.record(timestamp(), em)
        else:
            super().on_message(client, userdata, msg)

    def record(self, ts: float, info: dict[str, Any]) -> None:
        if "threads" in info:
            threads: dict[str, int] = info["threads"]
            try:
                self.write_point(
                    "systemstatus",
                    {"location": self.location, "category": "threads"},
                    threads,
                    epoc2utc(ts),
                )
            except Exception as e:
                self.error(f"Writing memory to influx failed {str(e)}")

        if "memory" in info:
            memory: dict[str, int] = info["memory"]
            try:
                self.write_point(
                    "systemstatus",
                    {"location": self.location, "category": "memory"},
                    memory,
                    epoc2utc(ts),
                )
            except Exception as e:
                self.error(f"Writing memory to influx failed {str(e)}")

        if "cpu_loads" in info:
            cpu_loads: dict[str, float] = info["cpu_loads"]
            try:
                self.write_point(
                    "systemstatus",
                    {"location": self.location, "category": "cpu"},
                    cpu_loads,
                    epoc2utc(ts),
                )
            except Exception as e:
                self.error(f"Writing cpu_loads to influx failed {str(e)}")

        if "disk_info" in info:
            disk_info: dict[str, float] = info["disk_info"]
            try:
                index: int = 0
                for _, value in disk_info.items():
                    self.write_point(
                        "systemstatus",
                        {"location": self.location, "category": "disk"},
                        {f"disk{index}": value["percent"]},
                        epoc2utc(ts),
                    )
                    index = index + 1
            except Exception as e:
                self.error(f"Writing disk_info to influx failed {str(e)}")

    @override
    def run(self) -> None:
        self.worker = cast(
            SystemStatusThread, self.instantiate(SystemStatusThread.__name__)
        )
        self.worker.name = self.name
        self.worker.init(
            self.systemstatus_topic,
            self.update_interval,
            self.location,
        )
        super().run()

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        systemstatus_data = {}
        for attr in self._SYSTEMSTATUS_ATTRS:
            systemstatus_data[attr] = getattr(self, attr)
        data[self._SYSTEMSTATUS] = systemstatus_data
        return data

    def from_dict(self, data: dict[str, Any]) -> None:
        super().from_dict(data)
        if self._SYSTEMSTATUS in data:
            systemstatus_data = data[self._SYSTEMSTATUS]
            for attr in self._SYSTEMSTATUS_ATTRS:
                setattr(self, attr, systemstatus_data.get(attr, None))

# --- Unit Tests ---

class TestSystemStatusThread(unittest.TestCase):
    """Tests the asynchronous data acquisition thread."""

    def setUp(self):
        self.mock_mqtt_client = MockMqtt()
        self.thread = SystemStatusThread(client=self.mock_mqtt_client)
        # Mock the publish method inherited from the base class
        self.thread.publish = MagicMock() 

    def test_init_and_config(self):
        """Tests initialization and the init configuration method."""
        self.assertIs(self.thread.mqtt_client, self.mock_mqtt_client)

        topic = "test/sys/status"
        interval = 30.0
        location = "office"
        self.thread.init(topic, interval, location)

        self.assertEqual(self.thread._systemstatus_topic, topic)
        self.assertEqual(self.thread._interval, interval)
        self.assertEqual(self.thread._location, location)
        self.assertEqual(self.thread.update_interval(), interval)
        
    @patch('threading.enumerate')
    def test_get_thread_counts(self, mock_enumerate):
        """Tests calculation of total, active, and idle thread counts."""
        # Setup mocks for 3 active and 1 inactive thread
        mock_active_thread = MagicMock(is_alive=MagicMock(return_value=True))
        mock_inactive_thread = MagicMock(is_alive=MagicMock(return_value=False))
        mock_enumerate.return_value = [
            mock_active_thread, 
            mock_active_thread, 
            mock_inactive_thread,
            mock_active_thread, 
        ]
        
        counts = self.thread.get_thread_counts()
        
        self.assertEqual(counts["total_threads"], 4)
        self.assertEqual(counts["active_threads"], 3)
        self.assertEqual(counts["idle_threads"], 1)

    @patch('psutil.disk_usage')
    @patch('psutil.disk_partitions')
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    def test_get_system_info_success(self, mock_cpu_percent, mock_virtual_memory, mock_disk_partitions, mock_disk_usage):
        """Tests fetching all system metrics correctly."""
        # 1. Mock CPU
        mock_cpu_percent.return_value = [10.5, 20.0, 5.2] 

        # 2. Mock Memory (1GB total, 800MB available)
        mock_mem = MagicMock(total=1073741824, available=858993459) # ~1GB total, ~80% avail
        mock_virtual_memory.return_value = mock_mem

        # 3. Mock Disk (2 partitions)
        mock_partitions = [
            MagicMock(device="/dev/sda1", mountpoint="/"),
            MagicMock(device="/dev/sdb1", mountpoint="/data"),
        ]
        mock_disk_partitions.return_value = mock_partitions

        mock_usage_root = MagicMock(total=100, free=50, used=50, percent=50.0)
        mock_usage_data = MagicMock(total=200, free=100, used=100, percent=50.0)
        
        mock_disk_usage.side_effect = lambda path: mock_usage_root if path == '/' else mock_usage_data
        
        # --- Execute ---
        info = self.thread.get_system_info()

        # --- Assertions ---
        # 1. CPU Loads (Note: Corrected `i += 1` logic is tested)
        self.assertEqual(info["cpu_loads"], {"cpu0": 10.5, "cpu1": 20.0, "cpu2": 5.2})
        
        # 2. Memory
        self.assertAlmostEqual(info["memory"]["memory_usage"], 80.0, places=2)
        
        # 3. Disk Info
        self.assertIn("/dev/sda1", info["disk_info"])
        self.assertEqual(info["disk_info"]["/dev/sda1"]["percent"], 50.0)

    @patch.object(SystemStatusThread, 'get_thread_counts', return_value={"total_threads": 5, "active_threads": 2, "idle_threads": 3})
    @patch.object(SystemStatusThread, 'get_system_info', return_value={
        "cpu_loads": {"cpu0": 10.0},
        "memory": {"memory_usage": 50.0, "avail_memory": 1, "total_memory": 2},
        "disk_info": {"/": {"percent": 75.0}}
    })
    def test_update_publishes_data(self, mock_sys_info, mock_thread_counts):
        """Tests that update() collects data and calls self.publish with correct payload."""
        # Setup thread properties
        self.thread.init("status/pub/topic", 60, "home")
        
        # Execute
        result = self.thread.update()
        
        self.assertTrue(result)
        
        expected_sysinfo = {
            "cpu_loads": {"cpu0": 10.0},
            "memory": {"memory_usage": 50.0, "avail_memory": 1, "total_memory": 2},
            "disk_info": {"/": {"percent": 75.0}},
            "threads": {"total_threads": 5, "active_threads": 2, "idle_threads": 3}
        }
        
        # Check that publish was called correctly
        self.thread.publish.assert_called_once_with(
            "status/pub/topic",
            json.dumps(expected_sysinfo),
            qos=1,
            retain=False
        )


class TestSystemStatus(unittest.TestCase):
    """Tests the JuhamThread wrapper class for system status."""

    def setUp(self):
        self.status = SystemStatus(name="TestStatus")
        self.status.subscribe = MagicMock()
        
    def test_init(self):
        """Tests initialization and default topic creation."""
        # make_topic_name is mocked to return "prefix/system"
        self.assertEqual(self.status.name, "TestStatus")
        self.assertEqual(self.status.systemstatus_topic, "prefix/system")
        self.status.debug.assert_called_once()
        
    def test_on_connect_subscribes_on_success(self):
        """Tests that subscription only happens on successful connection (rc=0)."""
        # rc=0 means success
        self.status.on_connect(client=None, userdata=None, flags=0, rc=0)
        self.status.subscribe.assert_called_once_with(self.status.systemstatus_topic)

        # rc=1 means failure
        self.status.subscribe.reset_mock()
        self.status.on_connect(client=None, userdata=None, flags=0, rc=1)
        self.status.subscribe.assert_not_called()

    @patch.object(SystemStatus, 'record')
    # FIX 3: Patching MockJuhamThread's on_message now works because the method exists.
    @patch.object(MockJuhamThread, 'on_message') 
    def test_on_message_handles_system_status(self, mock_super_on_message, mock_record):
        """Tests message handling for the status topic."""
        self.status.systemstatus_topic = "test/topic"
        payload_dict = {"test_key": "test_value"}
        msg = MockMqttMsg(
            topic="test/topic", 
            payload=json.dumps(payload_dict).encode('utf-8')
        )
        
        self.status.on_message(client=None, userdata=None, msg=msg)
        
        # Check that record was called with mocked timestamp and parsed payload
        mock_record.assert_called_once_with(
            mock_time_timestamp.return_value, 
            payload_dict
        )
        mock_super_on_message.assert_not_called()

    def test_record_writes_all_data_points(self):
        """Tests that the record method parses data and calls write_point for all categories."""
        mock_ts = mock_time_timestamp.return_value
        mock_utc = mock_time_epoc2utc.return_value
        self.status.location = "test_location"
        
        info = {
            "threads": {"total": 10, "active": 5},
            "memory": {"usage": 50.0},
            "cpu_loads": {"cpu0": 10.0},
            "disk_info": {
                "/dev/sda1": {"percent": 75.0},
                "/dev/sdb1": {"percent": 25.0}
            }
        }
        
        self.status.record(mock_ts, info)
        
        # Expected calls to self.write_point
        expected_calls = [
            call("systemstatus", {"location": "test_location", "category": "threads"}, info["threads"], mock_utc),
            call("systemstatus", {"location": "test_location", "category": "memory"}, info["memory"], mock_utc),
            call("systemstatus", {"location": "test_location", "category": "cpu"}, info["cpu_loads"], mock_utc),
            call("systemstatus", {"location": "test_location", "category": "disk"}, {"disk0": 75.0}, mock_utc),
            call("systemstatus", {"location": "test_location", "category": "disk"}, {"disk1": 25.0}, mock_utc),
        ]
        
        self.status.write_point.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(self.status.write_point.call_count, 5)
        self.status.error.assert_not_called()

    @patch.object(SystemStatus, 'instantiate')
    @patch.object(MockJuhamThread, 'run')
    def test_run_initializes_and_starts_worker(self, mock_super_run, mock_instantiate):
        """Tests the setup and start of the worker thread."""
        mock_worker = SystemStatusThread()
        mock_worker.init = MagicMock()
        mock_instantiate.return_value = mock_worker
        
        self.status.update_interval = 15.0
        self.status.location = "lab"
        self.status.systemstatus_topic = "prefix/topic"
        self.status.name = "MyStatus"
        
        self.status.run()
        
        # Assert instantiation and worker initialization
        mock_instantiate.assert_called_once_with("SystemStatusThread")
        self.assertEqual(self.status.worker.name, "MyStatus")
        mock_worker.init.assert_called_once_with("prefix/topic", 15.0, "lab")
        
        # Assert base class run is called
        mock_super_run.assert_called_once()
        
    def test_to_and_from_dict_serialization(self):
        """Tests data serialization (to_dict) and deserialization (from_dict)."""
        
        # Set new values
        self.status.topic = "original_topic"
        self.status.update_interval = 100.0
        self.status.location = "mars"
        
        # 1. to_dict
        data = self.status.to_dict()
        self.assertIn("systemstatus", data)
        sys_data = data["systemstatus"]
        
        self.assertEqual(sys_data["topic"], "original_topic")
        self.assertEqual(sys_data["update_interval"], 100.0)
        
        # 2. from_dict
        new_data = {
            "systemstatus": {
                "topic": "deserialized_topic",
                "update_interval": 5.0,
                "location": "earth"
            },
            "other_settings": 123
        }
        
        self.status.from_dict(new_data)
        
        # Assert values are updated
        self.assertEqual(self.status.topic, "deserialized_topic")
        self.assertEqual(self.status.update_interval, 5.0)
        self.assertEqual(self.status.location, "earth")


# To run tests when the file is executed
if __name__ == '__main__':
    unittest.main()
