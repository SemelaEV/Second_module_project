import hashlib
import io
import uuid
import cgi
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from os import listdir
from os.path import isfile, join
from PIL import Image
from loguru import logger

import psycopg2
from environs import Env
from urllib.parse import parse_qs


SERVER_ADDRESS = ('0.0.0.0', 8000)
ALLOWED_EXTENSIONS = ('.jpg', 'с', '.png', '.gif')
ALLOWED_LENGTH = (5 * 1024 * 1024)
UPLOAD_DIR = 'images'

logger.add('logs/app.log', format="[{time: YYYY-MM-DD HH:mm:ss}] | {level} | {message}")

class DBManager(metaclass=SingletonMeta):
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname, user=self.user, password=self.password, host=self.host, port=self.port)
            return self.conn
        except psycopg2.Error as e:
            logger.error(f"DB connection error: {e}")

    def close(self):
        self.conn.close()

    def execute(self, query):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
        except psycopg2.Error as e:
            logger.error(f"Error executing query: {e}")

    def execute_file(self, filename):
        try:
            self.execute(open(f'./{filename}').read())
        except FileNotFoundError:
            logger.error(f"File {filename} not found")

    def init_tables(self):
        self.execute_file('init_tables.sql')
        logger.info("Table initialized")
        self.conn.commit()

    def get_images(self, page=1, limit=10):
        offset = (page - 1) * limit
        logger.info(f'Try to get images with offset {offset}')
        with self.connect().cursor() as cursor:
            cursor.execute(
                "SELECT * FROM images ORDER BY upload_time DESC LIMIT %s OFFSET %s", (limit, offset))
            return cursor.fetchall()

    def add_image(self, filename, original_filename, size, ext):
        logger.info(f"Try to add image {filename}")
        with self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO images (filename, original_name, size, file_type) VALUES (%s, %s, %s, %s)",
                           (filename, original_filename, size, ext))
            self.conn.commit()

    def clear_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM images")
        self.conn.commit()

    def delete_image(self, filename):
        logger.info(f"Try to delete image {filename}")
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM images WHERE filename = %s", (filename))
            self.conn.commit()
        except psycopg2.Error as e:
            logger.error(f"Error deleting image {e}")


class ImageHostingHandler(BaseHTTPRequestHandler):
    server_version = 'Image Hosting Server/0.1'

    def __init__(self, request, client_address, server):
        self.get_routes = {
            '/upload': self.get_upload,
            '/images': self.get_images,
        }
        self.post_routes = {
            '/upload': self.post_upload,
        }
        self.db = DBManager()
        super().__init__(request, client_address, server)


    def do_GET(self):
        if self.path in self.get_routes:
            self.get_routes[self.path]()
        else:
            logger.warning(f'GET 404 {self.path}')
            self.send_response(404, 'Not Found')


    def do_POST(self):
        if self.path in self.post_routes:
            self.post_routes[self.path]()
        else:
            logger.warning(f'POST 404 {self.path}')
            self.send_response(405, 'Method Not Allowed')

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def get_images(self, limit):
        logger.info(f'GET {self.path}')

        query_components = parse_qs(self.headers.get('Query-String'))
        page = int(query_components.get('page', ['1'])[0])

        if page < 1:
            page = 1

        images = self.db.get_images(page, limit)

        images_json = []

        for image in images:
            image = {
                'filename': image[1],
                'original_filename': image[2],
                'size': image[3],
                'upload_date': image[4].strftime('%Y-%m-%d %H:%M:%s'),
                'file_type': image[5]
            }

            images_json.append(image)

        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

        self.wfile.write(json.dumps({'images': images_json}).encode('utf-8'))

    def get_upload(self):
        logger.info(f'GET {self.path}')
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(open('upload.html', 'rb').read())

    def post_upload(self):
        logger.info(f'POST {self.path}')
        content_length = int(self.headers.get('Content-Length'))

        original_filename, ext = os.path.splitext(self.headers.get('Filename'))

        filedata = self.rfile.read(content_length)
        image_raw_data = io.BytesIO(filedata)

        filename = hashlib.file_digest(image_raw_data, 'md5').hexdigest()
        file_size_kb = round(content_length / 1024)

        self.db.add_image(filename, original_filename, file_size_kb, ext)

        if content_length > ALLOWED_LENGTH:
            logger.error('Payload Too large')
            self.send_response(413, 'Payload Too large')
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )

        data = form['image'].file

        _, ext = os.path.splitext(form['image'].filename)

        if ext not in ALLOWED_EXTENSIONS:
            logger.error("File type not allowed")
            self.send_response(400, 'File type not allowed')
            return

        image_id = uuid.uuid4()
        image_name = f'{image_id}{ext}'
        with open(f'{UPLOAD_DIR}/{image_name}', 'wb') as f:
            f.write(data.read())

        try:
            im = Image.open(f'{UPLOAD_DIR}/{image_name}')
            im.verify()
        except (IOError, SyntaxError) as e:
            logger.error(f'Invalid file: {e}')
            self.send_response(400, 'Invalid file')
            return

        logger.info(f'Upload success: {image_name}')
        self.send_response(301)
        self.send_header('Location', f'/images/{image_name}')
        self.end_headers()


def run():
    httpd = HTTPServer(SERVER_ADDRESS, ImageHostingHandler)

    env = Env()
    env.read_env()

    db_name = env('POSTGRES_DB')
    db_username = env('POSTGRES_USER')
    db_password = env('POSTGRES_PASSWORD')
    db_host = env('POSTGRES_HOST')
    db_port = env('POSTGRES_PORT')

    db = DBManager(env('POSTGRES_DB'),
                   env('POSTGRES_USER'),
                   env('POSTGRES_PASSWORD'),
                   env('POSTGRES_HOST'),
                   env('POSTGRES_PORT'))

    db.init_tables()

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