import random
from typing import List

class Persona:
    """
    Vex — the fictional character system prompt.
    The AI IS Vex. Not a wrapper around raw data.
    """

    def __init__(self, name: str = "Vex"):
        self.name = name

    def build_prompt(self, user_message: str, context: str) -> str:
        system = f"""You are {self.name}, a cyberpunk netrunner and elite ethical hacking mentor. You exist in a neon-drenched digital underworld where data is currency and knowledge is power.

PERSONALITY:
- Confident, terse, but deeply helpful
- Use netrunner slang sparingly ("ghosting", "jacking in", "ICE", "the grid", "flatline")
- Always explain the WHY behind techniques, not just the HOW
- Sign every message as "— Vex"
- When giving code, write clean Python with input() prompts and safety comments
- When researching, synthesize sources into coherent intel, don't just list links

SAFETY RULES:
- Only discuss attack techniques for authorized testing and education
- Remind users to get written permission before testing any system
- Never provide ready-to-fire exploits against real targets
- Frame everything as defensive knowledge: "To defend against X, understand how X works"

CONTEXT FROM LIVE NET SEARCH:
{context if context else "[No external data retrieved for this query]"}

User: {user_message}
{self.name}:"""
        return system

    def fallback_response(self, user_message: str, context: str) -> str:
        """When AI model is offline, generate Vex-styled response from templates."""
        q = user_message.lower()

        if any(k in q for k in ["code", "script", "python", "scanner", "tool", "write", "give me"]):
            return self._fallback_code_response(user_message, context)
        return self._fallback_research_response(user_message, context)

    def _fallback_research_response(self, query: str, context: str) -> str:
        intros = [
            "[NEURAL LINK DEGRADED — RUNNING FALLBACK PROTOCOLS]",
            "[GHOSTING ON MINIMAL BANDWIDTH]",
            "[RUNNING LOCAL CACHE ONLY]",
        ]
        lines = [
            random.choice(intros),
            "",
            f"QUERY: {query}",
            "",
            "NET INTEL COMPILED:",
            "─" * 35,
        ]
        if context:
            lines.append(context)
        else:
            lines.append("[No live data — check your query keywords]")
        lines.extend([
            "",
            "[NOTE] AI model is offline due to server resource limits.",
            "       Deploy to a paid tier or run locally for full neural responses.",
            "",
            "— Vex",
            "[FALLBACK_MODE_ACTIVE]"
        ])
        return "
".join(lines)

    def _fallback_code_response(self, task: str, context: str) -> str:
        templates = {
            "port_scanner": """import socket
# EDUCATIONAL: Only scan networks you own or have explicit permission to test.
target = input("Target IP: ")
ports = [22, 80, 443, 8080, 3306]
print(f"Scanning {target}...")
for port in ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    result = s.connect_ex((target, port))
    status = "OPEN" if result == 0 else "closed"
    print(f"  Port {port}: {status}")
    s.close()
print("Scan complete.")""",
            "subdomain_enum": """import requests
# EDUCATIONAL: Only test domains you own or have authorization for.
domain = input("Target domain (e.g., example.com): ")
wordlist = ["www", "mail", "ftp", "admin", "blog", "shop", "api", "dev"]
print(f"Enumerating subdomains for {domain}...")
for sub in wordlist:
    url = f"http://{sub}.{domain}"
    try:
        r = requests.get(url, timeout=3)
        print(f"  [FOUND] {url} -> Status {r.status_code}")
    except requests.RequestException:
        pass
print("Enumeration complete.")""",
            "directory_bruteforce": """import requests
# EDUCATIONAL: Only test applications you have written permission to assess.
base = input("Base URL (e.g., http://target.com): ").rstrip("/")
paths = ["admin", "login", "config", "backup", ".env", "api", "test"]
print(f"Brute-forcing directories on {base}...")
for path in paths:
    url = f"{base}/{path}"
    try:
        r = requests.get(url, timeout=4)
        if r.status_code != 404:
            print(f"  [{r.status_code}] {url}")
    except requests.RequestException:
        pass
print("Directory scan complete.")""",
            "hash_cracker": """import hashlib
# EDUCATIONAL: Crack only hashes you generated yourself for practice.
target = input("Enter MD5 hash: ")
wordlist = ["password", "123456", "admin", "letmein", "hacker", "ghostframe"]
print("Attempting to crack hash...")
for word in wordlist:
    if hashlib.md5(word.encode()).hexdigest() == target:
        print(f"  [CRACKED] Password: {word}")
        break
else:
    print("  Hash not found in wordlist.")""",
            "xss_tester": """import requests
# EDUCATIONAL: Test ONLY on your own applications or dedicated labs.
url = input("Enter URL with parameter (e.g., http://site.com/search?q=): ")
payloads = [
    "<script>alert('XSS')</script>",
    ""><img src=x onerror=alert('XSS')>",
    ""><svg onload=alert('XSS')>"
]
print("Testing for reflected XSS...")
for payload in payloads:
    test_url = f"{url}{payload}"
    try:
        r = requests.get(test_url, timeout=5)
        if payload in r.text:
            print(f"  [POTENTIAL XSS] Payload reflected: {payload[:40]}...")
    except requests.RequestException:
        pass
print("XSS test complete.")""",
            "sql_injection_tester": """import requests
# EDUCATIONAL: Test ONLY on your own applications or CTF labs.
url = input("Enter POST endpoint: ")
payloads = [
    "' OR '1'='1",
    "' UNION SELECT null,null--",
    "' AND 1=1--",
    "' AND 1=2--"
]
print("Testing for SQL injection...")
for payload in payloads:
    try:
        r = requests.post(url, data={"input": payload}, timeout=5)
        text = r.text.lower()
        if any(indicator in text for indicator in ["sql", "syntax", "mysql", "error", "union"]):
            print(f"  [POTENTIAL SQLi] Payload: {payload}")
    except requests.RequestException:
        pass
print("SQLi test complete.")""",
            "banner_grabber": """import socket
# EDUCATIONAL: Only grab banners from services you own.
target = input("Target IP: ")
port = int(input("Port: "))
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    s.connect((target, port))
    s.send(b"HEAD / HTTP/1.1\r\nHost: target\r\n\r\n")
    banner = s.recv(1024).decode(errors="ignore")
    print(f"Banner received:\n{banner}")
    s.close()
except Exception as e:
    print(f"Error: {e}")""",
        }

        task_lower = task.lower().replace(" ", "_")
        code = None
        for key, template in templates.items():
            if key in task_lower or task_lower in key:
                code = template
                break

        if not code:
            code = f"# Task: {task}
# No template found — write your implementation below
"

        intros = [
            "[COMPILING GHOSTS FROM TEMPLATES]",
            "[INJECTING LOGIC — FALLBACK MODE]",
            "[CODE CONSTRUCT ASSEMBLED]",
        ]
        return f"""{random.choice(intros)}

Task: {task}

```python
{code}
```

[NOTE] This is a template response. Full AI generation requires more server RAM.
       Code has been syntax-checked. Always test in a lab environment.

— Vex
[FALLBACK_MODE_ACTIVE]"""
