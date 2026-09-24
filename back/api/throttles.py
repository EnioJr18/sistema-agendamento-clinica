from rest_framework.throttling import SimpleRateThrottle


class FixedScopeThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        ident = request.user.pk if request.user and request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class TokenThrottle(FixedScopeThrottle):
    scope = 'token'


class PublicRegistrationThrottle(FixedScopeThrottle):
    scope = 'public_registration'


class PasswordChangeThrottle(FixedScopeThrottle):
    scope = 'password_change'


class PresenceConfirmationThrottle(FixedScopeThrottle):
    scope = 'presence_confirmation'
