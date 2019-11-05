project      := postgres-webhook
current_dir  := $(shell pwd)
CPPFLAGS     += $(shell pkg-config --cflags libpq)
version      := 0.1
build_dir    := $(current_dir)/build

postgres-webhook: src/postgres-webhook.c src/req.c
	mkdir -p build
	gcc -std=c99 $(CPPFLAGS) -O3 -Wall -Wextra -o build/postgres-webhook src/postgres-webhook.c src/log.c -lpq -lcurl

clean:
	rm -rf build
