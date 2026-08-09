import requests
import subprocess
import re
from bs4 import BeautifulSoup
from typing import List, Dict

class RAGEngine:
    """
    Retrieval-Augmented Generation engine.
    Searches public security resources + uses terminal tools
    (lynx, curl, whois, dig) to extract clean intel.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })

    def check_terminal_tools(self) -> Dict[str, bool]:
        tools = {}
        for cmd in ["lynx", "curl", "whois", "dig", "host"]:
            try:
                subprocess.run([cmd, "--version"], capture_output=True, timeout=3)
                tools[cmd] = True
            except:
                tools[cmd] = False
        return tools

    def gather_context(self, query: str) -> str:
        sources = []
        q = query.lower()

        if any(k in q for k in ["xss", "cross site", "script", "injection", "portswigger", "burp"]):
            sources.extend(self._search_portswigger(query))
        if any(k in q for k in ["cve", "vulnerability", "exploit", "cvss", "mitre"]):
            sources.extend(self._search_cve(query))
        if any(k in q for k in ["learn", "tutorial", "room", "beginner", "path", "module"]):
            sources.extend(self._search_tryhackme(query))
        if any(k in q for k in ["owasp", "standard", "top 10", "guideline"]):
            sources.extend(self._search_owasp(query))
        if any(k in q for k in ["tool", "github", "script", "repo", "clone"]):
            sources.extend(self._search_github(query))
        if any(k in q for k in ["nmap", "scan", "port", "network", "recon"]):
            sources.append(self._get_nmap_cheatsheet())
        if any(k in q for k in ["sql", "sqli", "database", "injection"]):
            sources.append(self._get_sqli_reference())

        domain = self._extract_domain(query)
        if domain:
            sources.append(self._whois_context(domain))
            sources.append(self._dig_context(domain))

        seen = set()
        unique = []
        for s in sources:
            key = s[:80]
            if key not in seen and len(s) > 20:
                seen.add(key)
                unique.append(s)
        return "

".join(unique[:6])

    def _extract_domain(self, text: str) -> str:
        pattern = r"(?:https?://)?([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,})"
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        words = text.split()
        for w in words:
            if ".com" in w or ".org" in w or ".net" in w or ".io" in w:
                return w.strip(".,;:!?")
        return None

    def _lynx_dump(self, url: str) -> str:
        try:
            result = subprocess.run(
                ["lynx", "-dump", "-nolist", url],
                capture_output=True, text=True, timeout=12
            )
            text = result.stdout.strip()
            return text[:2500] if text else ""
        except:
            return ""

    def _curl_fetch(self, url: str) -> str:
        try:
            result = subprocess.run(
                ["curl", "-s", "-L", "-A", "Mozilla/5.0", url],
                capture_output=True, text=True, timeout=12
            )
            html = result.stdout
            try:
                import html2text
                h = html2text.HTML2Text()
                h.ignore_links = False
                text = h.handle(html)
                return text[:2500]
            except ImportError:
                soup = BeautifulSoup(html, "html.parser")
                return soup.get_text(separator="
", strip=True)[:2500]
        except:
            return ""

    def _whois_context(self, domain: str) -> str:
        try:
            result = subprocess.run(
                ["whois", domain],
                capture_output=True, text=True, timeout=10
            )
            out = result.stdout
            lines = [l for l in out.split("
") if any(k in l.lower() for k in [
                "registrant", "name server", "creation", "expiration", "org", "country", "email"
            ])]
            return f"[WHOIS {domain}]:
" + "
".join(lines[:15])
        except:
            return ""

    def _dig_context(self, domain: str) -> str:
        try:
            result = subprocess.run(
                ["dig", "+short", domain],
                capture_output=True, text=True, timeout=10
            )
            ips = result.stdout.strip()
            if ips:
                return f"[DIG {domain}]:
{ips}"
            return ""
        except:
            return ""

    def _search_portswigger(self, query: str) -> List[str]:
        try:
            url = "https://portswigger.net/web-security"
            text = self._lynx_dump(url) or self._curl_fetch(url)
            lines = text.split("
")
            keywords = query.lower().split()
            relevant = [l for l in lines if any(k in l.lower() for k in keywords) and len(l) > 10]
            if relevant:
                return [f"[PortSwigger Web Security]:
" + "
".join(relevant[:10])]
            return [f"[PortSwigger]: Visit https://portswigger.net/web-security for {query}"]
        except Exception as e:
            return [f"[PortSwigger]: Error — {e}"]

    def _search_cve(self, query: str) -> List[str]:
        try:
            keyword = query.replace(" ", "+")
            url = f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={keyword}"
            r = self.session.get(url, timeout=12)
            soup = BeautifulSoup(r.text, "html.parser")
            items = []
            for row in soup.find_all("tr")[1:4]:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    cve_id = cells[0].text.strip()
                    summary = cells[1].text.strip()
                    items.append(f"{cve_id}: {summary}")
            if items:
                return [f"[CVE.mitre.org]:
" + "
".join(items)]
            return [f"[CVE]: No direct results for '{query}'. Search: https://cve.mitre.org/"]
        except Exception as e:
            return [f"[CVE]: Error — {e}"]

    def _search_tryhackme(self, query: str) -> List[str]:
        try:
            url = "https://tryhackme.com/modules"
            text = self._lynx_dump(url) or self._curl_fetch(url)
            lines = text.split("
")
            keywords = query.lower().split()
            relevant = [l.strip() for l in lines if any(k in l.lower() for k in keywords) and len(l.strip()) > 5]
            if relevant:
                return [f"[TryHackMe]:
" + "
".join(relevant[:8])]
            return [f"[TryHackMe]: Search rooms at https://tryhackme.com/modules"]
        except Exception as e:
            return [f"[TryHackMe]: Error — {e}"]

    def _search_owasp(self, query: str) -> List[str]:
        try:
            url = "https://owasp.org/www-project-top-ten/"
            text = self._lynx_dump(url) or self._curl_fetch(url)
            lines = text.split("
")
            keywords = query.lower().split()
            relevant = [l.strip() for l in lines if any(k in l.lower() for k in keywords) and len(l.strip()) > 10]
            if relevant:
                return [f"[OWASP Top 10]:
" + "
".join(relevant[:10])]
            return [f"[OWASP]: Visit https://owasp.org/www-project-top-ten/"]
        except Exception as e:
            return [f"[OWASP]: Error — {e}"]

    def _search_github(self, query: str) -> List[str]:
        try:
            q = f"{query.replace(' ', '+')}+ethical+hacking+python"
            url = f"https://github.com/search?q={q}&type=repositories"
            r = self.session.get(url, timeout=12)
            soup = BeautifulSoup(r.text, "html.parser")
            items = []
            for a in soup.find_all("a", class_="v-align-middle")[:5]:
                items.append(a.text.strip())
            if items:
                return [f"[GitHub Repos]:
" + "
".join(items)]
            return [f"[GitHub]: Search https://github.com/search?q={q}"]
        except Exception as e:
            return [f"[GitHub]: Error — {e}"]

    def _get_nmap_cheatsheet(self) -> str:
        return """[NMAP REFERENCE]:
nmap -sS -T4 target        # SYN scan
nmap -sV -p- target        # Version scan all ports
nmap -A target             # Aggressive scan (OS + version + scripts)
nmap -sn 192.168.1.0/24    # Host discovery (ping sweep)
nmap --script vuln target  # Vulnerability scan
"""

    def _get_sqli_reference(self) -> str:
        return """[SQL INJECTION REFERENCE]:
' OR '1'='1' --            # Basic bypass
' UNION SELECT null,null--  # Union probe
' AND 1=1--                # True condition test
' AND 1=2--                # False condition test
Use sqlmap for automation: sqlmap -u "http://target.com/page.php?id=1"
"""
