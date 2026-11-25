/*
 * scy-shell-ipc — Ultra-low-latency native POSIX Unix-socket IPC client for Scy-Shell
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Used by Hyprland / Wayland compositor keybindings (`exec, scy-shell-ipc ...`)
 * so hotkeys (volume, brightness, launcher, lock, overview) dispatch in <0.3ms
 * without interpreter startup overhead.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

static void json_escape_print(FILE *f, const char *s) {
    fputc('"', f);
    for (; *s; s++) {
        unsigned char c = (unsigned char)*s;
        switch (c) {
            case '"':  fputs("\\\"", f); break;
            case '\\': fputs("\\\\", f); break;
            case '\b': fputs("\\b", f); break;
            case '\f': fputs("\\f", f); break;
            case '\n': fputs("\\n", f); break;
            case '\r': fputs("\\r", f); break;
            case '\t': fputs("\\t", f); break;
            default:
                if (c < 0x20) fprintf(f, "\\u%04x", c);
                else fputc(c, f);
        }
    }
    fputc('"', f);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: scy-shell-ipc [--json] <method-or-target> [args...]\n");
        return 2;
    }

    int raw_json = 0;
    int arg_start = 1;
    if (strcmp(argv[1], "--json") == 0) {
        raw_json = 1;
        arg_start = 2;
    }
    if (arg_start >= argc) {
        fprintf(stderr, "Error: missing IPC command\n");
        return 2;
    }

    const char *sock_override = getenv("SCY_SHELL_SOCK");
    const char *xdg_rt = getenv("XDG_RUNTIME_DIR");
    char sock_path[256];

    if (sock_override && sock_override[0] != '\0') {
        snprintf(sock_path, sizeof(sock_path), "%s", sock_override);
    } else if (xdg_rt && xdg_rt[0] != '\0') {
        snprintf(sock_path, sizeof(sock_path), "%s/scy-shell.sock", xdg_rt);
    } else {
        snprintf(sock_path, sizeof(sock_path), "/tmp/scy-shell-%u.sock", (unsigned)getuid());
    }

    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("scy-shell-ipc: socket");
        return 1;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    if ((size_t)snprintf(addr.sun_path, sizeof(addr.sun_path), "%s", sock_path) >= sizeof(addr.sun_path)) { fprintf(stderr, "scy-shell-ipc: socket path too long\n"); close(fd); return 2; }

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        fprintf(stderr, "scy-shell-ipc: cannot connect to %s (%s)\n", sock_path, strerror(errno));
        return 3;
    }

    char *payload = NULL;
    size_t payload_len = 0;
    FILE *mem = open_memstream(&payload, &payload_len);
    if (!mem) {
        close(fd);
        return 1;
    }

    fputs("{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ipc.dispatch\",\"params\":{\"args\":[", mem);
    for (int i = arg_start; i < argc; i++) {
        if (i > arg_start) fputc(',', mem);
        json_escape_print(mem, argv[i]);
    }
    fputs("]}}\n", mem);
    fclose(mem);

    ssize_t written = 0;
    while ((size_t)written < payload_len) {
        ssize_t n = write(fd, payload + written, payload_len - (size_t)written);
        if (n < 0) {
            if (errno == EINTR) continue;
            free(payload);
            close(fd);
            return 1;
        }
        written += n;
    }
    free(payload);
    shutdown(fd, SHUT_WR);

    char buf[8192];
    ssize_t n;
    int saw_error = 0;
    while ((n = read(fd, buf, sizeof(buf) - 1)) > 0) {
        buf[n] = '\0';
        if (strstr(buf, "\"error\":") != NULL && strstr(buf, "\"error\":null") == NULL && strstr(buf, "\"error\": null") == NULL) {
            saw_error = 1;
        }
        if (raw_json || saw_error) {
            fwrite(buf, 1, (size_t)n, saw_error ? stderr : stdout);
        } else {
            fwrite(buf, 1, (size_t)n, stdout);
        }
    }
    close(fd);
    return saw_error ? 1 : 0;
}
