import io
import uuid
from fileinput import filename
from http.server import HTTPServer, BaseHTTPRequestHandler
from loguru import logger
from typing import Any
from PIL import Image

SERVER_ADDRESS = ('localhost', 8000)
ALLOWED_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif')
ALLOWED_LENGTH = (5 * 1024 * 1024)

logger.add('logs/app.log', format="[{time: YYYY-MM-DD HH:mm:ss}] | {level} | {message}")

class ImageHostingHandler(BaseHTTPRequestHandler):
    server_version = 'Image Hosting Server/0.1'
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            logger.info(f'GET {self.path}')
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(open('index.html', 'rb').read())
        else:
            logger.warning(f'GET 404 {self.path}')
            self.send_response(404, 'Not Found')

    def do_POST(self):
        if self.path == '/upload':
            logger.info(f'POST {self.path}')
            content_length = int(self.headers.get('Content-Length'))
            if content_length > ALLOWED_LENGTH:
                logger.error('Payload Too large')
                self.send_response(413, 'Payload Too large')
                return

            filename = self.headers.get("Filename")

            if not filename:
                logger.error("Lack of Filename header")
                self.send_response(400, 'Lack of Filename header')
                return
            filename, ext = filename.split('.')
            if ext not in ALLOWED_EXTENSIONS:
                logger.error('Unsupported file extension')
                self.send_response(400, 'Unsupported file extension')
                return

            data = self.rfile.read(content_length)
            image_id = uuid.uuid4()

            with open(f'images/{image_id}.{ext}', 'wb') as f:
                f.write(data)
            logger.info(f'Upload success: {image_id}.{ext}')
            self.send_response(201)
            self.send_header('Location', f'http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}/images/{filename}.{ext}')
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(open('upload_success.html', 'rb').read())
        else:
            self.send_response(405, 'Method Not Allowed')


def run():
    httpd = HTTPServer(SERVER_ADDRESS, ImageHostingHandler)
    try:
        logger.info(f'Serving at http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}')
        httpd.serve_forever()
    except Exception:
        pass
    finally:
        logger.info('Server stopped')
        httpd.server_close()


if __name__ == "__main__":
    run()