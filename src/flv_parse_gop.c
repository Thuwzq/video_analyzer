#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define FLV_HEADER_SIZE 9
#define TAG_HEADER_SIZE 11
#define AUDIO_TAG 8
#define VIDEO_TAG 9
#define SCRIPT_TAG 18

// FLV文件头结构
typedef struct {
    uint8_t signature[3];  // FLV signature, 'FLV', 3 Bytes
    uint8_t version;       // FLV version, 1 Byte
    uint8_t flags;         // FLV flags, 1 Byte, first 5 bits remained, 6th bit presents audio, 8th bit presents video
    uint32_t data_offset;  // data offset, usually 9, 4 Bytes
} FlvHeader;

// FLV标签头结构
typedef struct {
    uint8_t type;          // tag type, 1 Byte, 0x08: audio, 0x09: video, 0x12: script data
    uint32_t data_size;    // data size(not include tag header), 3 Bytes
    uint32_t timestamp;    // timestamp, 3 Bytes + 1 Byte extended, 4 Bytes total
    uint32_t stream_id;    // stream ID, always 0, 3 Bytes
} FlvTagHeader; 

// 视频标签信息结构
typedef struct {
    uint8_t frame_type;    // frame type: 1=keyframe, 2=interframe
    uint8_t codec_id;      // codec ID, 1 Byte
    uint8_t avc_packet_type; // AVC packet type, 1 Byte
    uint32_t composition_time; // composition time, 4 Bytes
} VideoTagInfo;

// GOP information structure
typedef struct {
    uint32_t gop_num;       // GOP number
    long start_offset;      // GOP start offset
    long gop_length;        // GOP length
    uint32_t timestamp;     // GOP start timestamp (I frame time stamp)
    uint32_t gop_duration_time; // GOP duration time
} GopInfo;

