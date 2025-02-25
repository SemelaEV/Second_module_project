import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
SERVER_ADDRESS = ('localhost', 8000)


class ImageHostingHandler(BaseHTTPRequestHandler):
    server_version = 'Image Hosting Server/0.1'
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(open('index.html', 'rb').read())
        else:
            self.send_response(404, 'Not Found')

    def do_POST(self):
        if self.path == '/upload':
            content_length = int(self.headers.get('Content-Length'))
            data = self.rfile.read(content_length)
            image_id = uuid.uuid4()
            with open(f'images/{image_id}.jpg', 'wb') as f:
                f.write(data)
            self.send_response(201)
            self.send_header('Location', f'http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}/images/{image_id}.jpg')
            self.end_headers()
        else:
            self.send_response(405, 'Method Not Allowed')


def run():
    httpd = HTTPServer(SERVER_ADDRESS, ImageHostingHandler)
    try:
        print(f'Serving at http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}')
        httpd.serve_forever()
    except Exception:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run()