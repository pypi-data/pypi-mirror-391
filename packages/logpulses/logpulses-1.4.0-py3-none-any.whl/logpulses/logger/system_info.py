import psutil
import platform
import uuid
import tracemalloc
from datetime import datetime


def get_device_id():
    try:
        return str(uuid.UUID(int=uuid.getnode()))
    except:
        return platform.node()


def get_system_metrics():
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()

        return {
            "cpuUsage": f"{cpu_percent:.1f}%",
            "memoryUsage": {
                "total": f"{mem.total / (1024**3):.2f} GB",
                "used": f"{mem.used / (1024**3):.2f} GB",
                "available": f"{mem.available / (1024**3):.2f} GB",
                "percent": f"{mem.percent:.1f}%",
            },
        }

    except Exception as e:
        return {"error": str(e)}


def get_active_network_info():
    try:
        net_io = psutil.net_io_counters(pernic=True)
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        wireless_keywords = ["wifi", "wlan", "wireless", "802.11"]

        best = None
        best_score = -1

        for iface, entries in addrs.items():
            if iface.lower() == "lo" or iface.startswith("Loopback"):
                continue
            if iface in stats and not stats[iface].isup:
                continue

            for addr in entries:
                if addr.family.name != "AF_INET":
                    continue
                if addr.address == "127.0.0.1":
                    continue

                score = 0

                if any(w in iface.lower() for w in wireless_keywords):
                    score += 100
                    net_type = "WiFi"
                elif "eth" in iface.lower():
                    score += 50
                    net_type = "Ethernet"
                else:
                    net_type = "Other"

                if iface in net_io:
                    io = net_io[iface]
                    if io.bytes_sent or io.bytes_recv:
                        score += 10

                if addr.address.startswith(("10.", "192.168.", "172.")):
                    score += 5

                if score > best_score:
                    best_score = score
                    best = {
                        "interface": iface,
                        "type": net_type,
                        "ip": addr.address,
                        "netmask": addr.netmask,
                        "isActive": True,
                    }
                    if iface in net_io:
                        io = net_io[iface]
                        best.update(
                            {
                                "bytesSent": f"{io.bytes_sent / (1024**2):.2f} MB",
                                "bytesRecv": f"{io.bytes_recv / (1024**2):.2f} MB",
                            }
                        )

        return best or {"error": "No active network interface"}

    except Exception as e:
        return {"error": str(e)}
