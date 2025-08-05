"""
Proxy configuration for traffic generator
Add your own proxy lists here
"""

# Free proxy list (often unreliable, use for testing)
FREE_PROXIES = [
    {'server': '8.210.83.33', 'port': 80},
    {'server': '47.74.152.29', 'port': 8888},
    {'server': '43.134.68.153', 'port': 3128},
    {'server': '103.149.162.194', 'port': 80},
    {'server': '185.199.84.161', 'port': 53281},
    {'server': '91.107.197.9', 'port': 80},
    {'server': '188.163.170.130', 'port': 41209},
    {'server': '103.216.207.15', 'port': 8080},
    {'server': '182.253.158.52', 'port': 3128},
    {'server': '139.255.25.84', 'port': 3128}
]

# Premium proxy list (replace with your paid proxies)
PREMIUM_PROXIES = [
    {'server': 'premium-proxy1.example.com', 'port': 8080, 'username': 'user1', 'password': 'pass1'},
    {'server': 'premium-proxy2.example.com', 'port': 8080, 'username': 'user2', 'password': 'pass2'},
    {'server': 'premium-proxy3.example.com', 'port': 8080, 'username': 'user3', 'password': 'pass3'},
    {'server': 'premium-proxy4.example.com', 'port': 8080, 'username': 'user4', 'password': 'pass4'},
    {'server': 'premium-proxy5.example.com', 'port': 8080, 'username': 'user5', 'password': 'pass5'}
]

# Datacenter proxy list (high-speed, replace with your datacenter proxies)
DATACENTER_PROXIES = [
    {'server': 'dc-proxy1.example.com', 'port': 3128, 'username': 'dc_user1', 'password': 'dc_pass1'},
    {'server': 'dc-proxy2.example.com', 'port': 3128, 'username': 'dc_user2', 'password': 'dc_pass2'},
    {'server': 'dc-proxy3.example.com', 'port': 3128, 'username': 'dc_user3', 'password': 'dc_pass3'},
    {'server': 'dc-proxy4.example.com', 'port': 3128, 'username': 'dc_user4', 'password': 'dc_pass4'},
    {'server': 'dc-proxy5.example.com', 'port': 3128, 'username': 'dc_user5', 'password': 'dc_pass5'}
]

def get_proxies(proxy_type='free'):
    """
    Get proxy list based on type
    
    Args:
        proxy_type (str): 'free', 'premium', or 'datacenter'
    
    Returns:
        list: List of proxy dictionaries
    """
    if proxy_type == 'free':
        return FREE_PROXIES.copy()
    elif proxy_type == 'premium':
        return PREMIUM_PROXIES.copy()
    elif proxy_type == 'datacenter':
        return DATACENTER_PROXIES.copy()
    else:
        return FREE_PROXIES.copy()

def validate_proxy(proxy):
    """
    Validate proxy configuration
    
    Args:
        proxy (dict): Proxy configuration
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['server', 'port']
    return all(field in proxy for field in required_fields)

def get_working_proxies(proxy_type='free', max_concurrent_tests=10):
    """
    Test proxies and return only working ones
    Note: This is a placeholder - implement actual proxy testing
    
    Args:
        proxy_type (str): Type of proxies to test
        max_concurrent_tests (int): Maximum concurrent tests
    
    Returns:
        list: List of working proxies
    """
    proxies = get_proxies(proxy_type)
    # TODO: Implement actual proxy testing logic
    # For now, return all proxies (you should implement testing)
    return [proxy for proxy in proxies if validate_proxy(proxy)]

# Example usage
if __name__ == '__main__':
    print("Free proxies:", len(get_proxies('free')))
    print("Premium proxies:", len(get_proxies('premium')))
    print("Datacenter proxies:", len(get_proxies('datacenter')))
    
    # Test proxy validation
    test_proxy = {'server': '127.0.0.1', 'port': 8080}
    print("Test proxy valid:", validate_proxy(test_proxy))
