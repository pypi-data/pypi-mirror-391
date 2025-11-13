#!/usr/bin/env python3
"""
Pensity - Advanced JavaScript File Discovery and Security Analysis Tool
Author: iosec
"""

import re
import sys
import argparse
import requests
from urllib.parse import urljoin, urlparse, parse_qs
import json
from collections import defaultdict
import time
import os
import concurrent.futures
from bs4 import BeautifulSoup
import urllib3
import ssl
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class JSSpiderAnalyzer:
    def __init__(self, verify_ssl=False, proxy=None, timeout=10, allow_subdomains=False, delay=0.0):
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.allow_subdomains = allow_subdomains
        self.delay = delay
        self.patterns = {
            'api_keys': [
                r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,60})["\']',
                r'apikey["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,60})["\']',
                r'secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,60})["\']',
                r'key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,60})["\']',
            ],
            'jwt_tokens': [
                r'eyJhbGciOiJ[^\s"\']+',
                r'["\']eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+["\']',
            ],
            'passwords': [
                r'password["\']?\s*[:=]\s*["\']([^"\'\s]{3,50})["\']',
                r'pass["\']?\s*[:=]\s*["\']([^"\'\s]{3,50})["\']',
                r'pwd["\']?\s*[:=]\s*["\']([^"\'\s]{3,50})["\']',
                r'psw["\']?\s*[:=]\s*["\']([^"\'\s]{3,50})["\']',
            ],
            'endpoints': [
                r'["\'](https?://[^"\']+?/api/[^"\']*?)["\']',
                r'["\'](/api/[^"\']*?)["\']',
                r'["\'](https?://[^"\']+?/v[0-9]/[^"\']*?)["\']',
                r'["\'](https?://[^"\']+?/graphql[^"\']*?)["\']',
                r'["\'](https?://[^"\']+?/rest/[^"\']*?)["\']',
                r'["\'](https?://[^"\']+?/auth[^"\']*?)["\']',
                r'["\'](https?://[^"\']+?/login[^"\']*?)["\']',
                r'["\'](https?://[^"\']+?/register[^"\']*?)["\']',
                r'["\'](https?://[^"\']+?/user[^"\']*?)["\']',
                r'["\'](https?://[^"\']+?/admin[^"\']*?)["\']',
            ],
            'aws_keys': [
                r'AKIA[0-9A-Z]{16}',
                r'aws[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([^"\']+?)["\']',
                r'aws[_-]?secret[_-]?key["\']?\s*[:=]\s*["\']([^"\']+?)["\']',
            ],
            'database_urls': [
                r'mongodb[+]srv://[^"\'\s]+',
                r'postgresql://[^"\'\s]+',
                r'mysql://[^"\'\s]+',
                r'redis://[^"\'\s]+',
                r'database["\']?\s*[:=]\s*["\']([^"\']+?)["\']',
            ],
            'emails': [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            ],
            'ip_addresses': [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            ]
        }
        
        self.critical_endpoints = [
            'login', 'register', 'auth', 'password', 'reset', 'admin',
            'user', 'account', 'profile', 'payment', 'credit', 'bank',
            'secret', 'key', 'token', 'oauth', 'callback', 'api'
        ]
        
        self.js_patterns = [
            r'src=["\']([^"\']*?\.js(?:\?[^"\']*)?)["\']',
            r'<script[^>]*src=["\']([^"\']*?\.js(?:\?[^"\']*)?)["\']',
            r'import[^;]+from["\']([^"\']*?\.js)["\']',
            r'require\(["\']([^"\']*?\.js)["\']',
            r'["\']([^"\']*?\.js)["\']',
        ]
        
        self.discovered_js = set()
        self.analyzed_urls = set()
        self.results = defaultdict(list)
        self.js_files_data = []  # Store JS files with content and metadata for LLM analysis
        self.html_files_data = []  # Store HTML files with content and metadata for LLM analysis
        self.endpoint_data = []  # Store endpoint responses with metadata for LLM analysis

        # Common HTML pages to check
        self.common_html_pages = [
            'index.html', 'index.htm',
            'login.html', 'login.htm', 'signin.html', 'signin.htm', 'sign-in.html',
            'register.html', 'register.htm', 'signup.html', 'signup.htm', 'sign-up.html',
            'auth.html', 'auth.htm', 'authenticate.html', 'authentication.html',
            'logout.html', 'logout.htm', 'signout.html', 'sign-out.html',
            'dashboard.html', 'dashboard.htm', 'admin.html', 'admin.htm',
            'profile.html', 'profile.htm', 'account.html', 'account.htm',
            'settings.html', 'settings.htm', 'preferences.html',
            'forgot-password.html', 'forgot.html', 'reset-password.html', 'reset.html',
            'verify.html', 'verify-email.html', 'confirm.html', 'confirmation.html',
            'home.html', 'home.htm', 'main.html', 'main.htm',
            'user.html', 'users.html', 'member.html', 'members.html',
            'checkout.html', 'payment.html', 'billing.html',
            'api.html', 'docs.html', 'documentation.html',
            'error.html', '404.html', '403.html', '500.html',
        ]

        self.session = requests.Session()
        self.session.verify = self.verify_ssl
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        if proxy:
            self.session.proxies.update({'http': proxy, 'https': proxy})

    def print_header(self):
        """Print tool header"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("┌──────────────────────────────────────────────────────────────┐")
        print("│                    Pensity by iosec                          │")
        print("│         Advanced Security Analysis & Discovery Tool         │")
        print("└──────────────────────────────────────────────────────────────┘")
        print(f"{Colors.END}")

    def discover_js_files(self, base_url, depth=1, threads=5):
        """Discover JS files using a BFS crawl up to the specified depth.

        Depth 1 scans only the base_url. Higher depths follow in-scope links.
        Scope defaults to same-origin; include subdomains if allow_subdomains is True.
        """
        print(f"{Colors.BLUE}[*]{Colors.END} Discovering JS files: {Colors.CYAN}{base_url}{Colors.END}")

        discovered_urls = set()
        visited_pages = set()

        parsed_base = urlparse(base_url)
        base_netloc = parsed_base.netloc

        def normalize(u):
            try:
                pu = urlparse(u)
                pu = pu._replace(fragment='')
                return pu.geturl()
            except Exception:
                return u

        def in_scope(u):
            try:
                pu = urlparse(u)
                if pu.scheme not in ("http", "https"):
                    return False
                if pu.netloc == base_netloc:
                    return True
                if self.allow_subdomains and pu.netloc.endswith('.' + base_netloc.split(':')[0]):
                    return True
                return False
            except Exception:
                return False

        def fetch(url):
            try:
                if self.delay:
                    time.sleep(self.delay)
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                return resp.text
            except requests.exceptions.SSLError as e:
                print(f"{Colors.YELLOW}[!]{Colors.END} SSL Error: {e}")
                if not self.verify_ssl:
                    print(f"{Colors.BLUE}[*]{Colors.END} Retrying with SSL verification disabled...")
                    self.session.verify = False
                    try:
                        resp = self.session.get(url, timeout=self.timeout)
                        resp.raise_for_status()
                        return resp.text
                    except Exception:
                        return None
                return None
            except Exception as e:
                print(f"{Colors.RED}[!]{Colors.END} Discovery error {url}: {e}")
                return None

        # Always check robots.txt of the base URL
        try:
            robots_js = self.check_robots_txt(base_url)
            discovered_urls.update(robots_js)
        except Exception:
            pass

        current_level = [normalize(base_url)]
        visited_pages.add(normalize(base_url))
        lvl = 0
        while current_level and lvl < depth:
            next_level = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                future_to_url = {executor.submit(fetch, url): url for url in current_level}
                for future in concurrent.futures.as_completed(future_to_url):
                    page_url = future_to_url[future]
                    html = future.result()
                    if not html:
                        continue

                    # JS discovery from this page
                    js_files = self.extract_js_from_html(html, page_url)
                    discovered_urls.update(js_files)
                    additional_js = self.find_js_in_content(html, page_url)
                    discovered_urls.update(additional_js)

                    # Link discovery for next level
                    try:
                        soup = BeautifulSoup(html, 'html.parser')
                        for a in soup.find_all('a', href=True):
                            link = urljoin(page_url, a['href'])
                            link = normalize(link)
                            if link not in visited_pages and in_scope(link):
                                visited_pages.add(link)
                                next_level.append(link)
                    except Exception:
                        pass

            lvl += 1
            current_level = next_level

        return discovered_urls

    def extract_js_from_html(self, html_content, base_url):
        """Extract JS files from HTML"""
        js_files = set()
        
        try:
            # BeautifulSoup parsing
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find script tags
            for script in soup.find_all('script'):
                src = script.get('src')
                if src and '.js' in src:
                    full_url = urljoin(base_url, src)
                    js_files.add(full_url)
            
            # Find JS in links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '.js' in href:
                    full_url = urljoin(base_url, href)
                    js_files.add(full_url)
                    
        except Exception as e:
            print(f"{Colors.RED}[!]{Colors.END} HTML parsing error: {e}")
        
        return js_files

    def find_js_in_content(self, content, base_url):
        """Find JS references in content"""
        js_files = set()
        
        for pattern in self.js_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                js_path = match.group(1)
                if js_path and '.js' in js_path:
                    full_url = urljoin(base_url, js_path)
                    js_files.add(full_url)
        
        return js_files

    def check_robots_txt(self, base_url):
        """Find JS files from robots.txt"""
        js_files = set()
        
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=self.timeout)
            
            if response.status_code == 200:
                lines = response.text.split('\n')
                for line in lines:
                    if 'Disallow:' in line or 'Allow:' in line:
                        path = line.split(':')[1].strip()
                        if '.js' in path:
                            full_url = urljoin(base_url, path)
                            js_files.add(full_url)
        except:
            pass
        
        return js_files

    def fetch_js_content(self, url):
        """Download JS file content"""
        if url in self.analyzed_urls:
            return None
            
        self.analyzed_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Only analyze JavaScript files
            content_type = response.headers.get('content-type', '')
            if 'javascript' in content_type or url.endswith('.js') or '.js?' in url:
                return response.text
            else:
                print(f"{Colors.YELLOW}[!]{Colors.END} Not a JavaScript file: {url}")
                return None
                
        except requests.exceptions.SSLError as e:
            print(f"{Colors.YELLOW}[!]{Colors.END} SSL Error for {url}: {e}")
            if not self.verify_ssl:
                print(f"{Colors.BLUE}[*]{Colors.END} Retrying with SSL verification disabled...")
                self.session.verify = False
                return self.fetch_js_content(url)
        except Exception as e:
            print(f"{Colors.RED}[!]{Colors.END} Download error {url}: {e}")
            return None

    def extract_http_requests_advanced(self, content):
        """Advanced HTTP request analysis"""
        requests_found = []
        
        # Fetch API patterns
        fetch_patterns = [
            r'fetch\([\s]*["\']([^"\']+?)["\'][\s]*(?:,[\s]*({[^}]+?(?:{[^}]*?}[^}]*?)?}))?[\s]*\)',
            r'fetch\([\s]*`([^`]+?)`[\s]*(?:,[\s]*({[^}]+?(?:{[^}]*?}[^}]*?)?}))?[\s]*\)',
        ]
        
        for pattern in fetch_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                url = match.group(1).strip()
                options = match.group(2) if match.group(2) else None
                
                method = 'GET'
                headers = {}
                body = None
                
                if options:
                    method_match = re.search(r'method[\s]*:[\s]*["\']([^"\']+?)["\']', options, re.IGNORECASE)
                    if method_match:
                        method = method_match.group(1).upper()
                
                request_info = {
                    'type': 'fetch',
                    'method': method,
                    'url': url,
                    'full_match': match.group(0)[:200] + '...' if len(match.group(0)) > 200 else match.group(0)
                }
                requests_found.append(request_info)
        
        # Axios patterns
        axios_patterns = [
            r'axios\.(get|post|put|delete|patch)\([\s]*["\']([^"\']+?)["\']',
            r'axios\([\s]*{[\s]*method[\s]*:[\s]*["\'](GET|POST|PUT|DELETE|PATCH)["\'][^}]+url[\s]*:[\s]*["\']([^"\']+?)["\']',
        ]
        
        for pattern in axios_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:
                    method = match.group(1).upper()
                    url = match.group(2)
                else:
                    method = match.group(2).upper() if match.group(2) else 'GET'
                    url = match.group(1)
                
                request_info = {
                    'type': 'axios',
                    'method': method,
                    'url': url,
                }
                requests_found.append(request_info)
        
        # XMLHttpRequest patterns
        xhr_pattern = r'\.open\([\s]*["\'](GET|POST|PUT|DELETE)["\'][\s]*,[\s]*["\']([^"\']+?)["\']'
        matches = re.finditer(xhr_pattern, content)
        for match in matches:
            request_info = {
                'type': 'xhr',
                'method': match.group(1),
                'url': match.group(2),
            }
            requests_found.append(request_info)
        
        # jQuery patterns ($.ajax, $.get, $.post, $.getJSON)
        jquery_simple = r'\$\.(get|post|getJSON|put|delete)\(\s*["\']([^"\']+?)["\']'
        for match in re.finditer(jquery_simple, content, re.IGNORECASE):
            method = match.group(1).upper()
            url = match.group(2)
            requests_found.append({'type': 'jquery', 'method': method, 'url': url})

        jquery_ajax = r'\$\.ajax\(\s*{[^}]*url\s*:\s*["\']([^"\']+?)["\'][^}]*}\s*\)'
        for match in re.finditer(jquery_ajax, content, re.DOTALL | re.IGNORECASE):
            url = match.group(1)
            # Try to capture method/type inside the object
            snippet = match.group(0)
            m = re.search(r'(?:method|type)\s*:\s*["\'](GET|POST|PUT|DELETE|PATCH)["\']', snippet, re.IGNORECASE)
            method = m.group(1).upper() if m else 'GET'
            requests_found.append({'type': 'jquery', 'method': method, 'url': url})

        return requests_found

    def analyze_parameters(self, url):
        """Analyze URL parameters"""
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            path_params = re.findall(r'/:([a-zA-Z_]\w*)', parsed.path)
            
            return {
                'query_params': list(query_params.keys()),
                'path_params': path_params,
            }
        except:
            return {'query_params': [], 'path_params': []}

    def is_critical_endpoint(self, url):
        """Check if endpoint is critical"""
        url_lower = url.lower()
        for critical in self.critical_endpoints:
            if critical in url_lower:
                return True, critical
        return False, None

    def scan_js_content(self, content, url):
        """Scan JS content for sensitive data"""
        local_results = defaultdict(list)
        
        # Pattern scanning
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    
                    local_results[category].append({
                        'value': value,
                        'source_url': url,
                        'context': content[max(0, match.start()-50):match.end()+50],
                    })
        
        # HTTP request analysis
        http_requests = self.extract_http_requests_advanced(content)
        for req in http_requests:
            param_analysis = self.analyze_parameters(req['url'])
            req.update(param_analysis)
            
            is_critical, critical_type = self.is_critical_endpoint(req['url'])
            req['is_critical'] = is_critical
            req['critical_type'] = critical_type
            req['source_url'] = url
            
            local_results['http_requests'].append(req)
        
        return local_results

    def analyze_discovered_js(self, js_urls, max_workers=5, store_content=False):
        """Analyze discovered JS files"""
        print(f"{Colors.BLUE}[*]{Colors.END} Analyzing {Colors.CYAN}{len(js_urls)}{Colors.END} JS files...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.analyze_single_js, url, store_content): url
                for url in js_urls
            }

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"{Colors.RED}[!]{Colors.END} Analysis error {url}: {e}")

    def analyze_single_js(self, url, store_content=False):
        """Analyze single JS file"""
        print(f"{Colors.BLUE}[>]{Colors.END} Downloading: {Colors.CYAN}{url}{Colors.END}")

        content = self.fetch_js_content(url)
        if not content:
            return

        print(f"{Colors.GREEN}[+]{Colors.END} Analyzing: {Colors.CYAN}{url}{Colors.END} ({Colors.YELLOW}{len(content):,}{Colors.END} chars)")

        # Store content if requested (for LLM analysis)
        if store_content:
            self.js_files_data.append({
                'url': url,
                'content': content,
                'size': len(content),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })

        results = self.scan_js_content(content, url)

        # Add results to global results
        for category, items in results.items():
            self.results[category].extend(items)

    def print_comprehensive_report(self, base_url):
        """Print comprehensive report"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}                  COMPREHENSIVE ANALYSIS REPORT{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")
        print(f"{Colors.WHITE}🔗 Target Site: {Colors.CYAN}{base_url}{Colors.END}")
        print(f"{Colors.WHITE}📅 Scan Date: {Colors.CYAN}{time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print(f"{Colors.WHITE}📁 Discovered JS Files: {Colors.CYAN}{len(self.analyzed_urls)}{Colors.END}")
        print(f"{Colors.CYAN}{'─'*70}{Colors.END}")
        
        # Discovered JS files
        if self.analyzed_urls:
            print(f"\n{Colors.GREEN}📂 DISCOVERED JS FILES ({len(self.analyzed_urls)}):{Colors.END}")
            for i, url in enumerate(list(self.analyzed_urls)[:20], 1):
                print(f"   {Colors.WHITE}{i:2d}. {Colors.CYAN}{url}{Colors.END}")
        
        # Critical findings
        self.print_critical_findings()
        
        # HTTP requests
        self.print_http_requests()
        
        # Other findings
        self.print_other_findings()
        
        # Summary
        self.print_summary()

    def print_critical_findings(self):
        """Print critical findings with color coding"""
        critical_categories = {
            'passwords': Colors.RED,
            'aws_keys': Colors.RED, 
            'database_urls': Colors.RED,
            'api_keys': Colors.YELLOW,
            'jwt_tokens': Colors.YELLOW
        }
        
        found_critical = False
        
        for category, color in critical_categories.items():
            if self.results.get(category):
                found_critical = True
                icon = "🔴" if color == Colors.RED else "🟡"
                
                print(f"\n{color}{icon} CRITICAL {category.upper()} FOUND ({len(self.results[category])}):{Colors.END}")
                for i, item in enumerate(self.results[category][:10], 1):
                    print(f"   {Colors.WHITE}{i:2d}. {color}{item['value']}{Colors.END}")
                    print(f"       {Colors.WHITE}📎 Source: {Colors.CYAN}{item['source_url']}{Colors.END}")
                    if len(item['value']) < 50:  # Only show context for shorter values
                        print(f"       {Colors.WHITE}📝 Context: {Colors.YELLOW}...{item['context']}...{Colors.END}")
        
        if not found_critical:
            print(f"\n{Colors.GREEN}✅ No critical secrets found in JS files{Colors.END}")

    def print_http_requests(self):
        """Print HTTP requests with color coding"""
        if self.results.get('http_requests'):
            critical_requests = [r for r in self.results['http_requests'] if r.get('is_critical')]
            normal_requests = [r for r in self.results['http_requests'] if not r.get('is_critical')]
            
            if critical_requests:
                print(f"\n{Colors.RED}🚨 CRITICAL ENDPOINT REQUESTS ({len(critical_requests)}):{Colors.END}")
                for i, req in enumerate(critical_requests[:10], 1):
                    print(f"\n   {Colors.WHITE}{i:2d}. {Colors.RED}{req['method']} {req['url']}{Colors.END}")
                    print(f"       {Colors.WHITE}📎 Source: {Colors.CYAN}{req['source_url']}{Colors.END}")
                    print(f"       {Colors.WHITE}🔍 Type: {Colors.RED}{req.get('critical_type', 'N/A')}{Colors.END}")
                    
                    if req.get('query_params'):
                        print(f"       {Colors.WHITE}📋 Query Parameters: {Colors.YELLOW}{', '.join(req['query_params'])}{Colors.END}")
                    if req.get('path_params'):
                        print(f"       {Colors.WHITE}🛣️  Path Parameters: {Colors.YELLOW}{', '.join(req['path_params'])}{Colors.END}")
            
            if normal_requests:
                print(f"\n{Colors.BLUE}🌐 OTHER HTTP REQUESTS ({len(normal_requests)}):{Colors.END}")
                for i, req in enumerate(normal_requests[:5], 1):
                    print(f"   {Colors.WHITE}{i:2d}. {Colors.BLUE}{req['method']} {req['url']}{Colors.END}")
                    if req.get('query_params'):
                        print(f"       {Colors.WHITE}📋 Parameters: {Colors.YELLOW}{', '.join(req['query_params'])}{Colors.END}")
        else:
            print(f"\n{Colors.BLUE}ℹ️  No HTTP requests found in JS files{Colors.END}")

    def print_other_findings(self):
        """Print other findings"""
        other_categories = ['emails', 'ip_addresses', 'endpoints']
        found_other = False
        
        for category in other_categories:
            if self.results.get(category):
                found_other = True
                color = Colors.BLUE
                icon = "📧" if category == 'emails' else "🌐" if category == 'ip_addresses' else "🔗"
                
                print(f"\n{color}{icon} {category.upper()} FOUND ({len(self.results[category])}):{Colors.END}")
                for i, item in enumerate(self.results[category][:5], 1):
                    print(f"   {Colors.WHITE}{i:2d}. {Colors.CYAN}{item['value']}{Colors.END}")
                    print(f"       {Colors.WHITE}📎 Source: {Colors.CYAN}{item['source_url']}{Colors.END}")

    def print_summary(self):
        """Print colored summary"""
        total_findings = sum(len(items) for items in self.results.values())
        critical_requests = len([r for r in self.results.get('http_requests', []) if r.get('is_critical')])
        total_critical = sum(len(self.results.get(cat, [])) for cat in ['api_keys', 'jwt_tokens', 'passwords', 'aws_keys', 'database_urls'])
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")
        print(f"{Colors.WHITE}{Colors.BOLD}                    SCAN SUMMARY{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")
        print(f"   {Colors.WHITE}📁 Discovered JS Files: {Colors.GREEN}{len(self.analyzed_urls)}{Colors.END}")
        print(f"   {Colors.WHITE}🔴 Critical Secrets: {Colors.RED if total_critical > 0 else Colors.GREEN}{total_critical}{Colors.END}")
        print(f"   {Colors.WHITE}🌐 HTTP Requests: {Colors.BLUE}{len(self.results.get('http_requests', []))}{Colors.END}")
        print(f"   {Colors.WHITE}🚨 Critical Endpoints: {Colors.RED if critical_requests > 0 else Colors.GREEN}{critical_requests}{Colors.END}")
        print(f"   {Colors.WHITE}📊 Total Findings: {Colors.CYAN}{total_findings}{Colors.END}")
        
        # Security assessment
        if total_critical > 0 or critical_requests > 0:
            print(f"   {Colors.RED}⚡ SECURITY RISK: {Colors.BOLD}HIGH{Colors.END}")
        elif total_findings > 0:
            print(f"   {Colors.YELLOW}⚡ SECURITY RISK: {Colors.BOLD}MEDIUM{Colors.END}")
        else:
            print(f"   {Colors.GREEN}⚡ SECURITY RISK: {Colors.BOLD}LOW{Colors.END}")
            
        print(f"{Colors.CYAN}{'═'*70}{Colors.END}")

    def save_comprehensive_report(self, base_url, filename):
        """Save comprehensive report to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"inspectJS Analysis Report\n")
            f.write(f"Target: {base_url}\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Discovered JS Files: {len(self.analyzed_urls)}\n")
            f.write("="*70 + "\n\n")
            
            f.write("DISCOVERED JS FILES:\n")
            for url in self.analyzed_urls:
                f.write(f"- {url}\n")
            f.write("\n")
            
            for category, items in self.results.items():
                if items:
                    f.write(f"{category.upper()}:\n")
                    for item in items:
                        if isinstance(item, dict):
                            f.write(f"  - {item.get('value', str(item))}\n")
                            f.write(f"    Source: {item.get('source_url', 'N/A')}\n")
                        else:
                            f.write(f"  - {str(item)}\n")
                    f.write("\n")

    def save_json_report(self, base_url, filename):
        """Save a structured JSON report to file"""
        data = {
            'target': base_url,
            'scanned_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'discovered_js_files': list(self.analyzed_urls),
            'findings': self.results,
        }
        # Convert defaultdict to normal dict for JSON
        def serialize(obj):
            if isinstance(obj, defaultdict):
                return {k: serialize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [serialize(x) for x in obj]
            return obj
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serialize(data), f, ensure_ascii=False, indent=2)

    def run_llm_analysis(self, base_url):
        """Run LLM analysis on all collected JavaScript, HTML files and endpoint responses"""
        if not self.js_files_data and not self.html_files_data and not self.endpoint_data:
            print(f"{Colors.YELLOW}[!]{Colors.END} No files collected for LLM analysis")
            return

        try:
            import llm
        except ImportError:
            print(f"{Colors.RED}[!]{Colors.END} LLM library not found. Install with: pip install llm")
            return

        print(f"\n{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}              LLM VULNERABILITY ANALYSIS{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")

        total_items = len(self.js_files_data) + len(self.html_files_data) + len(self.endpoint_data)
        print(f"{Colors.BLUE}[*]{Colors.END} Analyzing {Colors.CYAN}{total_items}{Colors.END} items with LLM...")
        print(f"    {Colors.WHITE}JavaScript files: {Colors.CYAN}{len(self.js_files_data)}{Colors.END}")
        print(f"    {Colors.WHITE}HTML files: {Colors.CYAN}{len(self.html_files_data)}{Colors.END}")
        print(f"    {Colors.WHITE}Endpoints: {Colors.CYAN}{len(self.endpoint_data)}{Colors.END}")

        # Get default model
        model = llm.get_model()

        js_results = []
        html_results = []
        endpoint_results = []

        # Analyze JavaScript files
        if self.js_files_data:
            print(f"\n{Colors.BLUE}[*]{Colors.END} Analyzing JavaScript files...")
            for i, js_file in enumerate(self.js_files_data, 1):
                url = js_file['url']
                content = js_file['content']
                size = js_file['size']

                print(f"{Colors.BLUE}[{i}/{len(self.js_files_data)}]{Colors.END} Analyzing JS: {Colors.CYAN}{url}{Colors.END}")

                # Truncate very large files to avoid token limits
                max_chars = 20000
                truncated = False
                if len(content) > max_chars:
                    content = content[:max_chars]
                    truncated = True

                # Create the prompt
                prompt = f"""Analyze the following JavaScript code for potential security vulnerabilities.

Focus on:
- Authentication/authorization issues
- Hardcoded credentials or API keys
- Insecure data handling
- Exposed endpoints or sensitive URLs
- Cryptographic weaknesses
- Input validation issues
- XSS or injection vulnerabilities

Source: {url}
Size: {size:,} characters{' (truncated)' if truncated else ''}

JavaScript Code:
```javascript
{content}
```

Provide a concise analysis of any security concerns found."""

                try:
                    # Run the LLM analysis
                    response = model.prompt(prompt)
                    analysis = response.text()

                    js_results.append({
                        'url': url,
                        'size': size,
                        'truncated': truncated,
                        'analysis': analysis,
                        'timestamp': js_file['timestamp'],
                        'type': 'javascript'
                    })

                    print(f"{Colors.GREEN}[✓]{Colors.END} Analysis complete")

                except Exception as e:
                    print(f"{Colors.RED}[!]{Colors.END} LLM analysis error for {url}: {e}")
                    js_results.append({
                        'url': url,
                        'size': size,
                        'truncated': truncated,
                        'analysis': f"Error: {str(e)}",
                        'timestamp': js_file['timestamp'],
                        'type': 'javascript'
                    })

        # Analyze HTML files
        if self.html_files_data:
            print(f"\n{Colors.BLUE}[*]{Colors.END} Analyzing HTML files...")
            for i, html_file in enumerate(self.html_files_data, 1):
                url = html_file['url']
                content = html_file['content']
                size = html_file['size']

                print(f"{Colors.BLUE}[{i}/{len(self.html_files_data)}]{Colors.END} Analyzing HTML: {Colors.CYAN}{url}{Colors.END}")

                # Truncate very large files to avoid token limits
                max_chars = 20000
                truncated = False
                if len(content) > max_chars:
                    content = content[:max_chars]
                    truncated = True

                # Create the prompt
                prompt = f"""Analyze the following HTML page for potential security vulnerabilities.

Focus on:
- Forms without CSRF protection
- Exposed sensitive information in HTML/comments
- Insecure authentication forms (no HTTPS indicators, autocomplete issues)
- Inline scripts with potential XSS vulnerabilities
- Missing security headers indicators
- Exposed API endpoints or configurations
- Insecure form actions or methods
- Client-side validation bypasses
- Information disclosure in HTML comments

Source: {url}
Size: {size:,} characters{' (truncated)' if truncated else ''}

HTML Code:
```html
{content}
```

Provide a concise analysis of any security concerns found."""

                try:
                    # Run the LLM analysis
                    response = model.prompt(prompt)
                    analysis = response.text()

                    html_results.append({
                        'url': url,
                        'size': size,
                        'truncated': truncated,
                        'analysis': analysis,
                        'timestamp': html_file['timestamp'],
                        'type': 'html'
                    })

                    print(f"{Colors.GREEN}[✓]{Colors.END} Analysis complete")

                except Exception as e:
                    print(f"{Colors.RED}[!]{Colors.END} LLM analysis error for {url}: {e}")
                    html_results.append({
                        'url': url,
                        'size': size,
                        'truncated': truncated,
                        'analysis': f"Error: {str(e)}",
                        'timestamp': html_file['timestamp'],
                        'type': 'html'
                    })

        # Analyze endpoint responses
        if self.endpoint_data:
            print(f"\n{Colors.BLUE}[*]{Colors.END} Analyzing endpoint responses...")
            for i, endpoint in enumerate(self.endpoint_data, 1):
                url = endpoint['url']
                status_code = endpoint['status_code']
                status_desc = endpoint['status_desc']
                content = endpoint['content']
                headers = endpoint['headers']

                print(f"{Colors.BLUE}[{i}/{len(self.endpoint_data)}]{Colors.END} Analyzing endpoint: {Colors.CYAN}{endpoint['endpoint']}{Colors.END} ({status_code})")

                # Truncate very large responses
                max_chars = 15000
                truncated = False
                if len(content) > max_chars:
                    content = content[:max_chars]
                    truncated = True

                # Create the prompt
                prompt = f"""Analyze the following HTTP endpoint response for potential security vulnerabilities and misconfigurations.

Focus on:
- Information disclosure (error messages, stack traces, version info)
- Authentication/authorization weaknesses
- Exposed sensitive data or endpoints
- Missing security headers
- Misconfiguration indicators
- Potential for exploitation based on status code and response
- Debug information or development artifacts

Endpoint: {endpoint['endpoint']}
Full URL: {url}
Status Code: {status_code} {status_desc}
Response Time: {endpoint['response_time']:.2f}s

Response Headers:
{json.dumps(headers, indent=2)}

Response Content:
```
{content}
```

Provide a concise security analysis of this endpoint response."""

                try:
                    # Run the LLM analysis
                    response = model.prompt(prompt)
                    analysis = response.text()

                    endpoint_results.append({
                        'endpoint': endpoint['endpoint'],
                        'url': url,
                        'status_code': status_code,
                        'status_desc': status_desc,
                        'response_time': endpoint['response_time'],
                        'truncated': truncated,
                        'analysis': analysis,
                        'timestamp': endpoint['timestamp'],
                        'type': 'endpoint'
                    })

                    print(f"{Colors.GREEN}[✓]{Colors.END} Analysis complete")

                except Exception as e:
                    print(f"{Colors.RED}[!]{Colors.END} LLM analysis error for {endpoint['endpoint']}: {e}")
                    endpoint_results.append({
                        'endpoint': endpoint['endpoint'],
                        'url': url,
                        'status_code': status_code,
                        'status_desc': status_desc,
                        'response_time': endpoint['response_time'],
                        'truncated': truncated,
                        'analysis': f"Error: {str(e)}",
                        'timestamp': endpoint['timestamp'],
                        'type': 'endpoint'
                    })

        # Save results to markdown file
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        output_file = f"llm-{timestamp}.md"
        self.save_llm_markdown_report(base_url, js_results, html_results, endpoint_results, output_file)

        print(f"{Colors.GREEN}[+]{Colors.END} LLM analysis report saved to: {Colors.CYAN}{output_file}{Colors.END}")

    def save_llm_markdown_report(self, base_url, js_results, html_results, endpoint_results, filename):
        """Save LLM analysis results to a markdown file"""
        all_results = js_results + html_results + endpoint_results
        total_items = len(all_results)

        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Security Analysis Report\n\n")
            f.write(f"**Target:** {base_url}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Items Analyzed:** {total_items}\n")
            f.write(f"- JavaScript files: {len(js_results)}\n")
            f.write(f"- HTML files: {len(html_results)}\n")
            f.write(f"- Endpoints: {len(endpoint_results)}\n\n")
            f.write("---\n\n")

            # Table of Contents
            f.write("## Table of Contents\n\n")

            if js_results:
                f.write("### JavaScript Files\n\n")
                for i, result in enumerate(js_results, 1):
                    anchor = result['url'].replace('://', '-').replace('/', '-').replace('.', '-')
                    f.write(f"{i}. [{result['url']}](#{anchor})\n")
                f.write("\n")

            if html_results:
                f.write("### HTML Files\n\n")
                for i, result in enumerate(html_results, 1):
                    anchor = result['url'].replace('://', '-').replace('/', '-').replace('.', '-')
                    f.write(f"{i}. [{result['url']}](#{anchor})\n")
                f.write("\n")

            if endpoint_results:
                f.write("### Endpoints\n\n")
                for i, result in enumerate(endpoint_results, 1):
                    anchor = result['endpoint'].replace('/', '-').replace('.', '-')
                    f.write(f"{i}. [{result['endpoint']}](#{anchor}) - {result['status_code']} {result['status_desc']}\n")
                f.write("\n")

            f.write("---\n\n")

            # JavaScript Analysis
            if js_results:
                f.write("## JavaScript Files Analysis\n\n")
                for i, result in enumerate(js_results, 1):
                    anchor = result['url'].replace('://', '-').replace('/', '-').replace('.', '-')
                    f.write(f"### {i}. {result['url']} {{#{anchor}}}\n\n")
                    f.write(f"**Type:** JavaScript\n\n")
                    f.write(f"**Size:** {result['size']:,} characters\n\n")
                    f.write(f"**Analyzed:** {result['timestamp']}\n\n")

                    if result['truncated']:
                        f.write("**Note:** File was truncated for analysis due to size.\n\n")

                    f.write("#### Security Analysis\n\n")
                    f.write(f"{result['analysis']}\n\n")
                    f.write("---\n\n")

            # HTML Analysis
            if html_results:
                f.write("## HTML Files Analysis\n\n")
                for i, result in enumerate(html_results, 1):
                    anchor = result['url'].replace('://', '-').replace('/', '-').replace('.', '-')
                    f.write(f"### {i}. {result['url']} {{#{anchor}}}\n\n")
                    f.write(f"**Type:** HTML\n\n")
                    f.write(f"**Size:** {result['size']:,} characters\n\n")
                    f.write(f"**Analyzed:** {result['timestamp']}\n\n")

                    if result['truncated']:
                        f.write("**Note:** File was truncated for analysis due to size.\n\n")

                    f.write("#### Security Analysis\n\n")
                    f.write(f"{result['analysis']}\n\n")
                    f.write("---\n\n")

            # Endpoint Analysis
            if endpoint_results:
                f.write("## Endpoint Analysis\n\n")
                for i, result in enumerate(endpoint_results, 1):
                    anchor = result['endpoint'].replace('/', '-').replace('.', '-')
                    f.write(f"### {i}. {result['endpoint']} {{#{anchor}}}\n\n")
                    f.write(f"**Type:** Endpoint\n\n")
                    f.write(f"**URL:** {result['url']}\n\n")
                    f.write(f"**Status Code:** {result['status_code']} {result['status_desc']}\n\n")
                    f.write(f"**Response Time:** {result['response_time']:.2f}s\n\n")
                    f.write(f"**Analyzed:** {result['timestamp']}\n\n")

                    if result['truncated']:
                        f.write("**Note:** Response was truncated for analysis due to size.\n\n")

                    f.write("#### Security Analysis\n\n")
                    f.write(f"{result['analysis']}\n\n")
                    f.write("---\n\n")

            # Summary
            f.write("## Summary\n\n")
            f.write(f"This report analyzed {total_items} items from {base_url}:\n")
            f.write(f"- {len(js_results)} JavaScript files\n")
            f.write(f"- {len(html_results)} HTML files\n")
            f.write(f"- {len(endpoint_results)} endpoints\n\n")
            f.write("for potential security vulnerabilities using AI-powered analysis.\n\n")
            f.write("**Review the findings above and address any critical security issues.**\n")

    def discover_html_files(self, base_url):
        """Discover HTML files by checking index.html and trying common paths"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}              HTML FILE DISCOVERY{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")

        discovered_html = set()
        parsed_base = urlparse(base_url)
        base_path = f"{parsed_base.scheme}://{parsed_base.netloc}"

        # Step 1: Try to fetch index.html
        print(f"{Colors.BLUE}[*]{Colors.END} Fetching index.html...")
        index_urls = [
            urljoin(base_url, 'index.html'),
            urljoin(base_url, 'index.htm'),
            base_url if base_url.endswith('/') else base_url + '/',
        ]

        index_content = None
        index_url = None

        for url in index_urls:
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
                    index_content = response.text
                    index_url = url
                    discovered_html.add(url)
                    print(f"{Colors.GREEN}[+]{Colors.END} Found index: {Colors.CYAN}{url}{Colors.END}")
                    break
            except Exception:
                continue

        # Step 2: Extract HTML references from index.html
        if index_content:
            print(f"{Colors.BLUE}[*]{Colors.END} Extracting HTML references from index...")
            html_refs = self.extract_html_references(index_content, index_url)
            for ref in html_refs:
                discovered_html.add(ref)
                print(f"{Colors.GREEN}[+]{Colors.END} Found from index: {Colors.CYAN}{ref}{Colors.END}")

        # Step 3: Try common HTML pages
        print(f"{Colors.BLUE}[*]{Colors.END} Fuzzy searching for common HTML pages...")
        found_count = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {}
            for page in self.common_html_pages:
                # Try at base path
                test_url = urljoin(base_path + '/', page)
                if test_url not in discovered_html:
                    future_to_url[executor.submit(self.check_html_exists, test_url)] = test_url

                # Try in common directories
                for directory in ['/', '/pages/', '/auth/', '/user/', '/account/', '/admin/']:
                    test_url = urljoin(base_path + directory, page)
                    if test_url not in discovered_html:
                        future_to_url[executor.submit(self.check_html_exists, test_url)] = test_url

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    if future.result():
                        discovered_html.add(url)
                        found_count += 1
                        print(f"{Colors.GREEN}[+]{Colors.END} Found: {Colors.CYAN}{url}{Colors.END}")
                except Exception:
                    pass

        print(f"{Colors.GREEN}[+]{Colors.END} Total HTML files discovered: {Colors.CYAN}{len(discovered_html)}{Colors.END}")
        return discovered_html

    def extract_html_references(self, html_content, base_url):
        """Extract HTML file references from content"""
        html_files = set()

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find links to HTML files
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '.html' in href or '.htm' in href:
                    full_url = urljoin(base_url, href)
                    html_files.add(full_url)

            # Check forms action attributes
            for form in soup.find_all('form', action=True):
                action = form['action']
                if '.html' in action or '.htm' in action:
                    full_url = urljoin(base_url, action)
                    html_files.add(full_url)

        except Exception as e:
            print(f"{Colors.YELLOW}[!]{Colors.END} Error extracting HTML references: {e}")

        return html_files

    def check_html_exists(self, url):
        """Check if an HTML file exists at the given URL"""
        try:
            if self.delay:
                time.sleep(self.delay)

            response = self.session.get(url, timeout=self.timeout, allow_redirects=False)

            # Consider 200 as found, ignore 404, 403, 301/302 redirects
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type:
                    return True
            return False

        except Exception:
            return False

    def fetch_and_store_html(self, html_urls):
        """Fetch and store HTML files for analysis"""
        print(f"{Colors.BLUE}[*]{Colors.END} Fetching {Colors.CYAN}{len(html_urls)}{Colors.END} HTML files for analysis...")

        for url in html_urls:
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    content = response.text

                    self.html_files_data.append({
                        'url': url,
                        'content': content,
                        'size': len(content),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })

                    print(f"{Colors.GREEN}[+]{Colors.END} Stored: {Colors.CYAN}{url}{Colors.END} ({Colors.YELLOW}{len(content):,}{Colors.END} chars)")

            except Exception as e:
                print(f"{Colors.RED}[!]{Colors.END} Error fetching {url}: {e}")

    def load_common_endpoints(self, filename='common-endpoints.txt'):
        """Load common endpoints from file"""
        endpoints = []
        try:
            # Try package resource first (for installed package)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, filename)

            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        endpoints.append(line)

            return endpoints
        except FileNotFoundError:
            print(f"{Colors.YELLOW}[!]{Colors.END} Endpoints file not found: {filename}")
            # Return basic fallback list
            return ['/login', '/admin', '/api', '/dashboard', '/config', '/status']
        except Exception as e:
            print(f"{Colors.RED}[!]{Colors.END} Error loading endpoints: {e}")
            return []

    def test_endpoints(self, base_url, store_responses=False):
        """Test common endpoints and report interesting responses"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}              ENDPOINT DISCOVERY{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'═'*70}{Colors.END}")

        endpoints = self.load_common_endpoints()
        print(f"{Colors.BLUE}[*]{Colors.END} Testing {Colors.CYAN}{len(endpoints)}{Colors.END} common endpoints...")

        parsed_base = urlparse(base_url)
        base_path = f"{parsed_base.scheme}://{parsed_base.netloc}"

        interesting_responses = []

        # Status codes we consider interesting
        interesting_status_codes = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            301: 'Moved Permanently',
            302: 'Found',
            401: 'Unauthorized',
            403: 'Forbidden',
            405: 'Method Not Allowed',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable'
        }

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_endpoint = {}
            for endpoint in endpoints:
                test_url = urljoin(base_path, endpoint)
                future_to_endpoint[executor.submit(self.test_single_endpoint, test_url)] = (endpoint, test_url)

            for future in concurrent.futures.as_completed(future_to_endpoint):
                endpoint, test_url = future_to_endpoint[future]
                try:
                    result = future.result()
                    if result:
                        status_code, headers, content, response_time = result

                        # Check if status code is interesting
                        if status_code in interesting_status_codes:
                            status_desc = interesting_status_codes[status_code]

                            # Color code based on status
                            if status_code == 200:
                                color = Colors.GREEN
                                icon = "[+]"
                            elif status_code in [401, 403]:
                                color = Colors.YELLOW
                                icon = "[!]"
                            elif status_code >= 500:
                                color = Colors.RED
                                icon = "[!]"
                            else:
                                color = Colors.BLUE
                                icon = "[*]"

                            print(f"{color}{icon}{Colors.END} {Colors.CYAN}{endpoint}{Colors.END} → {color}{status_code} {status_desc}{Colors.END} ({response_time:.2f}s)")

                            interesting_responses.append({
                                'endpoint': endpoint,
                                'url': test_url,
                                'status_code': status_code,
                                'status_desc': status_desc,
                                'headers': dict(headers),
                                'content': content,
                                'response_time': response_time,
                                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                            })

                except Exception as e:
                    pass

        print(f"{Colors.GREEN}[+]{Colors.END} Found {Colors.CYAN}{len(interesting_responses)}{Colors.END} interesting endpoints")

        # Store responses for LLM analysis if requested
        if store_responses and interesting_responses:
            print(f"{Colors.BLUE}[*]{Colors.END} Storing responses for LLM analysis...")
            for resp in interesting_responses:
                # Only store responses with content
                if resp['content'] and len(resp['content']) > 0:
                    self.endpoint_data.append(resp)

            print(f"{Colors.GREEN}[+]{Colors.END} Stored {Colors.CYAN}{len(self.endpoint_data)}{Colors.END} endpoint responses")

        return interesting_responses

    def test_single_endpoint(self, url):
        """Test a single endpoint and return response details"""
        try:
            if self.delay:
                time.sleep(self.delay)

            start_time = time.time()
            response = self.session.get(url, timeout=self.timeout, allow_redirects=False)
            response_time = time.time() - start_time

            # Get content (truncate if too large)
            content = response.text
            if len(content) > 50000:
                content = content[:50000]

            return (
                response.status_code,
                response.headers,
                content,
                response_time
            )

        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.ConnectionError:
            return None
        except Exception:
            return None

def main():
    spider = JSSpiderAnalyzer()
    spider.print_header()
    
    parser = argparse.ArgumentParser(description='Pensity - Advanced Security Analysis & Discovery Tool')
    parser.add_argument('-u', '--url', required=True, help='Target website URL')
    parser.add_argument('-o', '--output', help='Save results to file')
    parser.add_argument('--json', dest='json_output', help='Save structured JSON report to file')
    parser.add_argument('-d', '--depth', type=int, default=1, help='Discovery depth (1-3)')
    parser.add_argument('-t', '--threads', type=int, default=5, help='Number of threads')
    parser.add_argument('--verify-ssl', action='store_true', help='Enable SSL verification')
    parser.add_argument('--proxy', help='HTTP/HTTPS proxy URL (e.g., http://127.0.0.1:8080)')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('--allow-subdomains', action='store_true', help='Include subdomains in crawl scope')
    parser.add_argument('--delay', type=float, default=0.0, help='Delay between requests in seconds')
    parser.add_argument('--js', action='store_true', help='Discover and analyze JavaScript files')
    parser.add_argument('--html', action='store_true', help='Discover and analyze HTML files (login, auth, register, etc.)')
    parser.add_argument('--fetch', action='store_true', help='Test common endpoints for interesting responses')
    parser.add_argument('--llm', action='store_true', help='Run LLM analysis on discovered files (requires --js, --html, and/or --fetch)')

    args = parser.parse_args()

    # Validation: at least one of --js, --html, or --fetch must be specified
    if not args.js and not args.html and not args.fetch:
        parser.error("At least one of --js, --html, or --fetch must be specified")
    
    spider = JSSpiderAnalyzer(
        verify_ssl=args.verify_ssl,
        proxy=args.proxy,
        timeout=args.timeout,
        allow_subdomains=args.allow_subdomains,
        delay=args.delay,
    )
    
    # Build analysis mode string
    modes = []
    if args.js:
        modes.append('JS')
    if args.html:
        modes.append('HTML')
    if args.fetch:
        modes.append('FETCH')
    mode_str = ' + '.join(modes)

    print(f"{Colors.BLUE}[*]{Colors.END} Target Site: {Colors.CYAN}{args.url}{Colors.END}")
    print(f"{Colors.BLUE}[*]{Colors.END} Analysis Mode: {Colors.CYAN}{mode_str}{Colors.END}")
    print(f"{Colors.BLUE}[*]{Colors.END} LLM Analysis: {Colors.CYAN}{'Enabled' if args.llm else 'Disabled'}{Colors.END}")
    print(f"{Colors.BLUE}[*]{Colors.END} Discovery Depth: {Colors.CYAN}{args.depth}{Colors.END}")
    print(f"{Colors.BLUE}[*]{Colors.END} Threads: {Colors.CYAN}{args.threads}{Colors.END}")
    print(f"{Colors.BLUE}[*]{Colors.END} Timeout: {Colors.CYAN}{args.timeout}s{Colors.END}")
    print(f"{Colors.BLUE}[*]{Colors.END} Allow Subdomains: {Colors.CYAN}{'Yes' if args.allow_subdomains else 'No'}{Colors.END}")
    if args.proxy:
        print(f"{Colors.BLUE}[*]{Colors.END} Proxy: {Colors.CYAN}{args.proxy}{Colors.END}")
    if args.delay:
        print(f"{Colors.BLUE}[*]{Colors.END} Delay: {Colors.CYAN}{args.delay}s{Colors.END}")
    print(f"{Colors.BLUE}[*]{Colors.END} SSL Verification: {Colors.CYAN}{'Enabled' if args.verify_ssl else 'Disabled'}{Colors.END}")
    print(f"\n{Colors.CYAN}{'─'*50}{Colors.END}")

    # JavaScript analysis
    if args.js:
        # Discover JS files
        print(f"{Colors.BLUE}[*]{Colors.END} Discovering JS files...")
        js_files = spider.discover_js_files(args.url, depth=args.depth, threads=args.threads)

        if not js_files:
            print(f"{Colors.YELLOW}[!]{Colors.END} No JS files found!")
        else:
            print(f"{Colors.GREEN}[+]{Colors.END} {Colors.CYAN}{len(js_files)}{Colors.END} JS files discovered")

            # Analyze JS files
            print(f"{Colors.BLUE}[*]{Colors.END} Analyzing JS files...")
            spider.analyze_discovered_js(js_files, max_workers=args.threads, store_content=args.llm)

            # Generate report
            spider.print_comprehensive_report(args.url)

            # Save to file(s)
            if args.output:
                spider.save_comprehensive_report(args.url, args.output)
                print(f"{Colors.GREEN}[+]{Colors.END} Full report saved to '{Colors.CYAN}{args.output}{Colors.END}'")
            if args.json_output:
                spider.save_json_report(args.url, args.json_output)
                print(f"{Colors.GREEN}[+]{Colors.END} JSON report saved to '{Colors.CYAN}{args.json_output}{Colors.END}'")

    # HTML analysis
    if args.html:
        html_files = spider.discover_html_files(args.url)
        if html_files:
            if args.llm:
                spider.fetch_and_store_html(html_files)
            else:
                print(f"{Colors.YELLOW}[!]{Colors.END} Use --llm flag to analyze HTML files")

    # Endpoint testing
    if args.fetch:
        endpoint_responses = spider.test_endpoints(args.url, store_responses=args.llm)
        if not args.llm and endpoint_responses:
            print(f"{Colors.YELLOW}[!]{Colors.END} Use --llm flag to analyze endpoint responses")

    # Run LLM analysis if requested
    if args.llm and (spider.js_files_data or spider.html_files_data or spider.endpoint_data):
        spider.run_llm_analysis(args.url)
    elif args.llm:
        print(f"{Colors.YELLOW}[!]{Colors.END} No data collected for LLM analysis")

if __name__ == "__main__":
    main()
