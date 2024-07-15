CDN_EDGE_SERVER = '1.1.1.1'  # Cloudflare's public DNS server
CDN_EDGE_PORT = 80           # HTTP port

PROXY_VALIDATION_URL = "8.8.8.8"  # Google's public DNS server - NOT USED
PROXY_VALIDATION_TIMEOUT = 5
MAX_WORKERS = 10

# URLS for proxy sources
FREE_PROXY_LIST_URL = "https://free-proxy-list.net"
SPEEDX_PROXY_LIST_URL = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
PROXY_SCRAPE_URL = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"

