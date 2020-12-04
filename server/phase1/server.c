#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BUFSIZE 8192
#define BACKLOG 10 // how many pending connections queue will hold

#define ERR_EXIT(a) \
    do {            \
        perror(a);  \
        exit(1);    \
    } while (0)

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s [port]\n", argv[0]);
        return 1;
    }
    int port = atoi(argv[1]);
    if (port < 1 || port > 65535) {
        fprintf(stderr, "Invalid port number: %d\n", port);
        return 1;
    }
    printf("Server listening at port %d\n", port);

    int listen_fd, conn_fd;
    struct sockaddr_in server_addr;
    struct sockaddr_in conn_addr;
    socklen_t sin_size;
    char buf[BUFSIZE];
    int n, yes = 1;
    char *pch1, *pch2;
    FILE *fp;
    long filesize;

    if ((listen_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
        ERR_EXIT("socket");

    if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) < 0)
        ERR_EXIT("setsockopt");

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = INADDR_ANY;
    memset(&(server_addr.sin_zero), '\0', 8);

    if (bind(listen_fd, (struct sockaddr *)&server_addr,
             sizeof(struct sockaddr)) < 0)
        ERR_EXIT("bind");

    if (listen(listen_fd, BACKLOG) < 0)
        ERR_EXIT("listen");

    while (1) {
        sin_size = sizeof(struct sockaddr_in);
        if ((conn_fd = accept(listen_fd, (struct sockaddr *)&conn_addr,
                              &sin_size)) < 0) {
            perror("accept");
            continue;
        }
        // printf("Got connection from %s\n", inet_ntoa(conn_addr.sin_addr));

        if ((n = read(conn_fd, buf, BUFSIZE - 1)) < 0) {
            perror("read");
        }
        pch1 = strtok(buf, " ");
        pch2 = strtok(NULL, " ");

        if (strcmp(pch1, "GET") != 0) {
            n = snprintf(buf, BUFSIZE,
                         "HTTP/1.0 400 Bad Request\r\n"
                         "Content-Type: text/plain; charset=utf-8\r\n"
                         "Content-Length: 11\r\n"
                         "\r\n"
                         "Bad Request");
            if (write(conn_fd, buf, n) < 0)
                perror("write");
            close(conn_fd);
            continue;
        }

        if (strcmp(pch2, "/") == 0) {
            fp = fopen("build/index.html", "rb");
            if (fp == NULL)
                ERR_EXIT("fopen");
            fseek(fp, 0, SEEK_END);
            filesize = ftell(fp);
            fseek(fp, 0, SEEK_SET);
            n = snprintf(buf, BUFSIZE,
                         "HTTP/1.0 200 OK\r\n"
                         "Content-Type: text/html; charset=utf-8\r\n"
                         "Content-Length: %ld\r\n"
                         "\r\n",
                         filesize);
            if (write(conn_fd, buf, n) < 0)
                perror("write");
            while ((n = fread(buf, 1, BUFSIZE, fp)) > 0) {
                if (write(conn_fd, buf, n) < 0)
                    perror("write");
            }
            fclose(fp);
            close(conn_fd);
            continue;
        }
        if (strcmp(pch2, "/bundle.js") == 0) {
            fp = fopen("build/bundle.js", "rb");
            if (fp == NULL)
                ERR_EXIT("fopen");
            fseek(fp, 0, SEEK_END);
            filesize = ftell(fp);
            fseek(fp, 0, SEEK_SET);
            n = snprintf(buf, BUFSIZE,
                         "HTTP/1.0 200 OK\r\n"
                         "Content-Type: text/javascript; charset=utf-8\r\n"
                         "Content-Length: %ld\r\n"
                         "\r\n",
                         filesize);
            if (write(conn_fd, buf, n) < 0)
                perror("write");
            while ((n = fread(buf, 1, BUFSIZE, fp)) > 0) {
                if (write(conn_fd, buf, n) < 0)
                    perror("write");
            }
            fclose(fp);
            close(conn_fd);
            continue;
        }
        n = snprintf(buf, BUFSIZE,
                     "HTTP/1.0 404 Not Found\r\n"
                     "Content-Type: text/plain; charset=utf-8\r\n"
                     "Content-Length: 9\r\n"
                     "\r\n"
                     "Not Found");
        if (write(conn_fd, buf, n) < 0)
            perror("write");
        close(conn_fd);
    }

    return 0;
}
