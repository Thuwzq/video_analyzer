# Compiler sets
include Makefile.config
CC := gcc
CFLAGS := -Wall -Wextra -O2 $(shell pkg-config --cflags libavutil libavformat 2>/dev/null) $(EXTRA_CFLAGS)
LDFLAGS := $(shell pkg-config --libs libavutil libavformat 2>/dev/null) $(EXTRA_LDFLAGS)

# project directories
SRCDIR := src
OBJDIR := obj
BINDIR := target/bin

# target files
TARGET := $(BINDIR)/all_video_frame_size

# get all source code
SRCS := $(wildcard $(SRCDIR)/*.c)
OBJS := $(patsubst $(SRCDIR)/%.c,$(OBJDIR)/%.o,$(filter %.c,$(SRCS)))

# default target
all: $(TARGET)

# connect .o files to target
$(TARGET): $(OBJS) | $(BINDIR)
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

# compile .c files to .o files
$(OBJDIR)/%.o: $(SRCDIR)/%.c | $(OBJDIR)
	$(CC) $(CFLAGS) -c $< -o $@

# create necessary directories
$(BINDIR) $(OBJDIR):
	mkdir -p $@

# make clean
clean:
	rm -rf $(OBJDIR) $(BINDIR)

.PHONY: all clean