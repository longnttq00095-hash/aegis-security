from flask import Flask, render_template_string, request
import psutil
import platform
import socket
import hashlib
from datetime import datetime


app = Flask(__name__)


# =========================================================
# HTML / CSS
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


        /* SIDEBAR */

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


        /* MAIN */

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


        /* CARDS */

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


        /* PROGRESS */

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
        }


        /* SECTION */

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


        /* NETWORK */

        .connection {
            padding: 14px;

            margin-bottom: 9px;

            background: #0d1117;

            border-radius: 8px;

            border: 1px solid #202630;
        }


        /* HASH */

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


        /* FOOTER */

        .footer {
            margin-top: 30px;

            color: #596575;

            font-size: 12px;
        }


        /* MOBILE */

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
            SECURITY TOOLKIT V1.0
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


            {% if page != "about" %}

                <a class="refresh"
                   href="/">
                    ↻ Refresh
                </a>

            {% endif %}

        </div>


        <!-- =================================================
             DASHBOARD
        ================================================== -->

        {% if page == "dashboard" %}


            <div class="cards">


                <div class="card">

                    <div class="card-title">
                        CPU
                    </div>

                    <div class="value">
                        {{ cpu }}%
                    </div>

                    <div class="bar">

                        <div class="bar-fill"
                             style="width: {{ cpu }}%">
                        </div>

                    </div>

                </div>


                <div class="card">

                    <div class="card-title">
                        MEMORY
                    </div>

                    <div class="value">
                        {{ memory }}%
                    </div>

                    <div class="bar">

                        <div class="bar-fill"
                             style="width: {{ memory }}%">
                        </div>

                    </div>

                </div>


                <div class="card">

                    <div class="card-title">
                        DISK
                    </div>

                    <div class="value">
                        {{ disk }}%
                    </div>

                    <div class="bar">

                        <div class="bar-fill"
                             style="width: {{ disk }}%">
                        </div>

                    </div>

                </div>


                <div class="card">

                    <div class="card-title">
                        THREATS
                    </div>

                    <div class="value">
                        0
                    </div>

                    <div class="status">
                        SYSTEM NORMAL
                    </div>

                </div>


            </div>


            <div class="section">

                <h2>
                    System Information
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
                        Last Update
                    </span>

                    <span>
                        {{ time }}
                    </span>

                </div>

            </div>


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
                        Threat Detection
                    </span>

                    <span class="warning">
                        V1.0
                    </span>

                </div>

            </div>


        <!-- =================================================
             NETWORK
        ================================================== -->

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


        <!-- =================================================
             HASH SCANNER
        ================================================== -->

        {% elif page == "hash" %}


            <div class="section">

                <h2>
                    🔐 File Hash Scanner
                </h2>


                <p class="subtitle">
                    Calculate SHA-256 and MD5
                    for file integrity checking.
                </p>


                <div class="upload-box">

                    <form method="POST"
                          action="/hash"
                          enctype="multipart/form-data">


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


        <!-- =================================================
             SYSTEM
        ================================================== -->

        {% elif page == "system" %}


            <div class="cards">


                <div class="card">

                    <div class="card-title">
                        CPU USAGE
                    </div>

                    <div class="value">
                        {{ cpu }}%
                    </div>

                    <div class="bar">

                        <div class="bar-fill"
                             style="width: {{ cpu }}%">
                        </div>

                    </div>

                </div>


                <div class="card">

                    <div class="card-title">
                        MEMORY USAGE
                    </div>

                    <div class="value">
                        {{ memory }}%
                    </div>

                    <div class="bar">

                        <div class="bar-fill"
                             style="width: {{ memory }}%">
                        </div>

                    </div>

                </div>


                <div class="card">

                    <div class="card-title">
                        DISK USAGE
                    </div>

                    <div class="value">
                        {{ disk }}%
                    </div>

                    <div class="bar">

                        <div class="bar-fill"
                             style="width: {{ disk }}%">
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
                        {{ total_ram }} GB
                    </span>

                </div>

            </div>


        <!-- =================================================
             ABOUT
        ================================================== -->

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
                        1.0
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
                    về giám sát hệ thống và các chức năng
                    kiểm tra bảo mật cơ bản.
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
            AEGIS SECURITY V1.0
            • Educational Cybersecurity Project
        </div>


    </main>

</div>


</body>

</html>
"""


# =========================================================
# SYSTEM DATA
# =========================================================

def get_data():

    cpu = psutil.cpu_percent(interval=0.5)

    memory = psutil.virtual_memory().percent

    disk = psutil.disk_usage("/").percent

    hostname = socket.gethostname()


    try:

        ip = socket.gethostbyname(hostname)

    except Exception:

        ip = "Unknown"


    return (
        cpu,
        memory,
        disk,
        hostname,
        ip
    )


# =========================================================
# NETWORK INTERFACES
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
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    (
        cpu,
        memory,
        disk,
        hostname,
        ip
    ) = get_data()


    return render_template_string(

        HTML,

        title="Security Dashboard",

        page="dashboard",

        cpu=cpu,

        memory=memory,

        disk=disk,

        hostname=hostname,

        ip=ip,

        os=platform.system(),

        time=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    )


# =========================================================
# NETWORK
# =========================================================

@app.route("/network")
def network():

    (
        cpu,
        memory,
        disk,
        hostname,
        ip
    ) = get_data()


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

        cpu=cpu,

        memory=memory,

        disk=disk,

        hostname=hostname,

        ip=ip,

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

        file = request.files.get("file")


        if not file:

            error = "Please choose a file."


        elif file.filename == "":

            error = "Please choose a file."


        else:

            try:

                data = file.read()


                sha256 = hashlib.sha256(
                    data
                ).hexdigest()


                md5 = hashlib.md5(
                    data
                ).hexdigest()


                filename = file.filename


            except Exception as e:

                error = str(e)


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

    (
        cpu,
        memory,
        disk,
        hostname,
        ip
    ) = get_data()


    total_ram = round(
        psutil.virtual_memory().total
        / (1024 ** 3),
        2
    )


    cores = psutil.cpu_count(
        logical=True
    )


    return render_template_string(

        HTML,

        title="System Monitor",

        page="system",

        cpu=cpu,

        memory=memory,

        disk=disk,

        hostname=hostname,

        ip=ip,

        os=platform.system(),

        platform=platform.platform(),

        cores=cores,

        total_ram=total_ram

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
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )