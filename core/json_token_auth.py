import traceback

from channels.auth import AuthMiddleware
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.sessions import CookieMiddleware, SessionMiddleware
from django.db import close_old_connections
from rest_framework_simplejwt.authentication import JWTAuthentication


class JsonTokenAuthMiddleware(BaseMiddleware):
    """
    Token authorization middleware for Django Channels 2
    """

    async def __call__(self, scope, receive, send):
        try:
            # Close old database connections to prevent usage of timed out connections
            close_old_connections()
            # Extract the token key from the Authorization header
            token = dict(scope["headers"]).get(b"authorization", None)
            if not token:
                query_string = scope.get("query_string")
                if b"authorization" in query_string:
                    token = query_string

            try:
                token = token.decode("utf8").split(" ")[1]
            except IndexError:
                token = token.decode("utf8").split("%20")[1]

            # Verify and authenticate the user using the JWT token
            scope["user"] = await self.get_user_from_token(token)
        except (AttributeError, IndexError):
            pass
        except Exception:
            print(traceback.format_exc())
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        jwt_authentication = JWTAuthentication()
        validated_token = jwt_authentication.get_validated_token(token)
        return jwt_authentication.get_user(validated_token)


def JsonTokenAuthMiddlewareStack(inner):
    return JsonTokenAuthMiddleware(CookieMiddleware(SessionMiddleware(AuthMiddleware(inner))))
