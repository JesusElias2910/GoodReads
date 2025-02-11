from functools import cached_property
from http.cookies import SimpleCookie
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
import redis

# Código basado en:
# https://realpython.com/python-http-server/
# https://docs.python.org/3/library/http.server.html
# https://docs.python.org/3/library/http.cookies.html

r = redis.StrictRedis(host="localhost", port = 6379, db = 0)


mappings = [
    (r"^/books/(?P<book_id>\d+)$","get_book"),
    (r"^/book/(?P<book_id>\d+)$","get_book"),
    (r"^/$","index"),
           ]

class WebRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.url_mapping_response()

    def get_params(self, pattern, path):
        match = re.match(pattern, path)
        if match:
            return match.groupdict()
    
    def get_book(self, book_id):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        # book_info = f"<h1> Info del libro {book_id} es correcto </h1>".encode("utf-8")
        book_info = r.get(f"book:{book_id}") or "No existe".encode("utf-8")
        self.wfile.write(book_info)
    
    def url_mapping_response(self):
        for (pattern, method) in mappings:
            match = self.get_params(pattern,self.path)
            print(match)
            if match is not None:
                md = getattr(self,method)
                md(**match)
                return
        self.send_response(404)
        self.end_headers()
        self.wfile.write("Not found".encode("utf-8"))
        
    def index(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        index_page = "<h1> Bienvenidos a los libros </h1>".encode("utf-8")
        self.wfile.write(index_page)

    def get_response(self):
        return f"""
    <h1> Hola Web </h1>
    <p>  {self.path}         </p>
    <p>  {self.headers}      </p> 
    
    """


if __name__ == "__main__":
    print("Server starting...")
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()
