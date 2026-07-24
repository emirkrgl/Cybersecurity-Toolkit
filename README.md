<img width="988" height="262" alt="portScanner_demo" src="https://github.com/user-attachments/assets/efe5ab03-e360-4e87-97ba-18258ff23a71" />
<img width="722" height="221" alt="netdiscover_demo" src="https://github.com/user-attachments/assets/05c7cabe-a4ff-46fc-b547-0716ffea4952" />
<img width="531" height="483" alt="dir_bruteforce_demo" src="https://github.com/user-attachments/assets/069d8006-11fb-49bb-8f37-7c556c8e3e27" />
<img width="1106" height="901" alt="dir_bruteForce_demo(2)" src="https://github.com/user-attachments/assets/dda32c95-34ee-4042-8b7e-10d07d66d940" />
# Cybersecurity Toolkit

A small collection of Python security tools, built from scratch as a hands-on way to learn networking, concurrency, and web fundamentals — one project at a time, one bug at a time.

> These are **beginner-level implementations**, written intentionally simple so the core logic stays easy to read and reason about. Each tool works, but none of them are "finished" — see the [Roadmap](#-roadmap--planned-improvements) below for what's coming next.

---

## 🧰 Tools

| Tool | What it does |
|---|---|
| [`netdiscover.py`](#netdiscoverpy) | Discovers live hosts on a local network using ARP requests |
| [`portScanner.py`](#portscannerpy) | Multi-threaded TCP port scanner with basic banner grabbing |
| [`dir_bruteForce.py`](#dir_bruteforcepy) | Recursive directory & file brute-forcer with extension fuzzing |

---

## 📸 Screenshots



### netdiscover.py
![netdiscover demo](docs/netdiscover_demo.png)

### portScanner.py
![portScanner demo](docs/portScanner_demo.png)

### dir_bruteForce.py
![dir_bruteForce demo](docs/dir_bruteforce_demo.png)

### dir_bruteForce.py
![dir_bruteForce demo](docs/dir_bruteforce_demo(2).png)


---

## netdiscover.py

A simple network discovery tool. It sends ARP broadcast requests across a target IP range and lists every device that responds, along with its IP address, MAC address, and (when resolvable) hostname.

### How it works
Built on top of `scapy`, it crafts an Ethernet + ARP broadcast packet (`ff:ff:ff:ff:ff:ff`) and listens for replies — the same low-level technique tools like `arp-scan` and `netdiscover` (the actual CLI tool) use under the hood.

### Requirements
```bash
pip install scapy
```
⚠️ ARP scanning requires raw socket access — on Windows you'll need [Npcap](https://npcap.com/) installed, and on Linux you'll likely need to run with `sudo`.

### Usage
```bash
python netdiscover.py
```
You'll be prompted to enter the target IP range (e.g. `192.168.1.0/24`).

---

## portScanner.py

A multi-threaded TCP port scanner that checks a range of ports on a target host, and attempts basic banner grabbing to identify what's running behind an open port (HTTP server headers, MySQL handshake bytes, etc.).

### Features
- One thread per port scanned — fast for small-to-medium port ranges
- Sends protocol-aware probes depending on the port (HTTP `HEAD` request for 80/443/8080, a MySQL greeting probe for 3306, passive listening for FTP/SSH)
- Resolves domain names to IPs automatically

### Usage
```bash
python portScanner.py
```
You'll be prompted for:
- Target (IP or domain)
- Start port
- End port

---

## dir_bruteForce.py

A recursive directory and file brute-forcing tool, similar in spirit to `gobuster` or `dirsearch`, built to understand how these tools actually work under the hood rather than just using them as a black box.

### Features
- **Multi-threaded** scanning (`ThreadPoolExecutor`, configurable thread count)
- **Recursive scanning** — automatically dives into discovered directories, up to a configurable depth
- **Extension fuzzing** — tries common file extensions (`.php`, `.bak`, `.zip`, `.tar.gz`, `.env`, etc.) against every wordlist entry
- **Custom headers & cookies** — supports a realistic `User-Agent` and session cookies for authenticated scans
- **Optional rate limiting** — random delay between requests to avoid tripping WAFs
- **Colorized terminal output** — found (200), forbidden (403), and redirected (301/302) results are visually distinct
- **Fully CLI-driven** via `argparse`

### Requirements
```bash
pip install requests
```

### Usage
```bash
python dir_bruteForce.py -u http://target.com/ -w wordlist.txt
```

### Options

| Flag | Description | Default |
|---|---|---|
| `-u`, `--url` | Target URL (required) | — |
| `-w`, `--wordlist` | Path to wordlist file (required) | — |
| `-x`, `--extensions` | Comma-separated extensions to fuzz | `php,html,bak,zip,txt,tar.gz,sql,...` |
| `-t`, `--threads` | Number of concurrent threads | `10` |
| `-d`, `--depth` | Maximum recursion depth | `2` |
| `--timeout` | Request timeout (seconds) | `10` |
| `--min-delay` / `--max-delay` | Random delay range between requests (seconds) | `0` (disabled) |
| `--cookie` | Add a cookie (`name=value`), repeatable | — |

### Example
```bash
python dir_bruteForce.py -u http://127.0.0.1:8000/ -w wordlist.txt -t 20 -d 2 --cookie session=abc123
```

---

## ⚠️ Legal / Ethical Notice

These tools are intended **only** for systems you own or have **explicit written permission** to test — your own local network, a self-hosted lab server, or an authorized penetration test / CTF environment. Scanning networks or websites without authorization is illegal in most jurisdictions.

---

## 🗺️ Roadmap / Planned Improvements

**dir_bruteForce.py**
- [ ] Wildcard / soft-404 detection (avoid false positives on servers that return 200 for everything)
- [ ] Save results to file (`-o results.txt` or JSON export)
- [ ] Progress bar while scanning
- [ ] Skip extension fuzzing on deeper recursion levels (currently repeats on every level, which is slower than necessary)

**portScanner.py**
- [ ] Replace one-thread-per-port with a `ThreadPoolExecutor` to safely handle large port ranges
- [ ] Add CLI arguments (`argparse`) instead of interactive `input()` prompts
- [ ] Export scan results to file

**netdiscover.py**
- [ ] Add CLI arguments instead of interactive `input()` prompt
- [ ] Add vendor/manufacturer lookup from MAC address (OUI database)

**General**
- [ ] Combine shared logic (threading, output formatting) into a common module
- [ ] Add basic unit tests
- [ ] Add a subdomain enumeration tool

---

## 🧪 Testing

Tools have been tested locally against a self-hosted test server and a local network, using a controlled set of known files, directories, and hosts to verify detection accuracy before pointing them at anything else.

---

## 🙋 About this project

Built as part of a self-directed cybersecurity learning path, combining:
- Practical scripting (this repo)
- Web security labs (PortSwigger Web Security Academy)
- Linux/network fundamentals (OverTheWire)
- Algorithmic problem solving (LeetCode)

The goal isn't to replace tools like `gobuster`, `nmap`, or `arp-scan` — it's to understand how they work by rebuilding simplified versions from scratch, and to keep improving them incrementally as new concepts are learned.

## 📄 License

*(Add a license here, e.g. MIT, if you'd like others to freely use or modify this code.)*
