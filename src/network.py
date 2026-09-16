import socket
import psutil


def get_hostname():
    return socket.gethostname()


def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "Unknown"


def get_network_interfaces():
    interfaces = []

    for name, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            if address.family == socket.AF_INET:
                interfaces.append({
                    "interface": name,
                    "ip": address.address
                })

    return interfaces


def get_connections():
    connections = []

    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr:
                local = f"{conn.laddr.ip}:{conn.laddr.port}"

                remote = "None"
                if conn.raddr:
                    remote = f"{conn.raddr.ip}:{conn.raddr.port}"

                connections.append({
                    "local": local,
                    "remote": remote,
                    "status": conn.status
                })

    except Exception as e:
        connections.append({
            "local": "Error",
            "remote": str(e),
            "status": "ERROR"
        })

    return connections