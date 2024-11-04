from flask import Flask, jsonify
import psutil
import GPUtil
import platform
from datetime import datetime

app = Flask(__name__)

class ResourceGetter:
    @staticmethod
    def get_system_info():
        uname = platform.uname()
        return {
            "system": uname.system,
            "node_name": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor
        }

    @staticmethod
    def get_network_info():
        net_io = psutil.net_io_counters(pernic=True)
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        network_data = {"interfaces": {}}
        for interface, addrs in net_if_addrs.items():
            addresses = [{"family": str(addr.family), "address": addr.address, "netmask": addr.netmask, "broadcast": addr.broadcast} for addr in addrs]
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
                "bytes_recv": io_stats.bytes_recv if io_stats else None
            }
        return network_data

    @staticmethod
    def get_cpu_info():
        return {
            "cpu_count_physical": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_percent_per_core": [{f"core_{i}": cpu_percent} for i, cpu_percent in enumerate(psutil.cpu_percent(interval=1, percpu=True))],
            "cpu_freq": [{f"core_{i}":cpu_freq} for i, cpu_freq in enumerate(psutil.cpu_freq(percpu=True))],
            "cpu_times": [{f"core_{i}": cpu_times} for i, cpu_times in enumerate(psutil.cpu_times(percpu=True))],
            "cpu_stats": psutil.cpu_stats()._asdict()
        }

    @staticmethod
    def get_memory_info():
        memory_info = psutil.virtual_memory()
        return {
            'total': memory_info.total,
            'available': memory_info.available,
            'used': memory_info.used,
            'free': memory_info.free,
            'percent_used': memory_info.percent
        }

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
                    "total_space": usage.total,
                    "used_space": usage.used,
                    "free_space": usage.free,
                    "percent_usage": usage.percent
                })
            except PermissionError:
                continue
        return disk_info

    @staticmethod
    def get_gpu_info():
        gpus = GPUtil.getGPUs()
        return [{"id": gpu.id, "name": gpu.name, "load": gpu.load * 100, "memory_total": gpu.memoryTotal, "memory_used": gpu.memoryUsed, "temperature": gpu.temperature} for gpu in gpus]

    @staticmethod
    def get_server_uptime():
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        current_time = datetime.now()
        uptime_duration = current_time - boot_time
        return {
            "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime_days": uptime_duration.days,
            "uptime_hours": uptime_duration.seconds // 3600,
            "uptime_minutes": (uptime_duration.seconds // 60) % 60,
            "uptime_seconds": uptime_duration.seconds % 60
        }

resource_getter = ResourceGetter()

@app.route('/metrics/system', methods=['GET'])
def system_info():
    return jsonify(resource_getter.get_system_info())

@app.route('/metrics/cpu', methods=['GET'])
def cpu_info():
    return jsonify(resource_getter.get_cpu_info())

@app.route('/metrics/memory', methods=['GET'])
def memory_info():
    return jsonify(resource_getter.get_memory_info())

@app.route('/metrics/disk', methods=['GET'])
def disk_info():
    return jsonify(resource_getter.get_disk_info())

@app.route('/metrics/gpu', methods=['GET'])
def gpu_info():
    return jsonify(resource_getter.get_gpu_info())

@app.route('/metrics/uptime', methods=['GET'])
def uptime_info():
    return jsonify(resource_getter.get_server_uptime())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
