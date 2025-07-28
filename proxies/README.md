# Proxy Configuration

This directory contains proxy lists for enhanced anonymity and rate limit bypassing.

## Setup Instructions

1. Copy `proxies.txt.example` to `proxies.txt`
2. Add your proxy servers to `proxies.txt`
3. The tool will automatically test and validate proxies

## Supported Formats

### Format 1: IP:Port
```
127.0.0.1:8080
192.168.1.100:3128
```

### Format 2: IP:Port:Username:Password
```
127.0.0.1:8080:username:password
192.168.1.100:3128:user:pass
```

### Format 3: HTTP URL
```
http://127.0.0.1:8080
http://username:password@127.0.0.1:8080
```

## Proxy Types Supported

- **HTTP Proxies** - Most common, good for Discord API
- **HTTPS Proxies** - Secure, recommended for sensitive operations
- **SOCKS5 Proxies** - Advanced, highest anonymity

## Recommendations

### Free Proxies
- Use with caution - often unstable
- Test thoroughly before use
- Expect higher failure rates

### Premium Proxies
- More reliable and faster
- Better for high-volume monitoring
- Residential IPs preferred over datacenter

### Proxy Services
- Rotating proxy services work well
- Consider services like ProxyMesh, Bright Data
- Ensure they support HTTPS endpoints

## Configuration Options

The tool provides these proxy options:
- **Test Before Use** - Validates connectivity (recommended)
- **Rotation Mode** - Cycles through working proxies
- **Failure Handling** - Removes or retries failed proxies
- **Timeout Settings** - Adjustable connection timeouts

## Security Notes

- Proxies can see your traffic
- Use trusted proxy providers only
- Consider using VPN + Proxy for maximum anonymity
- Avoid free proxies for sensitive operations
