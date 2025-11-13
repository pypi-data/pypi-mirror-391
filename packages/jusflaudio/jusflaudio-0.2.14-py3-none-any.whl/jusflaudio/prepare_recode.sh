#!/bin/bash

# Script to prepare video re-encoding commands for Chromecast v3 compatibility
# Uses ffmpeg for efficient stream copying and selective encoding
# Compatible codecs: video=h264, audio=aac/mp3/opus

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Output file for commands
OUTPUT_FILE="recode_commands.sh"

# Global option: force opus encoding for all audio
FORCE_OPUS=0

CRF=33
SPEED="fast"

# Default bitrate for video when detection fails
DEFAULT_VIDEO_BPS=2000000

# Check if required tools are installed
check_tools() {
    echo "Checking for required tools..."
    local missing_tools=0

    if ! command -v ffmpeg &> /dev/null; then
        echo -e "${RED}ERROR: ffmpeg is not installed${NC}"
        missing_tools=1
    else
        echo -e "${GREEN}✓ ffmpeg found${NC}"
    fi

    if ! command -v ffprobe &> /dev/null; then
        echo -e "${RED}ERROR: ffprobe is not installed${NC}"
        missing_tools=1
    else
        echo -e "${GREEN}✓ ffprobe found${NC}"
    fi

    if [ $missing_tools -eq 1 ]; then
        echo -e "${RED}Please install missing tools before running this script${NC}"
        exit 1
    fi
}

# Find all video files
find_videos() {
    local search_dir="${1:-.}"
    echo "Searching for video files in: $search_dir" >&2
    find -L "$search_dir" -type f \( -iname "*.avi" -o -iname "*.mp4" -o -iname "*.mkv" \) 2>/dev/null
}

# Get video information using ffprobe
get_video_info() {
    local video_file="$1"
    local info_type="$2"

    case "$info_type" in
        "vcodec")
            ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$video_file" 2>/dev/null
            ;;
        "acodec")
            ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$video_file" 2>/dev/null
            ;;
        "width")
            ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "$video_file" 2>/dev/null
            ;;
        "height")
            ffprobe -v error -select_streams v:0 -show_entries stream=height -of default=noprint_wrappers=1:nokey=1 "$video_file" 2>/dev/null
            ;;
        "vbitrate")
            ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$video_file" 2>/dev/null
            ;;
        "abitrate")
            ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$video_file" 2>/dev/null
            ;;
    esac
}

# Check if codec is in allowed list
is_video_codec_allowed() {
    local codec="$1"
    # Allowed video codec: h264 (also known as avc)
    [[ "$codec" == "h264" ]] || [[ "$codec" == "avc" ]]
}

is_audio_codec_allowed() {
    local codec="$1"
    # Allowed audio codecs: aac, mp3, opus
    [[ "$codec" == "aac" ]] || [[ "$codec" == "mp3" ]] || [[ "$codec" == "opus" ]]
}

# Generate ffmpeg command
generate_ffmpeg_command() {
    local input_file="$1"
    local vcodec="$2"
    local acodec="$3"
    local width="$4"
    local height="$5"
    local vbitrate="$6"
    local abitrate="$7"

    local output_file="${input_file%.*}_chromed2.mkv"

    # Determine video encoding strategy
    local needs_video_encode=0
    local needs_scaling=0
    local scale_filter=""

    # Check if we need to scale
    if [ -n "$width" ] && [ "$width" -gt 1280 ]; then
        needs_scaling=1
        scale_filter="scale=1280:-2"
    fi

    # Determine video codec settings
    if ! is_video_codec_allowed "$vcodec"; then
        # Video needs recoding to h264
        needs_video_encode=1
    elif [ $needs_scaling -eq 1 ]; then
        # Video is h264 but needs scaling, so must encode
        needs_video_encode=1
    fi

    if [ $needs_video_encode -eq 1 ]; then
        # Use 2-pass encoding with original bitrate
        # Default to 2M if bitrate cannot be determined
        local target_vbitrate="$vbitrate"
        if [ -z "$target_vbitrate" ] || [ "$target_vbitrate" = "N/A" ]; then
            target_vbitrate="$DEFAULT_VIDEO_BPS"
        fi

        # Build video filter options
        local vf_opts=""
        if [ $needs_scaling -eq 1 ]; then
            vf_opts="-vf $scale_filter"
        fi

        # Generate 2-pass command
        local cmd="# Pass 1\n"
        cmd="${cmd}ffmpeg -y -i \"$input_file\" $vf_opts -c:v libx264 -b:v $target_vbitrate -pass 1 -an -f null /dev/null && \\\\\n"
        cmd="${cmd}# Pass 2\n"
        cmd="${cmd}ffmpeg -i \"$input_file\" $vf_opts -c:v libx264 -b:v $target_vbitrate -pass 2 -c:a libopus -b:a 64k \"$output_file\""

        echo -e "$cmd"
    else
        # Video is already h264 and no scaling needed - copy it
        local cmd="ffmpeg -i \"$input_file\" -c:v copy"

        # Determine audio encoding strategy
        if [ "$FORCE_OPUS" -eq 1 ]; then
            # Force opus encoding for all audio
            cmd="$cmd -c:a libopus -b:a 64k"
        elif is_audio_codec_allowed "$acodec"; then
            # Audio codec is already compatible, copy it
            cmd="$cmd -c:a copy"
        else
            # Audio codec needs recoding, use opus
            cmd="$cmd -c:a libopus -b:a 64k"
        fi

        # Add output file
        cmd="$cmd \"$output_file\""

        echo "$cmd"
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS] [DIRECTORY]"
    echo ""
    echo "Options:"
    echo "  --force-opus    Force audio encoding to opus for all files (even if audio is already compatible)"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Arguments:"
    echo "  DIRECTORY       Directory to search for videos (default: current directory)"
    echo ""
    echo "Compatible codecs: video=h264, audio=aac/mp3/opus"
}

