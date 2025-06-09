# # Compiler sets
# include Makefile.config
# CC := gcc
# # CFLAGS := -Wall -Wextra -O2 $(shell pkg-config --cflags libavformat 2>/dev/null) $(EXTRA_CFLAGS)
# # LDFLAGS := $(shell pkg-config --libs libavformat 2>/dev/null) $(EXTRA_LDFLAGS)

# CFLAGS := -Wall -Wextra -O2 $(shell pkg-config --cflags libavutil libavformat libavcodec 2>/dev/null)
# LDFLAGS := $(shell pkg-config --libs libavutil libavformat libavcodec 2>/dev/null)

# # project directories
# SRCDIR := src
# OBJDIR := obj
# BINDIR := target/bin

# # target files
# TARGET := $(BINDIR)/all_video_frame_size

# # get all source code
# SRCS := $(wildcard $(SRCDIR)/*.c)
# OBJS := $(patsubst $(SRCDIR)/%.c,$(OBJDIR)/%.o,$(filter %.c,$(SRCS)))

# # default target
# all: $(TARGET)

# # connect .o files to target
# $(TARGET): $(OBJS) | $(BINDIR)
# 	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

# # compile .c files to .o files
# $(OBJDIR)/%.o: $(SRCDIR)/%.c | $(OBJDIR)
# 	$(CC) $(CFLAGS) -c $< -o $@

# # create necessary directories
# $(BINDIR) $(OBJDIR):
# 	mkdir -p $@

# # make clean
# clean:
# 	rm -rf $(OBJDIR) $(BINDIR)

# .PHONY: all clean


# 编译器设置
CC := gcc
CFLAGS := -Wall -Wextra -O2 $(shell pkg-config --cflags libavutil libavformat libavcodec)
LDFLAGS := $(shell pkg-config --libs libavutil libavformat libavcodec) -lm -lz -lpthread

# 项目目录结构
SRCDIR := src
OBJDIR := obj
BINDIR := target/bin

# 目标程序
TARGET := $(BINDIR)/all_video_frame_size

# 所有源码与目标文件
SRCS := $(wildcard $(SRCDIR)/*.c)
OBJS := $(patsubst $(SRCDIR)/%.c,$(OBJDIR)/%.o,$(filter %.c,$(SRCS)))

# 默认目标
all: $(TARGET)

# 链接目标程序
$(TARGET): $(OBJS) | $(BINDIR)
	$(CC) $(CFLAGS) $(OBJS) -o $@ $(LDFLAGS)

# 编译 .c -> .o
$(OBJDIR)/%.o: $(SRCDIR)/%.c | $(OBJDIR)
	$(CC) $(CFLAGS) -c $< -o $@

# 创建目录
$(BINDIR) $(OBJDIR):
	mkdir -p $@

# 清理中间文件
clean:
	rm -rf $(OBJDIR) $(BINDIR)

.PHONY: all clean