// 读取大端序32位无符号整数
uint32_t read_uint32_be(FILE *file) {
    uint8_t bytes[4];
    if (fread(bytes, 1, 4, file) != 4) {
        return 0;
    }
    return (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
}

// 读取大端序24位无符号整数
uint32_t read_uint24_be(FILE *file) {
    uint8_t bytes[3];
    if (fread(bytes, 1, 3, file) != 3) {
        return 0;
    }
    return (bytes[0] << 16) | (bytes[1] << 8) | bytes[2];
}

// 读取大端序16位无符号整数
uint16_t read_uint16_be(FILE *file) {
    uint8_t bytes[2];
    if (fread(bytes, 1, 2, file) != 2) {
        return 0;
    }
    return (bytes[0] << 8) | bytes[1];
}

// 解析FLV文件头
int parse_flv_header(FILE *file, FlvHeader *header) {
    if (fread(header->signature, 1, 3, file) != 3) {
        printf("FLV header parse error: signature read error!\n");
        return 0;
    }
    if (header->signature[0] != 'F' || header->signature[1] != 'L' || header->signature[2] != 'V') {
        printf("FLV header parse error: invalid FLV signature!\n");
        return 0;
    }
    
    if (fread(&header->version, 1, 1, file) != 1) {
        printf("FLV header parse error: version read error!\n");
        return 0;
    }
    
    if (fread(&header->flags, 1, 1, file) != 1) {
        printf("FLV header parse error: flags read error!\n");
        return 0;
    }
    
    header->data_offset = read_uint32_be(file);
    if (header->data_offset != 9) {
        printf("FLV header parse error: invalid data offset!\n");
        return 0;
    }
    
    return 1;
}

// 解析FLV标签头
int parse_flv_tag_header(FILE *file, FlvTagHeader *tag_header) {
    if (fread(&tag_header->type, 1, 1, file) != 1) {
        return 0;
    }
    
    tag_header->data_size = read_uint24_be(file);
    uint32_t timestamp = read_uint24_be(file);
    uint8_t timestamp_extended;
    if (fread(&timestamp_extended, 1, 1, file) != 1) {
        return 0;
    }
    tag_header->timestamp = (timestamp_extended << 24) | timestamp;
    
    tag_header->stream_id = read_uint24_be(file);
    if (tag_header->stream_id != 0) {
        return 0;
    }
    return 1;
}

// Parse video tag information
int parse_video_tag_info(FILE *file, VideoTagInfo *video_info) {
    uint8_t byte;
    if (fread(&byte, 1, 1, file) != 1) {
        return 0;
    }
    
    video_info->frame_type = (byte >> 4) & 0x0F;
    video_info->codec_id = byte & 0x0F;
    
    // if AVC codec, read composition time
    if (video_info->codec_id == 7) {
        if (fread(&video_info->avc_packet_type, 1, 1, file) != 1) {
            return 0;
        }
        
        video_info->composition_time = read_uint24_be(file);
        // return to the position before reading composition time
        fseek(file, -4, SEEK_CUR);
    } else {
        video_info->avc_packet_type = 0;
        video_info->composition_time = 0;
    }
    
    return 1;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("usage: %s <flv file path> <output file path>\n", argv[0]);
        return 1;
    }
    
    FILE *file = fopen(argv[1], "rb");
    if (!file) {
        printf("cannot open file: %s\n", argv[1]);
        return 1;
    }

    const char *output_filename = argv[2];
    FILE *output_file = NULL;
    if(output_filename) {
        output_file = fopen(output_filename, "w");
        if (!output_file) {
            printf("cannot open output file: %s\n", output_filename);
            fclose(file);
            return 1;
        }
    }
    
    // 解析FLV文件头
    FlvHeader header;
    if (!parse_flv_header(file, &header)) {
        printf("failed parse flv header, exit!\n");
        fclose(file);
        return 1;
    }
    
    printf("FLV file version: %d\n", header.version);
    printf("contains audio: %s\n", (header.flags & 0x04) ? "yes" : "no");
    printf("contains video: %s\n", (header.flags & 0x01) ? "yes" : "no");
    
    // Jump over PreviousTagSize0 after FLV header
    fseek(file, 4, SEEK_CUR);
    
    // Array of GOPs
    GopInfo *gop_list = NULL;
    int gop_count = 0;
    int gop_capacity = 10;
    gop_list = (GopInfo *)malloc(gop_capacity * sizeof(GopInfo));
    if (!gop_list) {
        printf("cannot malloc gop_list!\n");
        fclose(file);
        return 1;
    }
    
    // first gop position
    long current_position = ftell(file);
    long previous_position = current_position;
    uint32_t previous_timestamp = 0;

    // if find first I frame
    uint8_t if_find_first_frame = 0;
    uint8_t if_record_first_gop = 0;

    // record minimum 2 timestamp which means the beginning of first frame and the ending of first frame
    uint32_t first_frame_beginning = UINT32_MAX;
    uint32_t first_frame_ending = UINT32_MAX;

    // record final frame timestamp
    uint32_t final_frame_beginning = 0;
    
    // parse all tags
    while (!feof(file)) {
        // record gop start position
        long tag_start = current_position;
        
        // parse tag header
        FlvTagHeader tag_header;
        if (!parse_flv_tag_header(file, &tag_header)) {
            break;
        }
        
        // if video tag
        if (tag_header.type == VIDEO_TAG) {
            // save current position to restore after parsing video tag info
            long pos_before_video_info = ftell(file);
            
            // parse video tag information
            VideoTagInfo video_info;
            if (parse_video_tag_info(file, &video_info)) {
                // it's a real video key frame, not an AVC sequence header
                if (video_info.avc_packet_type == 1) {
                    // if key frame
                    if (video_info.frame_type == 1) {
                        // check gop list capacity
                        if (gop_count >= gop_capacity) {
                            gop_capacity *= 2;
                            gop_list = (GopInfo *)realloc(gop_list, gop_capacity * sizeof(GopInfo));
                            if (!gop_list) {
                                printf("gop_list memory realloc error!\n");
                                fclose(file);
                                return 1;
                            }
                        }

                        if (!if_find_first_frame) {
                            // first I frame will be stored as first gop
                            if_find_first_frame = 1;

                            gop_list[gop_count].gop_num = gop_count;
                            gop_list[gop_count].start_offset = tag_start;
                            gop_list[gop_count].timestamp = tag_header.timestamp;
                        } else {
                            // add gop information
                            gop_list[gop_count].gop_num = gop_count;
                            gop_list[gop_count].start_offset = tag_start;
                            gop_list[gop_count].timestamp = tag_header.timestamp;

                            if (gop_count > 1) {
                                gop_list[gop_count - 1].gop_length = tag_start - previous_position;
                                gop_list[gop_count - 1].gop_duration_time = tag_header.timestamp - previous_timestamp;
                            }
                        }

                        previous_position = tag_start;
                        previous_timestamp = tag_header.timestamp;
                        gop_count++;
                    } else {
                        // not a key frame video frame
                        if (if_find_first_frame && !if_record_first_gop) {
                            //record first gop without first frame
                            gop_list[gop_count].gop_num = gop_count;
                            gop_list[gop_count].start_offset = tag_start;

                            gop_list[gop_count - 1].gop_length = tag_start - previous_position;

                            previous_position = tag_start;

                            gop_count++;
                            if_record_first_gop = 1;
                        }
                    }

                    //calculate the beginning and ending timestamp of first frame
                    if(tag_header.timestamp < first_frame_beginning) {
                        first_frame_ending = first_frame_beginning;
                        first_frame_beginning = tag_header.timestamp;
                    } else if(tag_header.timestamp >= first_frame_beginning && tag_header.timestamp < first_frame_ending) {
                        first_frame_ending = tag_header.timestamp;
                    } else {
                        //do nothing
                    }

                    //calculate the beginning timestamp of final frame
                    if(tag_header.timestamp > final_frame_beginning) {
                        final_frame_beginning = tag_header.timestamp;
                    }
                }
            }

            // seek back to the position before parsing video tag info
            fseek(file, pos_before_video_info, SEEK_SET);
            
        }
        // jump tag data
        fseek(file, tag_header.data_size, SEEK_CUR);
        
        // read PreviousTagSize
        uint32_t previous_tag_size = read_uint32_be(file);
        if (previous_tag_size != tag_header.data_size + TAG_HEADER_SIZE) {
            printf("Warning: PreviousTagSize mismatch\n");
        }
        
        // update current position
        current_position = ftell(file);
    }

    if(first_frame_beginning != gop_list[0].timestamp) {
        printf("Warning: first frame timestamp not equal to first gop timestamp\n");
    }

    // update first gop and last gop information
    gop_list[0].start_offset = 0;
    gop_list[0].gop_duration_time = first_frame_ending - first_frame_beginning;
    gop_list[1].timestamp = first_frame_ending;
    gop_list[gop_count - 1].gop_length = current_position - gop_list[gop_count - 1].start_offset;
    // add one frame time to last gop duration
    gop_list[gop_count - 1].gop_duration_time = final_frame_beginning - gop_list[gop_count - 1].timestamp + first_frame_ending - first_frame_beginning;
    
    // output all GOP information
    printf("\nFound %d GOPs:\n", gop_count);
    printf("--------------------------------------------------------------------\n");
    printf("GOP seq\tStart byte\tGOP length\tGop start timestamp(ms)\tGOP duration(ms)\n");
    printf("--------------------------------------------------------------------\n");
    for (int i = 0; i < gop_count; i++) {
        printf("%-6d\t%-12ld\t%-8ld\t%-16d\t%-15d\n", 
            gop_list[i].gop_num, 
            gop_list[i].start_offset, 
            gop_list[i].gop_length, 
            gop_list[i].timestamp, 
            gop_list[i].gop_duration_time);

        if (output_file) {
            fprintf(output_file, "%d,%ld,%ld,%d,%d\n",
                gop_list[i].gop_num,
                gop_list[i].start_offset,
                gop_list[i].gop_length,
                gop_list[i].timestamp,
                gop_list[i].gop_duration_time);
        }
    }


    
    // release memory
    free(gop_list);
    fclose(file);

    if(output_file) {
        fclose(output_file);
    }
    
    return 0;
}    