from flask import Flask, render_template_string, request, jsonify
import psutil
import platform
import socket
import hashlib
from datetime import datetime

app = Flask(__name__)

security_logs = []


# =========================================================
# SECURITY LOG
# =========================================================

def add_log(level, message):
    security_logs.insert(0, {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "message": message
    })

    if len(security_logs) > 50:
        security_logs.pop()


# =========================================================
# SYSTEM MONITOR
# =========================================================

def get_system_data():

    cpu = psutil.cpu_percent(interval=None)

    memory = psutil.virtual_memory()

    disk = psutil.disk_usage("C:\\")

    hostname = socket.gethostname()

    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "Unknown"

    return {
        "cpu": round(cpu, 1),

        "memory_percent": round(memory.percent, 1),

        "memory_used_gb": round(
            memory.used / (1024 ** 3),
            2
        ),

        "memory_total_gb": round(
            memory.total / (1024 ** 3),
            2
        ),

        "disk_percent": round(disk.percent, 1),

        "disk_used_gb": round(
            disk.used / (1024 ** 3),
            2
        ),

        "disk_total_gb": round(
            disk.total / (1024 ** 3),
            2
        ),

        "hostname": hostname,

        "ip": ip,

        "os": platform.system(),

        "platform": platform.platform(),

        "cores": psutil.cpu_count(
            logical=True
        )
    }


def check_alerts(data):

    alerts = []

    if data["cpu"] >= 85:
        alerts.append(
            f"CPU usage is high: {data['cpu']}%"
        )

    if data["memory_percent"] >= 85:
        alerts.append(
            f"Memory usage is high: "
            f"{data['memory_percent']}%"
        )

    if data["disk_percent"] >= 90:
        alerts.append(
            f"Disk usage is high: "
            f"{data['disk_percent']}%"
        )

    return alerts


# =========================================================
# NETWORK
# =========================================================

def get_interfaces():

    result = []

    try:

        interfaces = psutil.net_if_addrs()

        for name, addresses in interfaces.items():

            for address in addresses:

                if address.family == socket.AF_INET:

                    result.append({
                        "name": name,
                        "ip": address.address
                    })

    except Exception:
        pass

    return result


# =========================================================
# HTML
# =========================================================

