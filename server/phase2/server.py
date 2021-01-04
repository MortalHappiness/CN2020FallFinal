import os
import sys
import json
import uuid
from socket import *
import sqlite3
from urllib.parse import urlparse, parse_qs
import threading

# ========================================

BUFSIZE = 4096

# ========================================


class ClientThread(threading.Thread):
    def __init__(self, conn_sock, addr):
        super().__init__()
        self.conn_sock = conn_sock
        self.addr = addr

    def run(self):
        with self.conn_sock as conn_sock:
            print("Got connection from", self.addr)
            try:
                req = conn_sock.recv(BUFSIZE).decode()
                handle_request(conn_sock, sql_conn, req)
            except:
                abort(conn_sock, 400)


def abort(conn_sock, status, err_msg=None):
    descriptions = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
    }
    assert status in descriptions
    description = descriptions[status]
    if err_msg is None:
        media_type = "text/plain"
        body = description
    else:
        media_type = "application/json"
        body = json.dumps({"msg": err_msg})
    res = (
        f"HTTP/1.0 {status} {description}\r\n"
        f"Content-Type: {media_type}; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
        f"{body}"
    )
    conn_sock.sendall(res.encode())


def end(conn_sock, status, body="", option=None):
    descriptions = {
        200: "OK",
        201: "Created",
        204: "No Content",
    }
    assert status in descriptions
    assert type(body) == str
    description = descriptions[status]
    if body:
        content_type = "Content-Type: application/json; charset=utf-8\r\n"
    else:
        content_type = ""
    cookie = ""
    if option is not None:
        assert type(option) == tuple and len(option) == 2
        if option[0] == "set-session":
            cookie = f"Set-Cookie: session={option[1]}; HttpOnly; Path=/\r\n"
        elif option[0] == "delete-session":
            expires = "Thu, 01 Jan 1970 00:00:00 UTC"
            cookie = f"Set-Cookie: session=; Expires={expires}; Path=/\r\n"
        else:
            raise ValueError("Invalid option")
    res = (
        f"HTTP/1.0 {status} {description}\r\n"
        f"{content_type}"
        f"Content-Length: {len(body)}\r\n"
        f"{cookie}"
        f"\r\n"
        f"{body}"
    )
    conn_sock.sendall(res.encode())


def sendfile(conn_sock, filename):
    media_types = {
        ".html": "text/html",
        ".js": "text/javascript",
    }
    ext = os.path.splitext(filename)[1]
    assert ext in media_types
    media_type = media_types[ext]
    try:
        with open(filename, "rb") as fin:
            fin.seek(0, os.SEEK_END)
            filesize = fin.tell()
            fin.seek(0, os.SEEK_SET)
            res = (
                f"HTTP/1.0 200 OK\r\n"
                f"Content-Type: {media_type}; charset=utf-8\r\n"
                f"Content-Length: {filesize}\r\n"
                f"\r\n"
            )
            conn_sock.sendall(res.encode())
            conn_sock.sendfile(fin)
    except FileNotFoundError:
        abort(conn_sock, 404)


def parse_form_data(header, body):
    media_type = header.get("content-type", None)
    if media_type != "application/x-www-form-urlencoded":
        return
    return parse_qs(body)


def get_session_id(header):
    cookies = header.get("cookie", None)
    if cookies is not None:
        cookies = cookies.split(";")
        for cookie in cookies:
            if cookie.startswith("session"):
                return cookie[cookie.index("=")+1:]
    return None


