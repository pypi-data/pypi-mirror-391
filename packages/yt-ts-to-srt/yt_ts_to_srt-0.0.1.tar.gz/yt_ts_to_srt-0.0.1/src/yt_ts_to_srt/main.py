import json
import argparse
import sys
import re

def format_time(seconds):
    """Converts seconds to SRT time format (HH:MM:SS,ms)."""
    delta = int(seconds * 1000)
    hours, delta = divmod(delta, 3600000)
    minutes, delta = divmod(delta, 60000)
    seconds, milliseconds = divmod(delta, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def time_str_to_seconds(time_str):
    """Converts a M:SS or H:MM:SS timestamp string to seconds."""
    parts = list(map(int, time_str.split(':')))
    seconds = 0
    if len(parts) == 3:  # H:MM:SS
        seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:  # M:SS
        seconds = parts[0] * 60 + parts[1]
    return float(seconds)

def parse_txt_transcript(lines):
    """Parses a TXT transcript into a list of dictionaries."""
    timestamp_regex = re.compile(r'^\d{1,2}:\d{2}(?::\d{2})?$')
    transcript_data = []
    current_text_lines = []
    current_start_time = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if timestamp_regex.match(line):
            if current_start_time is not None and current_text_lines:
                transcript_data.append({"start": current_start_time, "text": " ".join(current_text_lines)})
            current_start_time = time_str_to_seconds(line)
            current_text_lines = []
        elif current_start_time is not None:
            current_text_lines.append(line)

    if current_start_time is not None and current_text_lines:
        transcript_data.append({"start": current_start_time, "text": " ".join(current_text_lines)})
    return transcript_data

def parse_json_transcript(file_content):
    """Parses a JSON transcript into a list of dictionaries."""
    try:
        data = json.loads(file_content)
    except json.JSONDecodeError:
        return None

    # Handle nested format (e.g., from youtube-dl)
    if isinstance(data, dict) and 'events' in data:
        processed_data = []
        for event in data.get('events', []):
            if 'segs' in event and event.get('segs'):
                full_text = "".join([seg['utf8'] for seg in event['segs']]).strip()
                if full_text:
                    processed_data.append({
                        "text": full_text,
                        "start": event.get('tStartMs', 0) / 1000.0,
                        "duration": event.get('dDurationMs', 2000) / 1000.0
                    })
        return processed_data
    # Handle flat list format
    elif isinstance(data, list):
        return data
    return None

def convert_to_srt(transcript_data):
    """Converts transcript data from any parsed source to an SRT formatted string."""
    srt_content = []
    for i, item in enumerate(transcript_data):
        start_time = item['start']
        text = item['text']

        # Use duration if available (from JSON), otherwise calculate from next segment
        if 'duration' in item:
            end_time = start_time + item['duration']
        elif i + 1 < len(transcript_data):
            end_time = transcript_data[i+1]['start']
        else:
            # Fallback for the very last item
            end_time = start_time + 3.0

        # Prevent overlapping or zero-duration subtitles
        if end_time <= start_time:
            end_time = start_time + 1.0

        srt_content.append(str(i + 1))
        srt_content.append(f"{format_time(start_time)} --> {format_time(end_time)}")
        srt_content.append(text)
        srt_content.append("")  # Blank line separator

    return "\n".join(srt_content)

def main():
    """Main function to handle command-line arguments and file operations."""
    parser = argparse.ArgumentParser(
        description="Convert a YouTube transcript (JSON or TXT) file to an SRT file."
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input transcript file (.json or .txt).",
    )
    parser.add_argument(
        "output_file",
        nargs='?',
        type=str,
        help="Path to the output SRT file. If not provided, it will be the input filename with .srt extension.",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    input_path = args.input_file
    output_path = args.output_file

    if not output_path:
        if input_path.lower().endswith('.json'):
            output_path = input_path[:-5] + ".srt"
        elif input_path.lower().endswith('.txt'):
            output_path = input_path[:-4] + ".srt"
        else:
            output_path = input_path + ".srt"

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            file_content = f.read()

        transcript_data = None
        if input_path.lower().endswith('.json'):
            transcript_data = parse_json_transcript(file_content)
        elif input_path.lower().endswith('.txt'):
            transcript_data = parse_txt_transcript(file_content.splitlines())
        else:
            print(f"Error: Unsupported file format. Please use a '.json' or '.txt' file.", file=sys.stderr)
            sys.exit(1)

        if not transcript_data:
            print(f"Warning: No transcript data could be parsed from '{input_path}'. Is the format correct?", file=sys.stderr)
            sys.exit(1)

        srt_output = convert_to_srt(transcript_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_output)

        print(f"Successfully converted '{input_path}' to '{output_path}'")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
