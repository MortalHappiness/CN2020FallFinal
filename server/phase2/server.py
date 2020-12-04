import os
import sys
from socket import *

# ========================================

BUFSIZE = 4096

# ========================================


def abort(conn, status):
    msgs = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
    }
    assert status in msgs
    msg = msgs[status]
    res = (
        f"HTTP/1.0 {status} {msg}\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(msg)}\r\n"
        f"\r\n"
        f"{msg}"
    )
    conn.sendall(res.encode())


def sendfile(conn, filename):
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
            conn.sendall(res.encode())
            conn.sendfile(fin)
    except FileNotFoundError:
        abort(conn, 404)


def handle_routes(conn, method, path, header, body):
    if method == b"GET":
        if path == b"/" or path == b"/index.html":
            sendfile(conn, "build/index.html")
            return
        if path == b"/bundle.js":
            sendfile(conn, "build/bundle.js")
            return
        abort(conn, 404)
        return
    abort(conn, 400)


def handle_request(conn, req):
    lines = req.split(b"\r\n")
    tokens = lines[0].split()
    if len(tokens) != 3:
        abort(conn, 400)
        return
    method, path, version = tokens
    if method not in [b"GET", b"POST"]:
        abort(conn, 400)
        return
    if b"" not in lines:
        abort(conn, 400)
        return
    split_idx = lines.index(b"")
    header = dict()
    body = b"".join(lines[split_idx:])
    for line in lines[1:split_idx]:
        try:
            k, v = line.split(b":", 1)
            header[k.strip()] = v.strip()
        except ValueError:
            abort(conn, 400)
            return
    handle_routes(conn, method, path, header, body)


def main(port):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind(("", port))
        s.listen(1)
        print("Server listening at port", port)
        while True:
            conn, addr = s.accept()
            with conn:
                print("Got connection from", addr)
                req = conn.recv(BUFSIZE)
                handle_request(conn, req)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python %s [port]" % sys.argv[0])
        sys.exit(1)
    try:
        port = int(sys.argv[1])
        if port < 1 or port > 65535:
            raise ValueError
    except ValueError:
        print("Invalid port number:", sys.argv[1])
        sys.exit(1)

    main(port)
