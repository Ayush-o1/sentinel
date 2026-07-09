"""
SENTINEL — Rate Limiter Instance

Centralized slowapi limiter used across all rate-limited endpoints.
Imported here to ensure a single shared instance across the application.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limit by IP address for unauthenticated endpoints (login, register)
# In authenticated routes, we layer user-id keying on top of this
limiter = Limiter(key_func=get_remote_address)