def handle_routes(conn_sock, sql_conn, method, path, header, body):
    if method == "GET":
        parsed_url = urlparse(path)
        if path == "/" or path == "/index.html":
            sendfile(conn_sock, "build/index.html")
            return
        if path == "/bundle.js":
            sendfile(conn_sock, "build/bundle.js")
            return
        if path == "/api/users":
            cursor = sql_conn.execute(
                "SELECT username FROM accounts"
            )
            accounts = cursor.fetchall()
            users = [x[0] for x in accounts]
            end(conn_sock, 200, json.dumps(users))
            return
        if path == "/api/username":
            session_id = get_session_id(header)
            username = ""
            if session_id is not None:
                cursor = sql_conn.execute(
                    "SELECT username FROM sessions WHERE id=?",
                    (session_id,)
                )
                session = cursor.fetchone()
                if session is not None:
                    username = session[0]
            end(conn_sock, 200, json.dumps({"username": username}))
            return
        if parsed_url.path == "/api/messages":
            query = parse_qs(parsed_url.query)
            username = query.get("username", None)[0]
            if username is None or not username.isalnum():
                abort(conn_sock, 400)
                return
            cursor = sql_conn.execute(
                "SELECT * FROM accounts WHERE username=?",
                (username,)
            )
            account = cursor.fetchone()
            if account is None:
                abort(conn_sock, 404)
                return
            cursor = sql_conn.execute(
                "SELECT id, user_from, message FROM messages WHERE user_to=? "
                "ORDER BY id DESC",
                (username,)
            )
            messages = cursor.fetchall()
            messages = [dict(zip(("id", "user_from", "message"), message))
                        for message in messages]
            end(conn_sock, 200, json.dumps(messages))
            return
        abort(conn_sock, 404)
        return

    if method == "POST":
        if path == "/api/register":
            form_data = parse_form_data(header, body)
            if form_data is None:
                abort(conn_sock, 400)
                return
            if "username" not in form_data or "password" not in form_data:
                abort(conn_sock, 400)
                return
            username = form_data["username"][0]
            password = form_data["password"][0]
            if not username.isalnum() or not password.isalnum():
                abort(conn_sock, 400,
                      "Username and password must be alpha-numeric!")
                return
            cursor = sql_conn.execute(
                "SELECT * FROM accounts WHERE username=?",
                (username,)
            )
            account = cursor.fetchone()
            if account is not None:
                abort(conn_sock, 400, "The username has been registered!")
                return
            with sql_conn:
                sql_conn.execute(
                    "INSERT INTO accounts VALUES (?,?,?)",
                    (None, username, password)
                )
            end(conn_sock, 201, json.dumps({"username": username}))
            return
            end(conn_sock, 204)
        if path == "/api/login":
            form_data = parse_form_data(header, body)
            if form_data is None:
                abort(conn_sock, 400)
                return
            if "username" not in form_data or "password" not in form_data:
                abort(conn_sock, 400)
                return
            username = form_data["username"][0]
            password = form_data["password"][0]
            if not username.isalnum() or not password.isalnum():
                abort(conn_sock, 400,
                      "Username and password must be alpha-numeric!")
                return
            cursor = sql_conn.execute(
                "SELECT * FROM accounts WHERE username=? AND password=?",
                (username, password)
            )
            account = cursor.fetchone()
            if account is None:
                abort(conn_sock, 401, "Invalid username or password!")
                return
            session_id = uuid.uuid4().hex
            with sql_conn:
                sql_conn.execute(
                    "DELETE FROM sessions WHERE username=?",
                    (username,)
                )
            with sql_conn:
                sql_conn.execute(
                    "INSERT INTO sessions VALUES (?,?)",
                    (session_id, username)
                )
            end(conn_sock, 201, json.dumps({"username": username}),
                option=("set-session", session_id)
                )
            return
        if path == "/api/logout":
            session_id = get_session_id(header)
            if session_id is not None:
                with sql_conn:
                    sql_conn.execute(
                        "DELETE FROM sessions WHERE id=?",
                        (session_id,)
                    )
            end(conn_sock, 204, option=("delete-session", None))
            return
        if path == "/api/send-message":
            session_id = get_session_id(header)
            if session_id is None:
                abort(conn_sock, 403, "Login first to send message!")
                return
            cursor = sql_conn.execute(
                "SELECT username FROM sessions WHERE id=?",
                (session_id,)
            )
            session = cursor.fetchone()
            if session is None:
                abort(conn_sock, 403, "Login first to send message!")
                return
            user_from = session[0]
            form_data = parse_form_data(header, body)
            if form_data is None:
                abort(conn_sock, 400, "No form body is found!")
                return
            if "user-to" not in form_data or "message" not in form_data:
                abort(conn_sock, 400, "Please specify user-to and message")
                return
            user_to = form_data["user-to"][0]
            message = form_data["message"][0]
            if user_from == user_to:
                abort(conn_sock, 400, "You cannot send message to yourself!")
                return
            cursor = sql_conn.execute(
                "SELECT * FROM accounts WHERE username=?",
                (user_to,)
            )
            account = cursor.fetchone()
            if account is None:
                abort(conn_sock, 400, "The user does not exist!")
                return
            with sql_conn:
                cursor = sql_conn.execute(
                    "INSERT INTO messages VALUES (?,?,?,?)",
                    (None, user_from, user_to, message)
                )
                end(conn_sock, 201,
                    json.dumps({"id": cursor.lastrowid,
                                "user_from": user_from,
                                "message": message})
                    )
                return
        abort(conn_sock, 400)
        return

    abort(conn_sock, 400)


def handle_request(conn_sock, sql_conn, req):
    lines = req.split("\r\n")
    tokens = lines[0].split()
    if len(tokens) != 3:
        abort(conn_sock, 400)
        return
    method, path, version = tokens
    if method not in ["GET", "POST"]:
        abort(conn_sock, 400)
        return
    if "" not in lines:
        abort(conn_sock, 400)
        return
    split_idx = lines.index("")
    header = dict()
    body = "".join(lines[split_idx:])
    for line in lines[1:split_idx]:
        try:
            k, v = line.split(":", 1)
            header[k.strip().lower()] = v.strip()
        except ValueError:
            abort(conn_sock, 400)
            return
    handle_routes(conn_sock, sql_conn, method, path, header, body)


def main(port, sql_conn):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind(("", port))
        s.listen(1)
        print("Server listening at port", port)
        while True:
            conn_sock, addr = s.accept()
            new_thread = ClientThread(conn_sock, addr)
            new_thread.start()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python %s [port] [db_path]" % sys.argv[0])
        sys.exit(1)
    try:
        port = int(sys.argv[1])
        if port < 1 or port > 65535:
            raise ValueError
    except ValueError:
        print("Invalid port number:", sys.argv[1])
        sys.exit(1)
    db_path = sys.argv[2]
    if not os.path.exists(db_path):
        print(f"The database file '{db_path}' does not exists")
        sys.exit(1)

    sql_conn = sqlite3.connect(db_path)
    try:
        main(port, sql_conn)
    finally:
        sql_conn.close()
