#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JATHNIEL-WEB-CRAWLER-PRO v2.0
Crawler web professionnel avec extraction de fichiers sensibles
Pour Ubuntu/WSL - Usage éducatif et tests de sécurité autorisés uniquement
"""

import os
import sys
import time
import json
import re
import hashlib
import threading
import queue
import socket
import urllib3
import shutil
from datetime import datetime
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
from typing import Dict, List, Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque, defaultdict

import requests
from bs4 import BeautifulSoup
import mimetypes

# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class JATHNIELCrawlerPro:
    """Crawler web professionnel avec extraction de fichiers sensibles"""
    
    def __init__(self):
        # Configuration
        self.config = {
            'max_depth': 3,
            'max_pages': 500,
            'max_files': 100,
            'threads': 10,
            'timeout': 30,
            'delay': 0.5,
            'user_agent': 'JATHNIEL-Crawler-Pro/2.0 (Educational; Security Testing)',
            'output_dir': './crawled_sites',
            'download_sensitive': True,
            'download_assets': True,
            'respect_robots': True,
            'javascript': False,
            'follow_redirects': True,
            'verify_ssl': False
        }
        
        # État
        self.target_url = ""
        self.target_domain = ""
        self.visited_urls = set()
        self.visited_files = set()
        self.queue = deque()
        self.results = {
            'pages': [],
            'assets': [],
            'sensitive_files': [],
            'forms': [],
            'links': [],
            'emails': [],
            'technologies': [],
            'admin_pages': [],
            'comments': [],
            'vulnerabilities': [],
            'statistics': {
                'total_pages': 0,
                'total_assets': 0,
                'total_sensitive': 0,
                'total_size': 0,
                'start_time': None,
                'end_time': None,
                'duration': 0
            }
        }
        
        self.lock = threading.Lock()
        self.scanning = False
        self.pause = False
        
        # Liste des fichiers sensibles à rechercher
        self.sensitive_files = [
            # Configuration
            '.env', 'wp-config.php', 'config.php', 'settings.py', 'appsettings.json',
            'web.config', 'php.ini', 'nginx.conf', 'httpd.conf', '.htaccess',
            'robots.txt', 'sitemap.xml', 'crossdomain.xml', 'clientaccesspolicy.xml',
            
            # Base de données
            '.sql', '.db', '.sqlite', '.sqlite3', '.dump', 'backup.sql',
            'database.sql', 'dump.sql', 'db_backup.sql', 'mydb.sql',
            
            # Archives
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz',
            'backup.zip', 'backup.rar', 'archive.tar', 'backup.tar.gz',
            
            # Code source
            '.git', '.gitignore', '.gitconfig', '.svn', '.hg', '.cvs',
            '.idea', '.vscode', '.project', '.classpath', '.settings',
            
            # Logs
            '.log', 'access.log', 'error.log', 'debug.log', 'system.log',
            
            # Fichiers système
            '.passwd', '.shadow', '.bash_history', '.bashrc', '.profile',
            'id_rsa', 'id_dsa', 'authorized_keys', 'known_hosts',
            
            # Certificats
            '.pem', '.crt', '.key', '.p12', '.pfx', '.cer',
            
            # Fichiers temporaires
            '.tmp', '.temp', '.swp', '.swo', '.bak', '.old', '.orig',
            '~', '.#', '.DS_Store', 'Thumbs.db',
            
            # Autres
            'composer.json', 'package.json', 'Gemfile', 'requirements.txt',
            'Dockerfile', 'docker-compose.yml', 'Makefile', 'Vagrantfile',
            'README.md', 'INSTALL', 'CHANGELOG', 'LICENSE', 'COPYING'
        ]
        
        # Extensions d'assets à télécharger
        self.asset_extensions = [
            '.css', '.js', '.json', '.xml', '.txt', '.md',
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.webp',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wav',
            '.woff', '.woff2', '.ttf', '.eot', '.otf'
        ]
        
        # Patterns d'admin
        self.admin_patterns = [
            'admin', 'administrator', 'login', 'signin', 'panel', 'dashboard',
            'backoffice', 'backend', 'cpanel', 'webmail', 'manager',
            'moderator', 'staff', 'sysadmin', 'root', 'control'
        ]
        
        # Patterns de technologies
        self.tech_patterns = {
            'WordPress': ['wp-content', 'wp-includes', 'wp-json', 'wp-admin'],
            'Drupal': ['drupal', 'sites/all', 'drupal.js'],
            'Joomla': ['joomla', 'com_content', 'modules/mod_'],
            'Laravel': ['laravel', 'csrf-token', '_token'],
            'Django': ['django', 'csrfmiddlewaretoken', 'admin/'],
            'Rails': ['rails', 'authenticity_token', 'application.js'],
            'Express': ['express', 'x-powered-by: express'],
            'Flask': ['flask', 'x-powered-by: flask'],
            'React': ['react', 'react-dom', 'react.min.js'],
            'Vue': ['vue.js', 'vue.min.js', 'v-bind'],
            'Angular': ['angular', 'ng-app', 'ng-controller'],
            'jQuery': ['jquery', 'jquery.min.js', 'jquery-'],
            'Bootstrap': ['bootstrap', 'navbar', 'bootstrap.min.css'],
            'FontAwesome': ['font-awesome', 'fa-', 'fa-solid'],
            'GoogleAnalytics': ['ga.js', 'gtag.js', 'analytics.js'],
            'Cloudflare': ['cf-ray', '__cfduid', 'cloudflare'],
            'AmazonAWS': ['aws.amazon', 'x-amz', 'amazonaws']
        }
        
        self.clear_screen()
        self.show_banner()
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def colorize(self, text, color='white', bold=False):
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
        bold_text = colors['bold'] if bold else ''
        return f"{colors.get(color, '')}{bold_text}{text}{colors['end']}"
    
    def show_banner(self):
        banner = f"""
{self.colorize('╔══════════════════════════════════════════════════════════════════════════════╗', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('██╗ █████╗ ████████╗██╗  ██╗███╗   ██╗██╗███████╗██╗     ██╗   ██╗', 'red')}  {self.colorize('║', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('██║██╔══██╗╚══██╔══╝██║  ██║████╗  ██║██║██╔════╝██║     ██║   ██║', 'red')}  {self.colorize('║', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('██║███████║   ██║   ███████║██╔██╗ ██║██║█████╗  ██║     ██║   ██║', 'red')}  {self.colorize('║', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('██║██╔══██║   ██║   ██╔══██║██║╚██╗██║██║██╔══╝  ██║     ██║   ██║', 'red')}  {self.colorize('║', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('██║██║  ██║   ██║   ██║  ██║██║ ╚████║██║███████╗███████╗╚██████╔╝', 'red')}  {self.colorize('║', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚══════╝ ╚═════╝ ', 'red')}  {self.colorize('║', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('                    WEB CRAWLER PRO v2.0 - JATHNIEL EDITION', 'yellow')}  {self.colorize('║', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('              🕷️  Crawler professionnel avec extraction avancée  🕷️', 'green')}  {self.colorize('║', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('              🛡️  Ethical Hacking Tool - JATHNIEL  🛡️', 'magenta')}  {self.colorize('║', 'cyan')}
{self.colorize('║', 'cyan')}  {self.colorize('                              ★  JATHNIEL  ★                                  ', 'yellow')}  {self.colorize('║', 'cyan')}
{self.colorize('╚══════════════════════════════════════════════════════════════════════════════╝', 'cyan')}
        """
        print(banner)
    
    def show_menu(self):
        """Affiche le menu principal"""
        status = self.colorize('● EN COURS', 'green') if self.scanning else self.colorize('○ ARRETE', 'red')
        
        menu = f"""
{self.colorize('┌────────────────────────────────────────────────────────────────────────────────────┐', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('MENU PRINCIPAL - WEB CRAWLER PRO', 'bold')}                                               {self.colorize('│', 'cyan')}
{self.colorize('├────────────────────────────────────────────────────────────────────────────────────┤', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('1.', 'yellow')}  {self.colorize('Lancer un crawl complet', 'white')}                                                 {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('2.', 'yellow')}  {self.colorize('Crawl avec extraction de fichiers sensibles', 'white')}                             {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('3.', 'yellow')}  {self.colorize('Télécharger un fichier spécifique', 'white')}                                       {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('4.', 'yellow')}  {self.colorize('Voir les résultats du crawl', 'white')}                                             {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('5.', 'yellow')}  {self.colorize('Voir les fichiers sensibles trouvés', 'white')}                                     {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('6.', 'yellow')}  {self.colorize('Exporter les résultats (JSON/HTML)', 'white')}                                      {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('7.', 'yellow')}  {self.colorize('Configuration', 'white')}                                                          {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('8.', 'yellow')}  {self.colorize('Statistiques du crawl', 'white')}                                                   {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('9.', 'yellow')}  {self.colorize('Aide / Documentation', 'white')}                                                    {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('0.', 'yellow')}  {self.colorize('Quitter', 'white')}                                                               {self.colorize('│', 'cyan')}
{self.colorize('├────────────────────────────────────────────────────────────────────────────────────┤', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('📌 Cible:', 'bold')} {self.target_url if self.target_url else self.colorize('Aucune', 'red')}  {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('📄 Pages:', 'bold')} {self.results['statistics']['total_pages']}  {self.colorize('📁 Sensibles:', 'bold')} {self.results['statistics']['total_sensitive']}  {self.colorize('│', 'cyan')}
{self.colorize('│', 'cyan')}  {self.colorize('📊 Statut:', 'bold')} {status}  {self.colorize('│', 'cyan')}
{self.colorize('└────────────────────────────────────────────────────────────────────────────────────┘', 'cyan')}
        """
        print(menu)
    
    def get_user_input(self, prompt, default=""):
        if default:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "
        return input(self.colorize(prompt, 'yellow')).strip() or default
    
    def get_yes_no(self, prompt):
        while True:
            response = input(self.colorize(f"{prompt} (o/n): ", 'yellow')).lower()
            if response in ['o', 'oui', 'y', 'yes']:
                return True
            elif response in ['n', 'non', 'no']:
                return False
            else:
                print(self.colorize("❌ Repondez par 'o' ou 'n'", 'red'))

    # ==================== MOTEUR DE CRAWL ====================
    
    def crawl_complete(self, url):
        """Crawl complet avec extraction de fichiers"""
        self.target_url = url
        self.target_domain = urlparse(url).netloc
        self.scanning = True
        
        # Créer le dossier de sortie
        site_dir = f"{self.config['output_dir']}/{self.target_domain}"
        os.makedirs(site_dir, exist_ok=True)
        os.makedirs(f"{site_dir}/pages", exist_ok=True)
        os.makedirs(f"{site_dir}/assets", exist_ok=True)
        os.makedirs(f"{site_dir}/sensitive", exist_ok=True)
        os.makedirs(f"{site_dir}/reports", exist_ok=True)
        
        print(f"\n{self.colorize('🕷️ Debut du crawl de:', 'cyan')} {url}")
        print(self.colorize("="*80, 'blue'))
        print(f"📁 Dossier de sortie: {site_dir}")
        print(f"📊 Max pages: {self.config['max_pages']}")
        print(f"📊 Max depth: {self.config['max_depth']}")
        print(f"🔍 Recherche de fichiers sensibles: {self.colorize('OUI', 'green') if self.config['download_sensitive'] else self.colorize('NON', 'red')}")
        print(self.colorize("="*80, 'blue'))
        
        self.results['statistics']['start_time'] = datetime.now()
        
        # Initialiser la file
        self.queue.append((url, 0))
        
        # Lancer les threads
        with ThreadPoolExecutor(max_workers=self.config['threads']) as executor:
            while self.queue and len(self.visited_urls) < self.config['max_pages']:
                if self.pause:
                    time.sleep(1)
                    continue
                
                try:
                    current_url, depth = self.queue.popleft()
                    if current_url in self.visited_urls:
                        continue
                    
                    # Soumettre la tâche
                    executor.submit(self.crawl_page, current_url, depth, site_dir)
                    time.sleep(self.config['delay'])
                except IndexError:
                    break
        
        # Analyse complémentaire
        print(self.colorize("\n🔍 Analyse complémentaire...", 'yellow'))
        self.detect_technologies()
        self.find_admin_pages()
        self.extract_emails()
        
        # Statistiques finales
        self.results['statistics']['end_time'] = datetime.now()
        self.results['statistics']['duration'] = (
            self.results['statistics']['end_time'] - 
            self.results['statistics']['start_time']
        ).total_seconds()
        
        self.scanning = False
        
        print(self.colorize("\n✅ Crawl termine!", 'green'))
        print(f"📄 Pages: {self.results['statistics']['total_pages']}")
        print(f"📁 Fichiers sensibles: {self.results['statistics']['total_sensitive']}")
        print(f"📦 Assets: {self.results['statistics']['total_assets']}")
        print(f"📊 Duree: {self.results['statistics']['duration']:.2f} secondes")
    
    def crawl_page(self, url, depth, site_dir):
        """Crawl une page individuelle"""
        if url in self.visited_urls:
            return
        
        with self.lock:
            self.visited_urls.add(url)
        
        try:
            response = requests.get(
                url, 
                headers={'User-Agent': self.config['user_agent']},
                timeout=self.config['timeout'],
                verify=self.config['verify_ssl'],
                allow_redirects=self.config['follow_redirects']
            )
            
            if response.status_code != 200:
                return
            
            # Sauvegarder la page
            page_filename = self.save_page(url, response.text, site_dir)
            
            # Ajouter aux résultats
            page_data = {
                'url': url,
                'depth': depth,
                'status': response.status_code,
                'size': len(response.content),
                'filename': page_filename
            }
            
            with self.lock:
                self.results['pages'].append(page_data)
                self.results['statistics']['total_pages'] += 1
                self.results['statistics']['total_size'] += len(response.content)
            
            print(f"  📄 {url} ({len(response.content)} octets)")
            
            # Extraire les liens
            if depth < self.config['max_depth']:
                links = self.extract_links(response.text, url)
                for link in links:
                    if link not in self.visited_urls:
                        with self.lock:
                            self.queue.append((link, depth + 1))
            
            # Extraire et télécharger les assets
            if self.config['download_assets']:
                self.extract_assets(response.text, url, site_dir)
            
            # Rechercher des fichiers sensibles dans la page
            if self.config['download_sensitive']:
                self.search_sensitive_in_page(response.text, url, site_dir)
            
            # Extraire les formulaires
            forms = self.extract_forms(response.text, url)
            with self.lock:
                self.results['forms'].extend(forms)
            
            # Extraire les commentaires
            comments = self.extract_comments(response.text, url)
            with self.lock:
                self.results['comments'].extend(comments)
            
        except Exception as e:
            pass
    
    def extract_links(self, html, base_url):
        """Extrait les liens d'une page"""
        links = set()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Liens <a>
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                absolute_url = urljoin(base_url, href)
                if self.target_domain in urlparse(absolute_url).netloc:
                    links.add(absolute_url)
        
        # Liens <link>
        for link in soup.find_all('link', href=True):
            href = link['href']
            if href:
                absolute_url = urljoin(base_url, href)
                if self.target_domain in urlparse(absolute_url).netloc:
                    links.add(absolute_url)
        
        return links
    
    def extract_assets(self, html, base_url, site_dir):
        """Extrait et télécharge les assets (CSS, JS, images, etc.)"""
        soup = BeautifulSoup(html, 'html.parser')
        assets_found = []
        
        # CSS
        for link in soup.find_all('link', rel='stylesheet', href=True):
            href = link['href']
            if href:
                absolute_url = urljoin(base_url, href)
                if any(href.endswith(ext) for ext in ['.css']):
                    assets_found.append(absolute_url)
        
        # JS
        for script in soup.find_all('script', src=True):
            src = script['src']
            if src:
                absolute_url = urljoin(base_url, src)
                if any(src.endswith(ext) for ext in ['.js']):
                    assets_found.append(absolute_url)
        
        # Images
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src:
                absolute_url = urljoin(base_url, src)
                if any(src.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico']):
                    assets_found.append(absolute_url)
        
        # Télécharger les assets
        for asset_url in assets_found:
            self.download_asset(asset_url, site_dir)
    
    def download_asset(self, url, site_dir):
        """Télécharge un asset"""
        if url in self.visited_files:
            return
        
        with self.lock:
            self.visited_files.add(url)
        
        try:
            response = requests.get(
                url,
                headers={'User-Agent': self.config['user_agent']},
                timeout=self.config['timeout'],
                verify=self.config['verify_ssl']
            )
            
            if response.status_code == 200:
                # Déterminer le nom du fichier
                filename = urlparse(url).path.split('/')[-1]
                if not filename:
                    filename = hashlib.md5(url.encode()).hexdigest()
                
                # Déterminer l'extension
                ext = os.path.splitext(filename)[1]
                if not ext:
                    content_type = response.headers.get('content-type', '')
                    ext = mimetypes.guess_extension(content_type) or '.bin'
                    filename += ext
                
                # Sauvegarder
                filepath = f"{site_dir}/assets/{filename}"
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                with self.lock:
                    self.results['assets'].append({
                        'url': url,
                        'filename': filename,
                        'size': len(response.content)
                    })
                    self.results['statistics']['total_assets'] += 1
                
                print(f"    📦 Asset téléchargé: {filename}")
                
        except Exception as e:
            pass
    
    def save_page(self, url, html, site_dir):
        """Sauvegarde une page"""
        filename = urlparse(url).path.replace('/', '_') or 'index'
        if not filename.endswith('.html'):
            filename += '.html'
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        filepath = f"{site_dir}/pages/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filename
    
    # ==================== FICHIERS SENSIBLES ====================
    
    def search_sensitive_in_page(self, html, url, site_dir):
        """Recherche des fichiers sensibles dans le contenu de la page"""
        # Vérifier les URLs dans le texte
        urls_in_page = re.findall(r'(?:href|src|action)=["\']([^"\']+)["\']', html, re.IGNORECASE)
        
        for file_url in urls_in_page:
            # Vérifier si c'est un fichier sensible
            for pattern in self.sensitive_files:
                if pattern.lower() in file_url.lower():
                    absolute_url = urljoin(url, file_url)
                    self.download_sensitive_file(absolute_url, site_dir)
        
        # Vérifier les chemins absolus
        paths = re.findall(r'([/a-zA-Z0-9_\-\.]+\.(?:' + '|'.join([p.replace('.', '') for p in self.sensitive_files if p.startswith('.')]) + r'))', html)
        for path in paths:
            absolute_url = urljoin(url, path)
            self.download_sensitive_file(absolute_url, site_dir)
    
    def download_sensitive_file(self, url, site_dir):
        """Télécharge un fichier sensible"""
        if url in self.visited_files:
            return
        
        with self.lock:
            self.visited_files.add(url)
        
        try:
            response = requests.get(
                url,
                headers={'User-Agent': self.config['user_agent']},
                timeout=self.config['timeout'],
                verify=self.config['verify_ssl']
            )
            
            if response.status_code == 200:
                # Déterminer le nom du fichier
                filename = urlparse(url).path.split('/')[-1]
                if not filename:
                    filename = hashlib.md5(url.encode()).hexdigest()
                
                # Ajouter l'extension si nécessaire
                if '.' not in filename:
                    content_type = response.headers.get('content-type', '')
                    ext = mimetypes.guess_extension(content_type) or '.bin'
                    filename += ext
                
                # Nettoyer le nom
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                
                # Sauvegarder
                filepath = f"{site_dir}/sensitive/{filename}"
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Ajouter aux résultats
                file_info = {
                    'url': url,
                    'filename': filename,
                    'size': len(response.content),
                    'path': filepath,
                    'type': self.classify_sensitive_file(filename)
                }
                
                with self.lock:
                    self.results['sensitive_files'].append(file_info)
                    self.results['statistics']['total_sensitive'] += 1
                
                print(f"    🔴 FICHIER SENSIBLE TELECHARGE: {filename}")
                print(f"        📍 {url}")
                print(f"        📦 {len(response.content)} octets")
                
                return True
                
        except Exception as e:
            pass
        
        return False
    
    def classify_sensitive_file(self, filename):
        """Classifie le type de fichier sensible"""
        filename_lower = filename.lower()
        
        if 'config' in filename_lower or '.env' in filename_lower:
            return 'Configuration'
        elif '.sql' in filename_lower or 'dump' in filename_lower or 'backup' in filename_lower:
            return 'Database'
        elif '.log' in filename_lower:
            return 'Log'
        elif '.key' in filename_lower or '.pem' in filename_lower or 'id_rsa' in filename_lower:
            return 'Certificate/Key'
        elif '.git' in filename_lower or '.svn' in filename_lower:
            return 'Version Control'
        elif 'wp-config' in filename_lower:
            return 'WordPress Config'
        elif 'robots.txt' in filename_lower or 'sitemap' in filename_lower:
            return 'SEO/Discovery'
        elif '.zip' in filename_lower or '.rar' in filename_lower or '.tar' in filename_lower:
            return 'Archive'
        elif 'backup' in filename_lower or 'bak' in filename_lower:
            return 'Backup'
        else:
            return 'Other'
    
    # ==================== ANALYSE AVANCÉE ====================
    
    def detect_technologies(self):
        """Détecte les technologies utilisées"""
        techs_found = set()
        
        for page in self.results['pages']:
            try:
                response = requests.get(
                    page['url'],
                    headers={'User-Agent': self.config['user_agent']},
                    timeout=5,
                    verify=self.config['verify_ssl']
                )
                
                headers = response.headers
                text = response.text
                
                for tech, patterns in self.tech_patterns.items():
                    for pattern in patterns:
                        if pattern.lower() in text.lower():
                            techs_found.add(tech)
                        if pattern.lower() in str(headers).lower():
                            techs_found.add(tech)
                
                # Détection serveur
                server = headers.get('Server', '')
                if 'nginx' in server.lower():
                    techs_found.add('Nginx')
                elif 'apache' in server.lower():
                    techs_found.add('Apache')
                elif 'cloudflare' in server.lower():
                    techs_found.add('Cloudflare')
                
            except:
                pass
        
        self.results['technologies'] = list(techs_found)
    
    def find_admin_pages(self):
        """Recherche des pages d'administration"""
        base_url = self.target_url.rstrip('/')
        admin_urls = []
        
        for pattern in self.admin_patterns:
            for ext in ['', '.php', '.html', '.asp', '.aspx']:
                url = f"{base_url}/{pattern}{ext}"
                try:
                    response = requests.get(
                        url,
                        headers={'User-Agent': self.config['user_agent']},
                        timeout=5,
                        verify=self.config['verify_ssl']
                    )
                    
                    if response.status_code == 200:
                        admin_urls.append(url)
                        print(f"    🔐 Page admin trouvee: {url}")
                        
                        # Télécharger la page admin si c'est un fichier sensible
                        if self.config['download_sensitive']:
                            self.download_sensitive_file(url, f"{self.config['output_dir']}/{self.target_domain}")
                        
                except:
                    pass
        
        self.results['admin_pages'] = admin_urls
    
    def extract_emails(self):
        """Extrait les adresses email"""
        emails = set()
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        
        for page in self.results['pages']:
            try:
                response = requests.get(
                    page['url'],
                    headers={'User-Agent': self.config['user_agent']},
                    timeout=5,
                    verify=self.config['verify_ssl']
                )
                found = email_pattern.findall(response.text)
                emails.update(found)
            except:
                pass
        
        self.results['emails'] = list(emails)
        if emails:
            print(f"\n    📧 Emails trouves: {len(emails)}")
            for email in list(emails)[:10]:
                print(f"        - {email}")
    
    def extract_forms(self, html, base_url):
        """Extrait les formulaires"""
        forms = []
        soup = BeautifulSoup(html, 'html.parser')
        
        for form in soup.find_all('form'):
            action = form.get('action', '')
            method = form.get('method', 'GET').upper()
            absolute_action = urljoin(base_url, action)
            
            fields = []
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                field = {
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', 'text'),
                    'required': input_tag.has_attr('required')
                }
                fields.append(field)
            
            has_csrf = any('csrf' in str(field).lower() or 'token' in str(field).lower() for field in fields)
            
            forms.append({
                'url': base_url,
                'action': absolute_action,
                'method': method,
                'fields': fields,
                'has_csrf': has_csrf
            })
        
        return forms
    
    def extract_comments(self, html, url):
        """Extrait les commentaires HTML"""
        comments = []
        comment_pattern = re.compile(r'<!--(.*?)-->', re.DOTALL)
        
        found = comment_pattern.findall(html)
        for comment in found:
            comment = comment.strip()
            if len(comment) > 10 and '<!--' not in comment:
                comments.append({
                    'page': url,
                    'comment': comment[:200]
                })
        
        return comments
    
    # ==================== FONCTIONS UTILITAIRES ====================
    
    def download_specific_file(self):
        """Télécharge un fichier spécifique"""
        print(self.colorize("\n📥 TELECHARGER UN FICHIER SPECIFIQUE", 'bold'))
        print(self.colorize("="*60, 'cyan'))
        
        url = self.get_user_input("URL du fichier", "")
        if not url:
            return
        
        if not self.target_domain:
            self.target_domain = urlparse(url).netloc
        
        site_dir = f"{self.config['output_dir']}/{self.target_domain}"
        os.makedirs(site_dir, exist_ok=True)
        os.makedirs(f"{site_dir}/sensitive", exist_ok=True)
        
        print(f"\n🔍 Tentative de telechargement: {url}")
        success = self.download_sensitive_file(url, site_dir)
        
        if success:
            print(self.colorize("\n✅ Fichier telecharge avec succes!", 'green'))
        else:
            print(self.colorize("\n❌ Echec du telechargement", 'red'))
        
        input(self.colorize("\nAppuyez sur Entree pour continuer...", 'blue'))
    
    def show_sensitive_files(self):
        """Affiche les fichiers sensibles trouvés"""
        if not self.results['sensitive_files']:
            print(self.colorize("\n❌ Aucun fichier sensible trouve", 'yellow'))
            return
        
        print(self.colorize("\n🔴 FICHIERS SENSIBLES TROUVES", 'bold'))
        print(self.colorize("="*60, 'cyan'))
        
        for i, file in enumerate(self.results['sensitive_files'], 1):
            print(f"\n{i}. {self.colorize(file['filename'], 'red')}")
            print(f"   📍 {file['url']}")
            print(f"   📦 {file['size']} octets")
            print(f"   📂 {file['path']}")
            print(f"   📋 Type: {self.colorize(file['type'], 'yellow')}")
    
    def show_results(self):
        """Affiche les résultats complets"""
        print(self.colorize("\n📊 RESULTATS DU CRAWL", 'bold'))
        print(self.colorize("="*60, 'cyan'))
        
        print(f"\n📄 Pages decouvertes: {len(self.results['pages'])}")
        print(f"📦 Assets telecharges: {len(self.results['assets'])}")
        print(f"🔴 Fichiers sensibles: {len(self.results['sensitive_files'])}")
        print(f"📝 Formulaires: {len(self.results['forms'])}")
        print(f"📧 Emails: {len(self.results['emails'])}")
        print(f"🔐 Pages admin: {len(self.results['admin_pages'])}")
        
        if self.results['technologies']:
            print(f"\n⚙️ Technologies detectees:")
            for tech in self.results['technologies']:
                print(f"  - {tech}")
        
        if self.results['emails']:
            print(f"\n📧 Emails trouves:")
            for email in self.results['emails'][:10]:
                print(f"  - {email}")
    
    def export_results(self):
        """Exporte les résultats"""
        print(self.colorize("\n📤 EXPORT DES RESULTATS", 'bold'))
        print(self.colorize("="*60, 'cyan'))
        
        print("Formats disponibles:")
        print("  1. JSON")
        print("  2. HTML")
        print("  3. CSV")
        
        choice = self.get_user_input("Choisissez le format", "1")
        
        site_dir = f"{self.config['output_dir']}/{self.target_domain}"
        os.makedirs(f"{site_dir}/reports", exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if choice == '1':
            filename = f"{site_dir}/reports/crawl_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(self.colorize(f"✅ Exporte dans: {filename}", 'green'))
        
        elif choice == '2':
            filename = f"{site_dir}/reports/crawl_report_{timestamp}.html"
            self.export_html_report(filename)
            print(self.colorize(f"✅ Exporte dans: {filename}", 'green'))
        
        elif choice == '3':
            filename = f"{site_dir}/reports/crawl_report_{timestamp}.csv"
            self.export_csv_report(filename)
            print(self.colorize(f"✅ Exporte dans: {filename}", 'green'))
        
        input(self.colorize("\nAppuyez sur Entree pour continuer...", 'blue'))
    
    def export_html_report(self, filename):
        """Exporte un rapport HTML"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Crawl Report - JATHNIEL</title>
    <style>
        body {{ font-family: Arial; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 10px; }}
        h1 {{ color: #d32f2f; }}
        .header {{ background: #1e1e1e; color: white; padding: 15px; border-radius: 5px; }}
        .stats {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .stat-box {{ background: #e3f2fd; padding: 15px; border-radius: 5px; flex: 1; min-width: 150px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #1976d2; }}
        .stat-label {{ font-size: 14px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #1e1e1e; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        .sensitive {{ background: #ffebee; border-left: 4px solid #d32f2f; }}
        .admin {{ background: #fff3e0; border-left: 4px solid #f57c00; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ Web Crawl Report</h1>
            <p>Generated by JATHNIEL-WEB-CRAWLER-PRO</p>
            <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Target: {self.target_url}</p>
        </div>
        
        <h2>📊 Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{self.results['statistics']['total_pages']}</div>
                <div class="stat-label">Pages</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{self.results['statistics']['total_assets']}</div>
                <div class="stat-label">Assets</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{self.results['statistics']['total_sensitive']}</div>
                <div class="stat-label">Sensitive Files</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(self.results['emails'])}</div>
                <div class="stat-label">Emails</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(self.results['admin_pages'])}</div>
                <div class="stat-label">Admin Pages</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{self.results['statistics']['duration']:.2f}s</div>
                <div class="stat-label">Duration</div>
            </div>
        </div>
        
        <h2>🔴 Sensitive Files</h2>
        <table>
            <tr>
                <th>#</th>
                <th>File</th>
                <th>Type</th>
                <th>Size</th>
                <th>URL</th>
            </tr>"""
        
        for i, file in enumerate(self.results['sensitive_files'], 1):
            html += f"""
            <tr class="sensitive">
                <td>{i}</td>
                <td>{file['filename']}</td>
                <td>{file['type']}</td>
                <td>{file['size']} bytes</td>
                <td><a href="{file['url']}" target="_blank">{file['url'][:50]}...</a></td>
            </tr>"""
        
        html += """
        </table>
        
        <h2>🔐 Admin Pages</h2>
        <table>
            <tr>
                <th>#</th>
                <th>URL</th>
            </tr>"""
        
        for i, url in enumerate(self.results['admin_pages'], 1):
            html += f"""
            <tr class="admin">
                <td>{i}</td>
                <td><a href="{url}" target="_blank">{url}</a></td>
            </tr>"""
        
        html += """
        </table>
        
        <h2>📧 Emails</h2>
        <ul>"""
        
        for email in self.results['emails'][:20]:
            html += f"<li>{email}</li>"
        
        html += """
        </ul>
        
        <div class="footer">
            <p>Generated by JATHNIEL-WEB-CRAWLER-PRO v2.0</p>
            <p>Ethical Hacking Tool - For educational purposes only</p>
            <p>★ JATHNIEL ★</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def export_csv_report(self, filename):
        """Exporte un rapport CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Sensitive files
            writer.writerow(['SENSITIVE FILES'])
            writer.writerow(['File', 'Type', 'Size', 'URL'])
            for file in self.results['sensitive_files']:
                writer.writerow([file['filename'], file['type'], file['size'], file['url']])
            
            writer.writerow([])
            
            # Admin pages
            writer.writerow(['ADMIN PAGES'])
            writer.writerow(['URL'])
            for url in self.results['admin_pages']:
                writer.writerow([url])
            
            writer.writerow([])
            
            # Emails
            writer.writerow(['EMAILS'])
            writer.writerow(['Email'])
            for email in self.results['emails']:
                writer.writerow([email])
    
    def show_statistics(self):
        """Affiche les statistiques"""
        stats = self.results['statistics']
        
        print(self.colorize("\n📊 STATISTIQUES DU CRAWL", 'bold'))
        print(self.colorize("="*60, 'cyan'))
        
        print(f"\n📄 Pages decouvertes: {stats['total_pages']}")
        print(f"📦 Assets telecharges: {stats['total_assets']}")
        print(f"🔴 Fichiers sensibles: {stats['total_sensitive']}")
        print(f"📦 Taille totale: {self.format_size(stats['total_size'])}")
        print(f"⏱️  Duree: {stats['duration']:.2f} secondes")
        print(f"🚀 Vitesse moyenne: {stats['total_pages'] / stats['duration']:.2f} pages/sec")
    
    def format_size(self, bytes):
        """Formate la taille en unités lisibles"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} TB"
    
    # ==================== CONFIGURATION ====================
    
    def show_config(self):
        """Affiche la configuration"""
        print(self.colorize("\n⚙️ CONFIGURATION", 'bold'))
        print(self.colorize("="*60, 'cyan'))
        
        for key, value in self.config.items():
            print(f"  {key}: {self.colorize(str(value), 'green' if value else 'yellow')}")
        
        input(self.colorize("\nAppuyez sur Entree pour continuer...", 'blue'))
    
    def show_help(self):
        """Affiche l'aide"""
        help_text = f"""
{self.colorize('📚 WEB CRAWLER PRO - GUIDE D UTILISATION', 'bold')}
{self.colorize('='*60, 'cyan')}

{self.colorize('1. Crawl complet', 'green')}
   - Explore tout le site
   - Telecharge les pages, assets et fichiers sensibles
   - Analyse les technologies et emails

{self.colorize('2. Extraction de fichiers sensibles', 'green')}
   - Recherche automatique des fichiers sensibles
   - Telecharge les fichiers trouves
   - Classifie par type (config, DB, logs, etc.)

{self.colorize('3. Telechargement specifique', 'green')}
   - Telecharge un fichier specifique
   - Utile pour tester des URLs candidates

{self.colorize('4. Export des resultats', 'green')}
   - JSON: Donnees structurees
   - HTML: Rapport visuel
   - CSV: Analyse dans Excel

{self.colorize('⚠️ RAPPEL LEGAL', 'red')}
   - Utilisez UNIQUEMENT sur vos propres sites
   - Obtenez une autorisation écrite
   - Usage educatif et de securite uniquement
        """
        print(help_text)
    
    # ==================== MENU PRINCIPAL ====================
    
    def run(self):
        """Boucle principale"""
        while True:
            self.clear_screen()
            self.show_banner()
            self.show_menu()
            
            choice = input(self.colorize("\n👉 Votre choix: ", 'bold')).strip()
            
            if choice == '1':
                url = self.get_user_input("URL cible", "https://example.com")
                if url:
                    self.crawl_complete(url)
                input(self.colorize("\nAppuyez sur Entree pour continuer...", 'blue'))
            
            elif choice == '2':
                url = self.get_user_input("URL cible", "https://example.com")
                if url:
                    self.config['download_sensitive'] = True
                    self.crawl_complete(url)
                input(self.colorize("\nAppuyez sur Entree pour continuer...", 'blue'))
            
            elif choice == '3':
                self.download_specific_file()
            
            elif choice == '4':
                self.show_results()
                input(self.colorize("\nAppuyez sur Entree pour continuer...", 'blue'))
            
            elif choice == '5':
                self.show_sensitive_files()
                input(self.colorize("\nAppuyez sur Entree pour continuer...", 'blue'))
            
            elif choice == '6':
                self.export_results()
            
            elif choice == '7':
                self.show_config()
            
            elif choice == '8':
                self.show_statistics()
                input(self.colorize("\nAppuyez sur Entree pour continuer...", 'blue'))
            
            elif choice == '9':
                self.show_help()
                input(self.colorize("\nAppuyez sur Entree pour continuer...", 'blue'))
            
            elif choice == '0':
                print(self.colorize("\n👋 Au revoir!", 'green'))
                sys.exit(0)
            
            else:
                print(self.colorize("❌ Choix invalide", 'red'))
                time.sleep(1)

# ==================== MAIN ====================

if __name__ == "__main__":
    try:
        # Vérifier les dépendances
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            print("[!] Installation des dépendances...")
            os.system("pip3 install requests beautifulsoup4")
        
        crawler = JATHNIELCrawlerPro()
        crawler.run()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)