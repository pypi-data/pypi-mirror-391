from datetime import datetime, timedelta, timezone
import json
import time
import psutil
import threading
from typing import Any, Optional, Union, cast
from typing_extensions import override
from masterpiece.mqtt import MqttMsg, Mqtt
from masterpiece import MasterPieceThread
from juham_core import JuhamTs, JuhamThread
from juham_core.timeutils import timestamp, epoc2utc


class SystemStatusThread(MasterPieceThread):
    """Asynchronous thread for acquiring system info. Currently fetches
    memory usage, disk usage, for each partition and CPU utilization, all in percentages.
    """

    # class attributes
    _systemstatus_topic: str = ""
    _interval: float = 60  # seconds
    _location = "unknown"
    _max_uptime_before_reboot: float = 3600 * 48  # 48 hours

    def __init__(self, client: Optional[Mqtt] = None):
        """Construct with the given mqtt client. Acquires system metrics
        e.g. CPU load and space left on the device and publishes the data to
        systemstatus_topic.

        Args:
            client (object, optional): MQTT client. Defaults to None.
        """
        super().__init__(client)
        self.mqtt_client: Optional[Mqtt] = client
        self.startup_time: float = time.time()

    def reboot(self) -> None:
        """
        Reboot.
        Since the service runs as root, we use /sbin/reboot directly.
        """
        self.error("REBOOT: Rebooting system to recover")
                  
        # Simulated Reboot Command (for testing the logic)
        # subprocess.run(["echo", f"System reboot triggered by {self.name} due to crash detection."], check=True)
        # Actual Reboot Command (UNCOMMENT THIS LINE ONLY AFTER TESTING IS COMPLETE)
        subprocess.run(["/sbin/reboot"], check=True)


    def init(self, topic: str, interval: float, location: str, max_uptime : float) -> None:
        """Initialize the  data acquisition thread

        Args:
            topic (str): mqtt topic to publish the acquired system info
            interval (float): update interval in seconds
            location (str): geographic location
        """
        self._systemstatus_topic = topic
        self._interval = interval
        self._location = location
        self._max_uptime_before_reboot = max_uptime

    def get_thread_counts(self) -> dict[str, Union[int, float]]:
        """Fetch the number of total, active and idle threads in the current process.

        Returns:
            Thread info (dict[str, int])
        """
        all_threads = threading.enumerate()
        total_threads = len(all_threads)
        active_threads = sum(1 for thread in all_threads if thread.is_alive())

        return {
            "total_threads": total_threads,
            "active_threads": active_threads,
            "idle_threads": total_threads - active_threads,
        }

    def get_system_info(self) -> dict[str, dict[Any, Any]]:
        """Fetch system info e.g. CPU loads, thread count, disk and ram usage.

        Returns:
            Thread info (dict[str, dict])
        """
        cpus = psutil.cpu_percent(interval=1, percpu=True)  # List of CPU loads per core

        cpu_loads: dict[str, float] = {}
        i: int = 0
        for cpu in cpus:
            cpu_loads[f"cpu{i}"] = cpu
            i = i + i

        # Memory info
        memory = psutil.virtual_memory()  # Virtual memory details
        available_memory = memory.available  # Available memory in bytes
        total_memory = memory.total  # Total memory in bytes

        # Disk space info per partition
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
                # Skip partitions that we don't have permission to access
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


    def consider_reboot(self, current_time: float) -> None:
        """Consider rebooting the system if the uptime exceeds the maximum allowed uptime.

        Args:
            current_time (float): Current timestamp
        """
        elapsed : float = current_time - self.startup_time
        if elapsed > self._max_uptime_before_reboot:
            self.reboot()


    @override
    def update(self) -> bool:
        start_time: float = time.time()
        sysinfo: dict[str, dict] = self.get_system_info()
        sysinfo.update({"threads": self.get_thread_counts()})
        msg = json.dumps(sysinfo)
        stop_time: float = time.time()
        self.publish(self._systemstatus_topic, msg, qos=1, retain=False)
        # self.debug(f"System status  published to {self._systemstatus_topic}")

        self.consider_reboot(stop_time)
        return True


class SystemStatus(JuhamThread):
    """Constructs a data acquisition thread for reading system status
    info, e.g. available disk space and publishes the data to the systemstatus topic.

    """

    _SYSTEMSTATUS: str = "systemstatus"
    _SYSTEMSTATUS_ATTRS: list[str] = ["topic", "update_interval", "location"]

    _workerThreadId: str = SystemStatusThread.get_class_id()
    update_interval: float = 60
    topic = "system"
    location = "home"
    max_uptime_before_reboot: float = 3600 * 48  # 48 hours

    def __init__(self, name="systemstatus") -> None:
        """Constructs system status automation object for acquiring and publishing
        system info e.g. available memory and CPU loads.

        Args:
            name (str, optional): name of the object.
        """
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
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.systemstatus_topic:
            em = json.loads(msg.payload.decode())
            self.record(timestamp(), em)
        else:
            super().on_message(client, userdata, msg)

    def record(self, ts: float, info: dict[str, Any]) -> None:
        """Writes system info to the time series database

        Args:
            ts (float): utc time
            em (dict): energy meter message
        """

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
                value: Any
                index: int = 0
                for attr, value in disk_info.items():
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
        # create, initialize and start the asynchronous thread for acquiring forecast

        self.worker = cast(
            SystemStatusThread, self.instantiate(SystemStatus._workerThreadId)
        )
        self.worker.name = self.name
        self.worker.init(
            self.systemstatus_topic,
            self.update_interval,
            self.location,
            self.max_uptime_before_reboot
        )
        super().run()

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()  # Call parent class method
        systemstatus_data = {}
        for attr in self._SYSTEMSTATUS_ATTRS:
            systemstatus_data[attr] = getattr(self, attr)
        data[self._SYSTEMSTATUS] = systemstatus_data
        return data

    def from_dict(self, data: dict[str, Any]) -> None:
        super().from_dict(data)  # Call parent class method
        if self._SYSTEMSTATUS in data:
            systemstatus_data = data[self._SYSTEMSTATUS]
            for attr in self._SYSTEMSTATUS_ATTRS:
                setattr(self, attr, systemstatus_data.get(attr, None))