# Main function
main() {
    local search_dir="."

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force-opus)
                FORCE_OPUS=1
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            -*)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                search_dir="$1"
                shift
                ;;
        esac
    done

    echo "================================================"
    echo "Video Recoding Preparation for Chromecast v3"
    echo "================================================"
    echo ""

    if [ "$FORCE_OPUS" -eq 1 ]; then
        echo -e "${YELLOW}Option: Force opus encoding enabled${NC}"
        echo ""
    fi

    # Check tools
    check_tools
    echo ""

    # Initialize output file
    echo "#!/bin/bash" > "$OUTPUT_FILE"
    echo "# Auto-generated ffmpeg re-encoding commands for Chromecast v3 compatibility" >> "$OUTPUT_FILE"
    echo "# Uses stream copying when possible for speed and quality preservation" >> "$OUTPUT_FILE"
    echo "# Generated on: $(date)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    local total_files=0
    local files_need_recoding=0

    # Find and process videos
    echo "Analyzing video files..."
    echo ""

    while IFS= read -r video_file; do
        total_files=$((total_files + 1))

        echo -e "${YELLOW}Processing: $video_file${NC}"

        # Get video information
        local vcodec=$(get_video_info "$video_file" "vcodec")
        local acodec=$(get_video_info "$video_file" "acodec")
        local width=$(get_video_info "$video_file" "width")
        local height=$(get_video_info "$video_file" "height")
        local vbitrate=$(get_video_info "$video_file" "vbitrate")
        local abitrate=$(get_video_info "$video_file" "abitrate")

        # Format bitrates for display
        local vbitrate_display="N/A"
        local abitrate_display="N/A"
        if [ -n "$vbitrate" ] && [ "$vbitrate" != "N/A" ]; then
            vbitrate_display="$(awk "BEGIN {printf \"%.2f\", $vbitrate/1000000}")Mbps"
        fi
        if [ -n "$abitrate" ] && [ "$abitrate" != "N/A" ]; then
            abitrate_display="$(awk "BEGIN {printf \"%.0f\", $abitrate/1000}")kbps"
        fi

        echo "  Video codec: $vcodec | Audio codec: $acodec | Resolution: ${width}x${height}"
        echo "  Video bitrate: $vbitrate_display | Audio bitrate: $abitrate_display"

        # Check if recoding is needed
        local needs_recode=0

        if ! is_video_codec_allowed "$vcodec"; then
            echo -e "  ${RED}✗ Video codec needs recoding (not h264)${NC}"
            needs_recode=1
        else
            echo -e "  ${GREEN}✓ Video codec is compatible${NC}"
        fi

        if [ "$FORCE_OPUS" -eq 1 ]; then
            echo -e "  ${YELLOW}⚠ Audio will be forced to opus${NC}"
            needs_recode=1
        elif ! is_audio_codec_allowed "$acodec"; then
            echo -e "  ${RED}✗ Audio codec needs recoding (not aac/mp3/opus)${NC}"
            needs_recode=1
        else
            echo -e "  ${GREEN}✓ Audio codec is compatible${NC}"
        fi

        if [ -n "$width" ] && [ "$width" -gt 1280 ]; then
            echo -e "  ${YELLOW}⚠ Resolution will be scaled down to 1280px width${NC}"
            needs_recode=1
        fi

        # Check if chromecasted version already exists
        local output_file="${video_file%.*}_chromed2.mkv"
        if [ -f "$output_file" ]; then
            echo -e "  ${GREEN}→ Chromed version already exists, skipping${NC}"
            echo ""
            continue
        fi

        # Generate command if needed
        if [ $needs_recode -eq 1 ]; then
            files_need_recoding=$((files_need_recoding + 1))
            local ffmpeg_cmd=$(generate_ffmpeg_command "$video_file" "$vcodec" "$acodec" "$width" "$height" "$vbitrate" "$abitrate")
            echo "" >> "$OUTPUT_FILE"
            echo "# File: $video_file" >> "$OUTPUT_FILE"
            echo "# Original: vcodec=$vcodec, acodec=$acodec, resolution=${width}x${height}" >> "$OUTPUT_FILE"
            echo "# Original bitrates: video=${vbitrate_display}, audio=${abitrate_display}" >> "$OUTPUT_FILE"
            echo -e "$ffmpeg_cmd" >> "$OUTPUT_FILE"
            echo -e "  ${GREEN}→ Command added to $OUTPUT_FILE${NC}"
        else
            echo -e "  ${GREEN}→ No recoding needed${NC}"
        fi

        echo ""

    done < <(find_videos "$search_dir")

    # Make output file executable
    chmod +x "$OUTPUT_FILE"

    # Summary
    echo "================================================"
    echo "Summary"
    echo "================================================"
    echo "Total video files found: $total_files"
    echo "Files needing recoding: $files_need_recoding"
    echo ""

    if [ $files_need_recoding -gt 0 ]; then
        echo -e "${GREEN}Re-encoding commands have been saved to: $OUTPUT_FILE${NC}"
        echo "To start re-encoding, run: ./$OUTPUT_FILE"
    else
        echo -e "${GREEN}All video files are already compatible with Chromecast v3!${NC}"
    fi
}

# Run main function with optional directory argument
main "$@"