HTML = """
<!DOCTYPE html>

<html lang="vi">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>AEGIS SECURITY</title>


<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}


body {

    background: #080b10;

    color: #e8edf5;

    font-family: Arial, sans-serif;

}


.layout {

    display: flex;

    min-height: 100vh;

}


.sidebar {

    width: 235px;

    background: #0d1117;

    border-right: 1px solid #202630;

    padding: 30px 18px;

}


.logo {

    font-size: 25px;

    font-weight: bold;

    letter-spacing: 1px;

}


.version {

    color: #7f8a99;

    font-size: 12px;

    margin-top: 6px;

    margin-bottom: 35px;

}


.menu {

    display: block;

    width: 100%;

    padding: 13px 15px;

    margin-bottom: 8px;

    color: #b9c2cf;

    text-decoration: none;

    border-radius: 8px;

    transition: 0.2s;

}


.menu:hover {

    background: #171d26;

    color: white;

}


.main {

    flex: 1;

    padding: 35px;

    overflow-x: auto;

}


.topbar {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 20px;

    margin-bottom: 30px;

}


h1 {

    font-size: 30px;

    margin-bottom: 7px;

}


.subtitle {

    color: #7f8a99;

    font-size: 14px;

}


.refresh {

    display: inline-block;

    background: #1f6feb;

    color: white;

    padding: 11px 18px;

    border-radius: 8px;

    text-decoration: none;

    font-weight: bold;

    border: none;

    cursor: pointer;

}


.refresh:hover {

    background: #388bfd;

}


.cards {

    display: grid;

    grid-template-columns:
        repeat(4, minmax(150px, 1fr));

    gap: 15px;

}


.card {

    background: #10151d;

    border: 1px solid #202630;

    border-radius: 12px;

    padding: 22px;

}


.card-title {

    color: #8d98a8;

    font-size: 13px;

    margin-bottom: 12px;

}


.value {

    font-size: 28px;

    font-weight: bold;

}


.small-value {

    color: #8994a4;

    font-size: 13px;

    margin-top: 7px;

}


.bar {

    width: 100%;

    height: 8px;

    background: #202630;

    border-radius: 10px;

    margin-top: 12px;

    overflow: hidden;

}


.bar-fill {

    height: 100%;

    background: #1f6feb;

    border-radius: 10px;

    transition: width 0.5s ease;

}


.section {

    margin-top: 25px;

    background: #10151d;

    border: 1px solid #202630;

    border-radius: 12px;

    padding: 25px;

}


.section h2 {

    margin-bottom: 20px;

    font-size: 19px;

}


.row {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 20px;

    padding: 13px 0;

    border-bottom: 1px solid #202630;

}


.row:last-child {

    border-bottom: none;

}


.label {

    color: #8994a4;

}


.status {

    color: #3fb950;

    font-weight: bold;

}


.warning {

    color: #d29922;

    font-weight: bold;

}


.info {

    color: #58a6ff;

    font-weight: bold;

}


.connection {

    padding: 14px;

    margin-bottom: 9px;

    background: #0d1117;

    border-radius: 8px;

    border: 1px solid #202630;

}


.log {

    padding: 15px;

    margin-bottom: 10px;

    background: #0d1117;

    border: 1px solid #202630;

    border-radius: 8px;

}


.log-time {

    color: #6e7781;

    font-family: monospace;

    font-size: 12px;

    margin-bottom: 6px;

}


.log-message {

    margin-top: 5px;

}


.upload-box {

    border: 1px dashed #394352;

    border-radius: 10px;

    padding: 25px;

    margin-top: 20px;

}


.file-input {

    width: 100%;

    margin-bottom: 20px;

    color: #c9d1d9;

}


.hash-value {

    word-break: break-all;

    max-width: 70%;

    text-align: right;

    font-family: monospace;

    font-size: 13px;

    color: #c9d1d9;

}


.live {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    color: #3fb950;

    font-size: 12px;

    font-weight: bold;

}


.live-dot {

    width: 8px;

    height: 8px;

    border-radius: 50%;

    background: #3fb950;

}


.footer {

    margin-top: 30px;

    color: #596575;

    font-size: 12px;

}


@media (max-width: 900px) {

    .cards {

        grid-template-columns:
            repeat(2, 1fr);

    }

}


@media (max-width: 650px) {

    .sidebar {

        display: none;

    }

    .main {

        padding: 20px;

    }

    .cards {

        grid-template-columns: 1fr;

    }

    .topbar {

        align-items: flex-start;

        flex-direction: column;

    }

    .row {

        flex-direction: column;

        align-items: flex-start;

    }

    .hash-value {

        max-width: 100%;

        text-align: left;

    }

}

</style>

</head>


<body>


<div class="layout">


<!-- SIDEBAR -->

<aside class="sidebar">

<div class="logo">
◈ AEGIS
</div>

<div class="version">
SECURITY TOOLKIT V3.0
</div>


<a class="menu" href="/">
🛡️ Dashboard
</a>


<a class="menu" href="/network">
🌐 Network
</a>


<a class="menu" href="/hash">
🔐 Hash Scanner
</a>


<a class="menu" href="/system">
💻 System
</a>


<a class="menu" href="/logs">
📋 Security Logs
</a>


<a class="menu" href="/about">
ℹ️ About
</a>


</aside>


<!-- MAIN -->

<main class="main">


<div class="topbar">

<div>

<h1>
{{ title }}
</h1>

<p class="subtitle">
Python Cybersecurity Toolkit
</p>

</div>


{% if page == "dashboard" %}

<div class="live">

<span class="live-dot"></span>

LIVE MONITORING

</div>

{% endif %}

</div>


<!-- ================================================= -->
<!-- DASHBOARD -->
<!-- ================================================= -->

{% if page == "dashboard" %}


<div class="cards">


<!-- CPU -->

<div class="card">

<div class="card-title">
CPU
</div>

<div
id="cpu-value"
class="value"
>
{{ cpu }}%
</div>

<div class="bar">

<div
id="cpu-bar"
class="bar-fill"
style="width: {{ cpu }}%"
>
</div>

</div>

</div>


<!-- RAM -->

<div class="card">

<div class="card-title">
MEMORY
</div>

<div
id="memory-value"
class="value"
>
{{ memory }}%
</div>

<div
id="memory-detail"
class="small-value"
>
{{ memory_used }} GB /
{{ memory_total }} GB
</div>

<div class="bar">

<div
id="memory-bar"
class="bar-fill"
style="width: {{ memory }}%"
>
</div>

</div>

</div>


<!-- DISK -->

<div class="card">

<div class="card-title">
DISK C:
</div>

<div
id="disk-value"
class="value"
>
{{ disk }}%
</div>

<div
id="disk-detail"
class="small-value"
>
{{ disk_used }} GB /
{{ disk_total }} GB
</div>

<div class="bar">

<div
id="disk-bar"
class="bar-fill"
style="width: {{ disk }}%"
>
</div>

</div>

</div>


<!-- ALERTS -->

<div class="card">

<div class="card-title">
ALERTS
</div>

<div
id="alerts-value"
class="value"
>
{{ alerts }}
</div>

<div
id="alerts-status"
class="{% if alerts > 0 %}warning{% else %}status{% endif %}"
>

{% if alerts > 0 %}
RESOURCE WARNING
{% else %}
SYSTEM NORMAL
{% endif %}

</div>

</div>


</div>


<!-- SYSTEM INFO -->

<div class="section">

<h2>
System Information
</h2>


<div class="row">

<span class="label">
Operating System
</span>

<span id="os">
{{ os }}
</span>

</div>


<div class="row">

<span class="label">
Hostname
</span>

<span id="hostname">
{{ hostname }}
</span>

</div>


<div class="row">

<span class="label">
Local IP
</span>

<span id="ip">
{{ ip }}
</span>

</div>


<div class="row">

<span class="label">
Last Update
</span>

<span id="update-time">
{{ time }}
</span>

</div>


</div>


<!-- SECURITY STATUS -->

<div class="section">

<h2>
Security Status
</h2>


<div class="row">

<span>
System Monitoring
</span>

<span class="status">
ACTIVE
</span>

</div>


<div class="row">

<span>
Network Monitor
</span>

<span class="status">
ACTIVE
</span>

</div>


<div class="row">

<span>
File Hash Scanner
</span>

<span class="status">
ACTIVE
</span>

</div>


<div class="row">

<span>
Resource Alerts
</span>

<span class="status">
ACTIVE
</span>

</div>


</div>


<!-- ================================================= -->
<!-- NETWORK -->
<!-- ================================================= -->

{% elif page == "network" %}


<div class="section">

<h2>
Network Information
</h2>


<div class="row">

<span class="label">
Hostname
</span>

<span>
{{ hostname }}
</span>

</div>


<div class="row">

<span class="label">
Local IP
</span>

<span>
{{ ip }}
</span>

</div>


<div class="row">

<span class="label">
Active Connections
</span>

<span>
{{ connections }}
</span>

</div>


</div>


<div class="section">

<h2>
Network Interfaces
</h2>


{% if interfaces %}

{% for interface in interfaces %}

<div class="connection">

<strong>
{{ interface.name }}
</strong>

<br>

<span class="label">
IPv4: {{ interface.ip }}
</span>

</div>

{% endfor %}

{% else %}

<p class="warning">
No IPv4 interfaces found.
</p>

{% endif %}


</div>


<!-- ================================================= -->
<!-- HASH -->
<!-- ================================================= -->

{% elif page == "hash" %}


<div class="section">

<h2>
🔐 File Hash Scanner
</h2>

<p class="subtitle">
Calculate SHA-256 and MD5 for file integrity checking.
</p>


<div class="upload-box">


<form
method="POST"
action="/hash"
enctype="multipart/form-data"
>


<input
class="file-input"
type="file"
name="file"
required
>


<button
class="refresh"
type="submit"
>
Calculate Hash
</button>


</form>


</div>

</div>


{% if error %}

<div class="section">

<h2>
Error
</h2>

<span class="warning">
{{ error }}
</span>

</div>

{% endif %}


{% if filename %}

<div class="section">

<h2>
Scan Result
</h2>


<div class="row">

<span class="label">
File
</span>

<span>
{{ filename }}
</span>

</div>


<div class="row">

<span class="label">
SHA-256
</span>

<span class="hash-value">
{{ sha256 }}
</span>

</div>


<div class="row">

<span class="label">
MD5
</span>

<span class="hash-value">
{{ md5 }}
</span>

</div>


</div>

{% endif %}


<!-- ================================================= -->
<!-- SYSTEM -->
<!-- ================================================= -->

{% elif page == "system" %}


<div class="cards">


<div class="card">

<div class="card-title">
CPU USAGE
</div>

<div
id="system-cpu"
class="value"
>
{{ cpu }}%
</div>

<div class="bar">

<div
id="system-cpu-bar"
class="bar-fill"
style="width: {{ cpu }}%"
>
</div>

</div>

</div>


<div class="card">

<div class="card-title">
MEMORY USAGE
</div>

<div
id="system-memory"
class="value"
>
{{ memory }}%
</div>

<div class="small-value">
{{ memory_used }} GB /
{{ memory_total }} GB
</div>

<div class="bar">

<div
id="system-memory-bar"
class="bar-fill"
style="width: {{ memory }}%"
>
</div>

</div>

</div>


<div class="card">

<div class="card-title">
DISK C: USAGE
</div>

<div
id="system-disk"
class="value"
>
{{ disk }}%
</div>

<div class="small-value">
{{ disk_used }} GB /
{{ disk_total }} GB
</div>

<div class="bar">

<div
id="system-disk-bar"
class="bar-fill"
style="width: {{ disk }}%"
>
</div>

</div>

</div>


</div>


<div class="section">

<h2>
System Details
</h2>


<div class="row">

<span class="label">
Operating System
</span>

<span>
{{ os }}
</span>

</div>


<div class="row">

<span class="label">
Platform
</span>

<span>
{{ platform }}
</span>

</div>


<div class="row">

<span class="label">
CPU Cores
</span>

<span>
{{ cores }}
</span>

</div>


<div class="row">

<span class="label">
Total RAM
</span>

<span>
{{ memory_total }} GB
</span>

</div>


</div>


<!-- ================================================= -->
<!-- LOGS -->
<!-- ================================================= -->

{% elif page == "logs" %}


<div class="section">

<h2>
📋 Security Logs
</h2>

<p class="subtitle">
Monitoring events generated by Aegis Security.
</p>

<br>


{% if logs %}


{% for log in logs %}

<div class="log">

<div class="log-time">
{{ log.time }}
</div>


{% if log.level == "WARNING" %}

<span class="warning">
⚠ WARNING
</span>

{% else %}

<span class="info">
● INFO
</span>

{% endif %}


<div class="log-message">
{{ log.message }}
</div>

</div>

{% endfor %}


{% else %}

<p class="subtitle">
No security events recorded.
</p>

{% endif %}


</div>


<!-- ================================================= -->
<!-- ABOUT -->
<!-- ================================================= -->

{% elif page == "about" %}


<div class="section">

<h2>
◈ AEGIS SECURITY
</h2>

<p class="subtitle">
Python Cybersecurity Toolkit
</p>

<br>


<div class="row">

<span class="label">
Version
</span>

<span>
3.0
</span>

</div>


<div class="row">

<span class="label">
Language
</span>

<span>
Python
</span>

</div>


<div class="row">

<span class="label">
Framework
</span>

<span>
Flask
</span>

</div>


<br>


<p>
Aegis Security là project học tập
về giám sát hệ thống và kiểm tra
bảo mật cơ bản.
</p>

<br>


<p>
V3 bổ sung hệ thống giám sát
CPU, RAM và Disk realtime.
</p>

<br>


<p>
Chỉ sử dụng các chức năng network
trên hệ thống mà bạn sở hữu hoặc
được phép kiểm tra.
</p>


</div>


{% endif %}


<div class="footer">

AEGIS SECURITY V3.0
•
Educational Cybersecurity Project

</div>


</main>

</div>


<!-- ================================================= -->
<!-- REALTIME JAVASCRIPT -->
<!-- ================================================= -->

{% if page == "dashboard" or page == "system" %}

<script>

async function updateSystem() {

    try {

        const response =
            await fetch("/api/status");

        const data =
            await response.json();


        // CPU

        document.getElementById(
            "cpu-value"
        ).textContent =
            data.cpu + "%";


        document.getElementById(
            "cpu-bar"
        ).style.width =
            data.cpu + "%";


        // MEMORY

        document.getElementById(
            "memory-value"
        ).textContent =
            data.memory_percent + "%";


        document.getElementById(
            "memory-detail"
        ).textContent =
            data.memory_used_gb +
            " GB / " +
            data.memory_total_gb +
            " GB";


        document.getElementById(
            "memory-bar"
        ).style.width =
            data.memory_percent + "%";


        // DISK

        document.getElementById(
            "disk-value"
        ).textContent =
            data.disk_percent + "%";


        document.getElementById(
            "disk-detail"
        ).textContent =
            data.disk_used_gb +
            " GB / " +
            data.disk_total_gb +
            " GB";


        document.getElementById(
            "disk-bar"
        ).style.width =
            data.disk_percent + "%";


        // ALERTS

        document.getElementById(
            "alerts-value"
        ).textContent =
            data.alerts;


        const alertStatus =
            document.getElementById(
                "alerts-status"
            );


        if (data.alerts > 0) {

            alertStatus.textContent =
                "RESOURCE WARNING";

            alertStatus.className =
                "warning";

        } else {

            alertStatus.textContent =
                "SYSTEM NORMAL";

            alertStatus.className =
                "status";

        }


        // TIME

        document.getElementById(
            "update-time"
        ).textContent =
            data.time;


    } catch (error) {

        console.log(
            "Monitoring error:",
            error
        );

    }

}


setInterval(
    updateSystem,
    1000
);

</script>

{% endif %}


</body>

</html>
"""


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    data = get_system_data()

    alerts = check_alerts(data)

    if alerts:

        for alert in alerts:

            add_log(
                "WARNING",
                alert
            )

    else:

        add_log(
            "INFO",
            "System monitoring normal."
        )


    return render_template_string(

        HTML,

        title="Security Dashboard",

        page="dashboard",

        cpu=data["cpu"],

        memory=data["memory_percent"],

        memory_used=data["memory_used_gb"],

        memory_total=data["memory_total_gb"],

        disk=data["disk_percent"],

        disk_used=data["disk_used_gb"],

        disk_total=data["disk_total_gb"],

        alerts=len(alerts),

        hostname=data["hostname"],

        ip=data["ip"],

        os=data["os"],

        time=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    )


