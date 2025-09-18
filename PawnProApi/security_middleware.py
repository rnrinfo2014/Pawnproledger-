"""
Security middleware for FastAPI application
Implements rate limiting, security headers, and request validation
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger("security")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Check if this is a docs endpoint
        is_docs_endpoint = any(path in str(request.url.path) for path in ["/docs", "/redoc", "/openapi.json"])
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Relax X-Frame-Options for docs to allow embedding
        if is_docs_endpoint:
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
        else:
            response.headers["X-Frame-Options"] = "DENY"
            
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HTTPS headers (only add if using HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy - Allow FastAPI docs to work
        if is_docs_endpoint:
            # Relaxed CSP for API documentation
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net https://unpkg.com; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
        else:
            # Strict CSP for API endpoints
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, app, max_requests: int = 100, time_window: int = 3600):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers (when behind a proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = time.time()
        client_requests = self.requests[client_ip]
        
        # Remove old requests outside the time window
        client_requests[:] = [req_time for req_time in client_requests 
                             if current_time - req_time < self.time_window]
        
        # Check if limit exceeded
        if len(client_requests) >= self.max_requests:
            security_logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return True
        
        # Add current request
        client_requests.append(current_time)
        return False
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        if self._is_rate_limited(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        return await call_next(request)


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Log security-relevant events"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        # Log authentication attempts
        if request.url.path == "/token":
            security_logger.info(f"Authentication attempt from IP: {client_ip}")
        
        # Log sensitive endpoint access
        sensitive_paths = ["/users", "/admin", "/delete", "/update"]
        if any(path in request.url.path for path in sensitive_paths):
            security_logger.info(f"Sensitive endpoint access: {request.method} {request.url.path} from IP: {client_ip}")
        
        response = await call_next(request)
        
        # Log failed authentication
        if request.url.path == "/token" and response.status_code == 401:
            security_logger.warning(f"Failed authentication attempt from IP: {client_ip}")
        
        # Log processing time for monitoring
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"