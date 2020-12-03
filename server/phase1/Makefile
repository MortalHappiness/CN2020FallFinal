.PHONY: all clean

CC := gcc
CFLAGS := -Wall

TARGET := server

all: $(TARGET)

%: %.c
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -rf core.* $(TARGET)