# =========================================================
# API STATUS
# =========================================================

@app.route("/api/status")
def api_status():

    data = get_system_data()

    alerts = check_alerts(data)


    return jsonify({

        "cpu": data["cpu"],

        "memory_percent":
            data["memory_percent"],

        "memory_used_gb":
            data["memory_used_gb"],

        "memory_total_gb":
            data["memory_total_gb"],

        "disk_percent":
            data["disk_percent"],

        "disk_used_gb":
            data["disk_used_gb"],

        "disk_total_gb":
            data["disk_total_gb"],

        "alerts": len(alerts),

        "hostname":
            data["hostname"],

        "ip":
            data["ip"],

        "time":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    })


# =========================================================
# NETWORK
# =========================================================

@app.route("/network")
def network():

    data = get_system_data()

    try:

        connections = len(
            psutil.net_connections(
                kind="inet"
            )
        )

    except Exception:

        connections = 0


    interfaces = get_interfaces()


    return render_template_string(

        HTML,

        title="Network Monitor",

        page="network",

        hostname=data["hostname"],

        ip=data["ip"],

        connections=connections,

        interfaces=interfaces

    )


# =========================================================
# HASH SCANNER
# =========================================================

@app.route(
    "/hash",
    methods=["GET", "POST"]
)

def hash_scanner():

    sha256 = None

    md5 = None

    filename = None

    error = None


    if request.method == "POST":

        file = request.files.get(
            "file"
        )


        if not file:

            error = "Please choose a file."


        elif file.filename == "":

            error = "Please choose a file."


        else:

            try:

                sha256_hash =
                    hashlib.sha256()

                md5_hash =
                    hashlib.md5()


                while True:

                    chunk =
                        file.stream.read(
                            8192
                        )

                    if not chunk:

                        break


                    sha256_hash.update(
                        chunk
                    )

                    md5_hash.update(
                        chunk
                    )


                sha256 =
                    sha256_hash.hexdigest()

                md5 =
                    md5_hash.hexdigest()

                filename =
                    file.filename


                add_log(
                    "INFO",
                    f"Hash calculated: {filename}"
                )


            except Exception as e:

                error = str(e)

                add_log(
                    "WARNING",
                    f"Hash scanner error: {error}"
                )


    return render_template_string(

        HTML,

        title="Hash Scanner",

        page="hash",

        sha256=sha256,

        md5=md5,

        filename=filename,

        error=error

    )


# =========================================================
# SYSTEM
# =========================================================

@app.route("/system")
def system():

    data = get_system_data()


    return render_template_string(

        HTML,

        title="System Monitor",

        page="system",

        cpu=data["cpu"],

        memory=data["memory_percent"],

        memory_used=data["memory_used_gb"],

        memory_total=data["memory_total_gb"],

        disk=data["disk_percent"],

        disk_used=data["disk_used_gb"],

        disk_total=data["disk_total_gb"],

        os=data["os"],

        platform=data["platform"],

        cores=data["cores"]

    )


# =========================================================
# LOGS
# =========================================================

@app.route("/logs")
def logs():

    return render_template_string(

        HTML,

        title="Security Logs",

        page="logs",

        logs=security_logs

    )


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    return render_template_string(

        HTML,

        title="About",

        page="about"

    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )