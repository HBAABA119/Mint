"""
Prim Web Framework
Provides routing, middleware, request/response handling, and template engine.
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HTTPStatus(Enum):
    """HTTP status codes"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500


@dataclass
class Request:
    """HTTP request"""
    method: HTTPMethod
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    path_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class Response:
    """HTTP response"""
    status: HTTPStatus = HTTPStatus.OK
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None

    def json(self, data: Any) -> 'Response':
        """Set JSON body"""
        self.body = json.dumps(data)
        self.headers['Content-Type'] = 'application/json'
        return self

    def text(self, text: str) -> 'Response':
        """Set text body"""
        self.body = text
        self.headers['Content-Type'] = 'text/plain'
        return self

    def html(self, html: str) -> 'Response':
        """Set HTML body"""
        self.body = html
        self.headers['Content-Type'] = 'text/html'
        return self


class Route:
    """Route definition"""

    def __init__(self, method: HTTPMethod, path: str, handler: Callable):
        self.method = method
        self.path = path
        self.handler = handler
        self.path_parts = self._parse_path(path)

    def _parse_path(self, path: str) -> List[str]:
        """Parse path into parts"""
        return [part for part in path.split('/') if part]

    def match(self, method: HTTPMethod, path: str) -> Optional[Dict[str, str]]:
        """Check if route matches"""
        if self.method != method:
            return None

        path_parts = [part for part in path.split('/') if part]

        if len(path_parts) != len(self.path_parts):
            return None

        params = {}
        for route_part, path_part in zip(self.path_parts, path_parts):
            if route_part.startswith(':'):
                params[route_part[1:]] = path_part
            elif route_part != path_part:
                return None

        return params


class Router:
    """Router for handling routes"""

    def __init__(self):
        self.routes: List[Route] = []
        self.middleware: List[Callable] = []

    def get(self, path: str) -> Callable:
        """Register GET route"""
        def decorator(handler: Callable) -> Callable:
            self.routes.append(Route(HTTPMethod.GET, path, handler))
            return handler
        return decorator

    def post(self, path: str) -> Callable:
        """Register POST route"""
        def decorator(handler: Callable) -> Callable:
            self.routes.append(Route(HTTPMethod.POST, path, handler))
            return handler
        return decorator

    def put(self, path: str) -> Callable:
        """Register PUT route"""
        def decorator(handler: Callable) -> Callable:
            self.routes.append(Route(HTTPMethod.PUT, path, handler))
            return handler
        return decorator

    def delete(self, path: str) -> Callable:
        """Register DELETE route"""
        def decorator(handler: Callable) -> Callable:
            self.routes.append(Route(HTTPMethod.DELETE, path, handler))
            return handler
        return decorator

    def patch(self, path: str) -> Callable:
        """Register PATCH route"""
        def decorator(handler: Callable) -> Callable:
            self.routes.append(Route(HTTPMethod.PATCH, path, handler))
            return handler
        return decorator

    def use(self, middleware: Callable):
        """Add middleware"""
        self.middleware.append(middleware)

    def match(self, request: Request) -> Optional[Route]:
        """Find matching route"""
        for route in self.routes:
            params = route.match(request.method, request.path)
            if params is not None:
                request.path_params = params
                return route
        return None


class Middleware:
    """Middleware base class"""

    def __init__(self, app: 'Application'):
        self.app = app

    def process_request(self, request: Request) -> Optional[Response]:
        """Process request before route handler"""
        return None

    def process_response(self, request: Request, response: Response) -> Response:
        """Process response after route handler"""
        return response


class CORS(Middleware):
    """CORS middleware"""

    def __init__(self, app: 'Application', origins: List[str] = ['*']):
        super().__init__(app)
        self.origins = origins

    def process_response(self, request: Request, response: Response) -> Response:
        """Add CORS headers"""
        response.headers['Access-Control-Allow-Origin'] = ','.join(self.origins)
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response


class Logging(Middleware):
    """Logging middleware"""

    def process_request(self, request: Request) -> Optional[Response]:
        """Log request"""
        print(f"{request.method.value} {request.path}")
        return None


class Application:
    """Web application"""

    def __init__(self):
        self.router = Router()
        self.middleware: List[Middleware] = []

    def route(self, method: HTTPMethod, path: str) -> Callable:
        """Register a route"""
        if method == HTTPMethod.GET:
            return self.router.get(path)
        elif method == HTTPMethod.POST:
            return self.router.post(path)
        elif method == HTTPMethod.PUT:
            return self.router.put(path)
        elif method == HTTPMethod.DELETE:
            return self.router.delete(path)
        elif method == HTTPMethod.PATCH:
            return self.router.patch(path)

    def use(self, middleware: Union[Middleware, Callable]):
        """Add middleware"""
        if isinstance(middleware, Middleware):
            self.middleware.append(middleware)
        else:
            self.middleware.append(middleware)

    def handle(self, request: Request) -> Response:
        """Handle a request"""
        # Apply request middleware
        for middleware in self.middleware:
            if isinstance(middleware, Middleware):
                response = middleware.process_request(request)
                if response:
                    return response

        # Match route
        route = self.router.match(request)

        if not route:
            return Response(status=HTTPStatus.NOT_FOUND).text("Not Found")

        # Call handler
        try:
            result = route.handler(request)
            if isinstance(result, Response):
                response = result
            else:
                response = Response().json(result)
        except Exception as e:
            response = Response(status=HTTPStatus.INTERNAL_SERVER_ERROR).text(str(e))

        # Apply response middleware
        for middleware in self.middleware:
            if isinstance(middleware, Middleware):
                response = middleware.process_response(request, response)

        return response

    def run(self, host: str = "localhost", port: int = 8000):
        """Run the application"""
        print(f"Running on http://{host}:{port}")
        # In a real implementation, this would start a web server
        print("Server started (simulated)")


class TemplateEngine:
    """Template engine for rendering templates"""

    def __init__(self):
        self.templates: Dict[str, str] = {}

    def load_template(self, name: str, template: str):
        """Load a template"""
        self.templates[name] = template

    def render(self, name: str, context: Dict[str, Any] = None) -> str:
        """Render a template"""
        template = self.templates.get(name, "")
        if not template:
            return ""

        context = context or {}

        # Simple template rendering
        result = template
        for key, value in context.items():
            result = result.replace(f"{{{{ {key} }}}}", str(value))

        return result


def create_app() -> Application:
    """Create a new application"""
    return Application()


def main():
    """Main entry point for testing"""
    # Create app
    app = create_app()

    # Add middleware
    app.use(Logging(app))
    app.use(CORS(app))

    # Define routes
    @app.route(HTTPMethod.GET, "/")
    def index(request: Request) -> Response:
        return Response().html("<h1>Hello World</h1>")

    @app.route(HTTPMethod.GET, "/hello/:name")
    def hello(request: Request) -> Response:
        name = request.path_params.get('name', 'World')
        return Response().text(f"Hello, {name}!")

    @app.route(HTTPMethod.POST, "/api/data")
    def create_data(request: Request) -> Response:
        return Response().json({"message": "Created"}).json({"id": 1})

    # Test request handling
    request = Request(method=HTTPMethod.GET, path="/")
    response = app.handle(request)
    print(f"Response: {response.status.value} - {response.body}")

    print("\nWeb framework initialized successfully")


if __name__ == "__main__":
    main()
