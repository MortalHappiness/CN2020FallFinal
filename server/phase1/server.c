#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

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
    int yes = 1;

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
        printf("Got connection from %s\n", inet_ntoa(conn_addr.sin_addr));
        if (write(conn_fd, "Hello, world!\n", 14) == -1)
            perror("send");

        close(conn_fd);
    }

    return 0;
}
