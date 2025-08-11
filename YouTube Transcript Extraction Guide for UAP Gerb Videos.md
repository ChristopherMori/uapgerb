# YouTube Transcript Extraction Guide for UAP Gerb Videos

## Overview
While I was able to extract all video information, HTML embeds, and direct links from the UAP Gerb channel, transcript extraction faced API limitations. Here are alternative methods you can use to extract transcripts:

## Method 1: Using yt-dlp (Recommended)
```bash
# Install yt-dlp
pip install yt-dlp

# Extract transcript for a single video
yt-dlp --write-auto-sub --write-sub --sub-lang en --skip-download "VIDEO_URL"

# Extract transcripts for all videos (batch)
yt-dlp --write-auto-sub --write-sub --sub-lang en --skip-download --batch-file video_urls.txt
```

## Method 2: Using youtube-transcript-api (Local Environment)
```python
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([item['text'] for item in transcript])
    except Exception as e:
        return f"Error: {e}"

# Example usage
video_id = "QJxbyu-9Tj0"  # The 1948 Aztec, New Mexico UFO Crash Retrieval
transcript = get_transcript(video_id)
print(transcript)
```

## Method 3: Browser Extension
Use browser extensions like:
- YouTube Transcript
- Video Transcript
- Transcript for YouTube

## Video URLs for Batch Processing
All 43 video URLs are available in the provided files. Here are a few examples:

1. https://www.youtube.com/watch?v=QJxbyu-9Tj0 - The 1948 Aztec, New Mexico UFO Crash Retrieval
2. https://www.youtube.com/watch?v=9p99lTsC7wQ - UFO Legacy Programs - Science Applications International Corporation (SAIC)
3. https://www.youtube.com/watch?v=7Jc2G5aEH0A - 1997 Peru UFO Crash Retrieval - the Story of Jonathan Weygandt

## Notes
- Some videos may not have transcripts available
- Auto-generated transcripts may have accuracy issues
- Manual transcripts (when available) are more accurate
- Consider using multiple methods for best results

## Complete Video List
All 43 videos with their URLs, video IDs, and HTML embeds are provided in:
- uap_gerb_complete_results.json
- uap_gerb_results.csv
- uap_gerb_report.html

