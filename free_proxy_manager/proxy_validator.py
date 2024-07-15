import socket
import logging

from .config import PROXY_VALIDATION_TIMEOUT, CDN_EDGE_SERVER, CDN_EDGE_PORT

log = logging.getLogger(__name__)

class ProxyValidator:

    @staticmethod
    def format_proxy_as_str(proxy):
        if not isinstance(proxy, dict):
            raise TypeError("`proxy` must be a dict")
        return f"{proxy['ip']}:{proxy['port']}"

    @staticmethod
    def format_proxy_as_dict(proxy_str):
        if not isinstance(proxy_str, str):
            raise TypeError("`proxy_str` must be a string")
        ip, port = proxy_str.split(":")
        return {'ip': ip, 'port': port}

    @staticmethod
    def check_proxy(proxy, timeout=PROXY_VALIDATION_TIMEOUT):
        # Convert the proxy dictionary to a string in the format "ip:port"
        proxy_str = ProxyValidator.format_proxy_as_str(proxy)
        
        try:
            log.debug(f"Testing proxy: {proxy_str}")
            
            # Extract the IP and port from the proxy dictionary
            proxy_ip, proxy_port = proxy['ip'], int(proxy['port'])
            
            # Create a socket connection to the proxy IP and port with a specified timeout
            sock = socket.create_connection((proxy_ip, proxy_port), timeout)
            
            # Set the timeout for the socket
            sock.settimeout(timeout)
            
            # Send a CONNECT request to the CDN edge server through the proxy
            sock.sendall(f"CONNECT {CDN_EDGE_SERVER}:{CDN_EDGE_PORT} HTTP/1.1\r\n\r\n".encode())
            
            # Receive the response from the proxy
            response = sock.recv(4096).decode()
            
            # Close the socket connection
            sock.close()

            # Check if the response indicates a successful connection establishment
            if "200 Connection established" in response:
                log.debug(f"Proxy: {proxy_str} is valid (response: {response.strip()})")
                return True
            else:
                # Raise an error if the response is not as expected
                raise socket.error("Invalid proxy response")

        except Exception as e:
            # Log the exception and return False indicating the proxy is invalid
            log.debug(f"Proxy: {proxy_str} is invalid - Exception: {e.__class__.__name__}: {str(e)}")
            return False