// An util for calculate video all frame size
// Author: <whisky>

#include "libavformat/avformat.h"
#include "libavcodec/avcodec.h"
#include <stdio.h>

int main(int argc, char *argv[]) {
    AVFormatContext *fmt_ctx = NULL;
    AVPacket *pkt = NULL;
    AVCodecContext *dec_ctx = NULL;
    AVFrame *frame = NULL;

    int ret = -1;
    int video_stream_idx = -1;
    int found_iframe = 0;

    if (argc < 2) {
        av_log(fmt_ctx, AV_LOG_ERROR, "usage: %s <input video file>\n", argv[0]);
        goto __END;
    }

    // open input file
    if ((ret = avformat_open_input(&fmt_ctx, argv[1], NULL, NULL)) < 0) {
        av_log(fmt_ctx, AV_LOG_ERROR, "cannot open input video file\n");
        goto __END;
    }

    // get stream info
    if ((ret = avformat_find_stream_info(fmt_ctx, NULL)) < 0) {
        av_log(fmt_ctx, AV_LOG_ERROR, "cannot get stream info\n");
        goto __END;
    }

    printf("print meta info for %s:\n", argv[1]);
    // get video duration time
    if (fmt_ctx->duration != AV_NOPTS_VALUE) {
        double duration = (double)fmt_ctx->duration / AV_TIME_BASE;
        printf("  duration time: %.2f 秒\n", duration);
    } else {
        printf("  duration time: unknown\n");
    }

    // get video size
    if (fmt_ctx->pb && fmt_ctx->pb->seekable & AVIO_SEEKABLE_NORMAL) {
        int64_t file_size = avio_size(fmt_ctx->pb);
        if (file_size > 0) {
            printf("  file size: %.2f MB\n", (double)file_size / (1024 * 1024));
        } else {
            printf("  file size: unknown\n");
        }
    } else {
        printf("  file size: unknown\n");
    }

    // find video stream id
    video_stream_idx = av_find_best_stream(fmt_ctx, AVMEDIA_TYPE_VIDEO, -1, -1, NULL, 0);
    if(video_stream_idx < 0) {
        av_log(fmt_ctx, AV_LOG_ERROR, "no video stream!\n");
        goto __END;
    }

    // get frame rate
    AVRational framerate = av_guess_frame_rate(fmt_ctx, fmt_ctx->streams[video_stream_idx], NULL);
    if (framerate.num && framerate.den) {
        printf("  frame rate: %.2f fps\n", av_q2d(framerate));
    } else {
        printf("  frame rate: unknown\n");
    }

    // init AVPacket
    pkt = av_packet_alloc();
    if (!pkt) {
        av_log(fmt_ctx, AV_LOG_ERROR, "cannot allocate AVPacket\n");
        goto __END;
    }

    // init AVFrame
    frame = av_frame_alloc();
    if (!frame) {
        av_log(fmt_ctx, AV_LOG_ERROR, "cannot allocate AVFrame\n");
        goto __END;
    }

    int frame_count = 0;
    int i_frame_count = 0;
    printf("\n帧类型与大小统计:\n");
    // find the first I frame in video stream
    while (av_read_frame(fmt_ctx, pkt) >= 0 && !found_iframe) {
        // check if the packet belongs to video stream
        if (pkt->stream_index == video_stream_idx) {
            
            const char *frame_type;
            if (pkt->flags & AV_PKT_FLAG_KEY) {
                frame_type = "I";
                i_frame_count++;
            } else {
                frame_type = "P/B";
            }
            
            //print frame info
            printf("frame #%d: size before decode=%d Bytes, type=%s, timestamp=%.3f seconds\n", 
                frame_count, 
                pkt->size,
                frame_type,
                (double)pkt->pts * av_q2d(fmt_ctx->streams[video_stream_idx]->time_base));

            frame_count++;
        }
        av_packet_unref(pkt);
    }

    // print result summary
    if (frame_count > 0) {
        printf("\nresult summary:\n");
        printf("  total frame count: %d\n", frame_count);
        printf("  I frame count: %d (%.2f%%)\n", i_frame_count, (double)i_frame_count / frame_count * 100);
    } else {
        fprintf(stderr, "no video frame\n");
    }    

    __END:
    // 清理资源
    if (fmt_ctx) {
        avformat_close_input(&fmt_ctx);
    }

    if (dec_ctx) {
        avcodec_free_context(&dec_ctx);
    }

    if (pkt) {
        av_packet_free(&pkt);
    }

    if (frame) {
        av_frame_free(&frame);
    }

    return 0;
}