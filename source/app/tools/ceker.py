import psutil
import GPUtil
import platform
import argparse

from datetime import datetime

class ResourceGetter:
    def __init__(self):
        pass

    @staticmethod
    def get_system_info():
        uname = platform.uname()
        system_info = {
            "system": uname.system,
            "node_name": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor
        }
        return system_info

    @staticmethod
    def get_network_info():
        net_io = psutil.net_io_counters(pernic=True)
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        network_data = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "interfaces": {}
        }

        for interface, addrs in net_if_addrs.items():
            addresses = []
            for addr in addrs:
                addresses.append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })

            io_stats = net_io.get(interface, None)
            stats = net_if_stats.get(interface, None)

            network_data["interfaces"][interface] = {
                "addresses": addresses,
                "is_up": stats.isup if stats else None,
                "speed_mbps": stats.speed if stats else None,
                "mtu": stats.mtu if stats else None,
                "packets_sent": io_stats.packets_sent if io_stats else None,
                "packets_recv": io_stats.packets_recv if io_stats else None,
                "bytes_sent": io_stats.bytes_sent if io_stats else None,
                "bytes_recv": io_stats.bytes_recv if io_stats else None,
                "err_in": io_stats.errin if io_stats else None,
                "err_out": io_stats.errout if io_stats else None,
                "drop_in": io_stats.dropin if io_stats else None,
                "drop_out": io_stats.dropout if io_stats else None
            }
        return network_data

    @staticmethod
    def get_cpu_info():
        cpu_info = {
            "cpu_count_physical": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_freq": psutil.cpu_freq()._asdict(),
            "cpu_times": psutil.cpu_times()._asdict(),
            "cpu_stats": psutil.cpu_stats()._asdict()
        }
        return cpu_info

    @staticmethod
    def get_memory_info():
        memory_info = psutil.virtual_memory()
        swap_info = psutil.swap_memory()
        memory_info = {
            'physical_memory': {
                'total': memory_info.total,
                'available': memory_info.available,
                'used': memory_info.used,
                'free': memory_info.free,
                'percent_used': memory_info.percent
            },
            'swap_memory': {
                'total': swap_info.total,
                'used': swap_info.used,
                'free': swap_info.free,
                'percent_used': swap_info.percent
            }
        }
        return memory_info

    @staticmethod
    def get_disk_info():
        disk_info = []
        partitions = psutil.disk_partitions(all=False)
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "opts": partition.opts,
                    "total_space": usage.total,
                    "used_space": usage.used,
                    "free_space": usage.free,
                    "percent_usage": usage.percent
                })
            except PermissionError:
                continue

        return disk_info

    @staticmethod
    def get_disk_io_info():
        disk_io = psutil.disk_io_counters(perdisk=True)
        io_info = {}
        
        for disk, stats in disk_io.items():
            io_info[disk] = {
                "read_count": stats.read_count,
                "write_count": stats.write_count,
                "read_bytes": stats.read_bytes,
                "write_bytes": stats.write_bytes,
                "read_time": stats.read_time,
                "write_time": stats.write_time
            }

        return io_info
    
    @staticmethod
    def get_server_uptime():
        boot_time_timestamp = psutil.boot_time()
        boot_time = datetime.fromtimestamp(boot_time_timestamp)
        current_time = datetime.now()
        uptime_duration = current_time - boot_time
        uptime_info = {
            "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime": {
                "days": uptime_duration.days,
                "hours": uptime_duration.seconds // 3600,
                "minutes": (uptime_duration.seconds // 60) % 60,
                "seconds": uptime_duration.seconds % 60
            }
        }
        return uptime_info

    @staticmethod
    def get_gpu_info():
        gpus = GPUtil.getGPUs()
        gpu_info_list = []
        for gpu in gpus:
            gpu_info = {
                "id": gpu.id,
                "name": gpu.name,
                "driver_version": gpu.driver,
                "gpu_load_percent": gpu.load * 100,
                "memory_total": gpu.memoryTotal,
                "memory_used": gpu.memoryUsed,
                "memory_free": gpu.memoryFree,
                "temperature": gpu.temperature,
            }
            gpu_info_list.append(gpu_info)
        return gpu_info_list
    
    @staticmethod
    def get_sensor_info():
        temperatures = psutil.sensors_temperatures()
        fans = psutil.sensors_fans()
        battery = psutil.sensors_battery()

        sensor_info = {
            "temperatures": {},
            "fans": {},
            "battery": None
        }

        for name, entries in temperatures.items():
            sensor_info["temperatures"][name] = []
            for entry in entries:
                temp_info = {
                    "label": entry.label,
                    "current": entry.current,
                }
                if hasattr(entry, 'high'):
                    temp_info["high"] = entry.high
                if hasattr(entry, 'low'):
                    temp_info["low"] = entry.low
                sensor_info["temperatures"][name].append(temp_info)

        for name, entries in fans.items():
            sensor_info["fans"][name] = [entry for entry in entries]

        if battery is not None:
            sensor_info["battery"] = {
                "percent": battery.percent,
                "plugged": battery.power_plugged,
                "secsleft": battery.secsleft
            }

        return sensor_info

    @staticmethod
    def get_detailed_resource_usage(limit=5):
        process_info = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
            try:
                process_data = {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_mb': proc.info['memory_info'].rss / (1024 * 1024),  # Convert ke MB
                    'status': proc.info['status'],
                }
                process_info.append(process_data)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        process_info = sorted(process_info, key=lambda x: (-x['cpu_percent'], -x['memory_mb']))
        process_info = process_info[:limit]
        return process_info


    def resource_info(self):
        return {
            "system_info": self.get_system_info(),
            "cpu_info": self.get_cpu_info(),
            "gpu_info": self.get_gpu_info(),
            "memory_info": self.get_memory_info(),
            "disk_info": self.get_disk_info(),
            "disk_io_info": self.get_disk_io_info(),
            "network_info": self.get_network_info(),
            "sensor_info": self.get_sensor_info(),
            "resource_usage_info": self.get_detailed_resource_usage(),
            "server_uptime": self.get_server_uptime(),
        }

def main():
    resource_getter = ResourceGetter()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--action", choices=["detail", "simple"], default="detail", required=True
    )

    args = arg_parser.parse_args()
    if args.action == "detail":
        result = resource_getter.resource_info()
    elif args.action == "simple":
        result = resource_getter.simple_resource_info()
    print(result)


if __name__ == "__main__":
    main()
