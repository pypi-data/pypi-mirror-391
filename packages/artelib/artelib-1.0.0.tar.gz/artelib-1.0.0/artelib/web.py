import re
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Callable, Any, List

#print("ArteLib WEB [WARNING] - ArteLib WEB is dont work on this verison!")

class Request:
    def __init__(self, handler: BaseHTTPRequestHandler):
        self.method = handler.command
        self.path = handler.path
        self.headers = dict(handler.headers)
        self.query_params = parse_qs(urlparse(self.path).query)
        
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            self.body = handler.rfile.read(content_length).decode('utf-8')
        else:
            self.body = ''
            
        try:
            self.json = json.loads(self.body) if self.body else {}
        except:
            self.json = {}

class Response:
    def __init__(self):
        self.status_code = 200
        self.headers = {'Content-Type': 'text/html'}
        self.body = b''
    
    def json(self, data: Dict) -> 'Response':
        """JSON Response"""
        self.headers['Content-Type'] = 'application/json'
        self.body = json.dumps(data).encode('utf-8')
        return self
    
    def text(self, text: str) -> 'Response':
        """Text Response"""
        self.headers['Content-Type'] = 'text/plain'
        self.body = text.encode('utf-8')
        return self
    
    def html(self, html: str) -> 'Response':
        """HTML Response"""
        self.headers['Content-Type'] = 'text/html'
        self.body = html.encode('utf-8')
        return self
    
    def render_template(self, template_path: str, context: Dict = None) -> 'Response':
        """Render HTML template"""
        self.headers['Content-Type'] = 'text/html'
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            if context:
                for key, value in context.items():
                    template_content = template_content.replace(f'{{{{ {key} }}}}', str(value))
            
            self.body = template_content.encode('utf-8')
        except FileNotFoundError:
            self.status(500).text(f'Template not found: {template_path}')
        except Exception as e:
            self.status(500).text(f'Template error: {str(e)}')
        
        return self
    
    def status(self, code: int) -> 'Response':
        """Status Code"""
        self.status_code = code
        return self

class Web:
    def __init__(self, name: str = __name__):
        self.name = name
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.before_request_handlers: List[Callable] = []
        self.after_request_handlers: List[Callable] = []
    
    def route(self, path: str, methods: List[str] = None):
        """
        Decorator to register url\n
        For example:\n
        app.route("/", ['GET'])
        def home():
            return response.html('<h1>Welcome to ArteLib!</h1><p>This is your home page.</p>')
        """
        if methods is None:
            methods = ['GET']
        
        def decorator(func: Callable):
            for method in methods:
                if method not in self.routes:
                    self.routes[method] = {}
                self.routes[method][path] = func
            return func
        return decorator
    
    def get(self, path: str):
        """Decorator to GET"""
        return self.route(path, methods=['GET'])
    
    def post(self, path: str):
        """Decorator to POST"""
        return self.route(path, methods=['POST'])
    
    def put(self, path: str):
        """Decorator to PUT"""
        return self.route(path, methods=['PUT'])
    
    def delete(self, path: str):
        """Decorator to DELETE"""
        return self.route(path, methods=['DELETE'])
    
    #def before_request(self, func: Callable):
     #   """Декоратор для функций, выполняемых перед каждым запросом"""
      #  self.before_request_handlers.append(func)
       # return func
    
    #def after_request(self, func: Callable):
     #   """Декоратор для функций, выполняемых после каждого запроса"""
      #  self.after_request_handlers.append(func)
       # return func
    
    def _find_route_handler(self, method: str, path: str):
        """Найти обработчик для маршрута с поддержкой динамических параметров"""
        if method not in self.routes:
            return None, {}
        
        if path in self.routes[method]:
            return self.routes[method][path], {}
        
        for route_pattern, handler in self.routes[method].items():
            if '<' in route_pattern and '>' in route_pattern:
                pattern = re.sub(r'<[^>]+>', r'([^/]+)', route_pattern)
                pattern = pattern.replace('/', r'\/')
                match = re.match(f'^{pattern}$', path)
                if match:
                    param_names = re.findall(r'<([^>]+)>', route_pattern)
                    param_values = match.groups()
                    params = dict(zip(param_names, param_values))
                    return handler, params
        
        return None, {}
    
    def run(self, host: str = 'localhost', port: int = 8000, debug: bool = False):
        """Запустить сервер"""
        app_instance = self
        
        class ArteLibHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.handle_request('GET')
            
            def do_POST(self):
                self.handle_request('POST')
            
            def do_PUT(self):
                self.handle_request('PUT')
            
            def do_DELETE(self):
                self.handle_request('DELETE')
            
            def handle_request(self, method: str):
                request = Request(self)
                response = Response()
                
                try:
                    for handler in app_instance.before_request_handlers:
                        handler(request, response)
                    
                    handler, params = app_instance._find_route_handler(method, request.path)
                    
                    if handler:
                        result = handler(request, response, **params)
                        
                        if result is not None:
                            if isinstance(result, Response):
                                response = result
                            elif isinstance(result, (dict, list)):
                                response.json(result)
                            else:
                                response.text(str(result))
                        else:
                            response.status(404).text('404 Not Found')
                    
                    for handler in app_instance.after_request_handlers:
                        handler(request, response)
                    
                except Exception as e:
                    if debug:
                        response.status(500).text(f'500 Internal Server Error: {str(e)}')
                    else:
                        response.status(500).text('500 Internal Server Error')
                
                self.send_response(response.status_code)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.body)
            
            def log_message(self, format, *args):
                if debug:
                    print(f"ArteLib WEB [INFO] - {format % args}")
        
        print(f"ArteLib WEB [INFO] - server running on http://{host}:{port}")
        server = HTTPServer((host, port), ArteLibHandler)
        server.serve_forever()