
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <time.h>

#define SERVER_PORT 5432
#define BUF_SIZE 8192
#define MAX_PENDING 5
#define MAX_LINE 256

int main(int argc, char *argv[])
{

    while (1)
    {
        struct sockaddr_in sin;
        char buf[MAX_LINE];
        int len;
        int s, new_s;
        /* build address data structure */
        bzero((char *)&sin, sizeof(sin));
        sin.sin_family = AF_INET;
        sin.sin_addr.s_addr = INADDR_ANY;
        // sin.sin_addr.s_addr = inet_addr("10.20.129.12");
        sin.sin_port = htons(SERVER_PORT);
        socklen_t addr_size;
        addr_size = sizeof(sin);
        FILE *fp;
        /* setup passive open */
        if ((s = socket(PF_INET, SOCK_STREAM, 0)) < 0)
        {
            perror("simplex-talk: socket");
            exit(1);
        }
        if ((bind(s, (struct sockaddr *)&sin, sizeof(sin))) < 0)
        {
            perror("l");
            exit(1);
        }
        listen(s, MAX_PENDING);
        int i = 2;
        if ((new_s = accept(s, (struct sockaddr *)&sin, &addr_size)) < 0)
        {
            perror("simplex-talk: accept");
            exit(1);
        }
        snprintf(buf, 20, "Hello\n");
        send(new_s, buf, MAX_LINE, 0);
        bzero(buf, MAX_LINE);
        int n;
    }
    return 0;
}
