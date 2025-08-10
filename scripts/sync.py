#!/usr/bin/env python3
"""
Creates/updates a Markdown page for EVERY video on the channel.
Run locally once or let GitHub Actions call it hourly.
"""
from pathlib import Path
from yt_dlp import YoutubeDL
try:
    from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
except ImportError:
    print("Warning: youtube_transcript_api not available")
    YouTubeTranscriptApi = None
    NoTranscriptFound = Exception
import frontmatter, slugify, datetime, os, hashlib, textwrap, json

CHANNEL_URL = "https://www.youtube.com/@UAPGerb"
PAGES_DIR   = Path("pages")
PAGES_DIR.mkdir(exist_ok=True)

TEMPLATE = textwrap.dedent("""\
    ---
    title: "{title}"
    date: {date}
    video_id: {video_id}
    duration: "{duration}"
    tags: [uap, gerb]
    ---

    <iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" allowfullscreen></iframe>

    ---

    ## Transcript
    {body}
""")

def list_videos():
    """Fetch all videos from the YouTube channel."""
    print(f"Fetching videos from {CHANNEL_URL}...")
    opts = {
        "quiet": True, 
        "extract_flat": True, 
        "dump_single_json": True,
        "no_warnings": True
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(CHANNEL_URL, download=False)
        print(f"Found {len(info['entries'])} videos")
        return info["entries"]
    except Exception as e:
        print(f"Error fetching videos: {e}")
        return []

def safe_slug(s):
    """Create a safe filename slug from a string."""
    return slugify.slugify(s, lowercase=True)[:60]

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS format."""
    if not seconds:
        return "unknown"
    return str(datetime.timedelta(seconds=int(seconds)))

def write_page(entry):
    """Write a markdown page for a single video."""
    vid = entry["id"]
    
    # Handle timestamp - could be in different formats
    try:
        if "timestamp" in entry and entry["timestamp"]:
            date = datetime.datetime.fromtimestamp(entry["timestamp"]).date()
        elif "upload_date" in entry and entry["upload_date"]:
            date = datetime.datetime.strptime(entry["upload_date"], "%Y%m%d").date()
        else:
            date = datetime.date.today()
    except (ValueError, TypeError):
        date = datetime.date.today()
    
    title = entry.get("title", "Untitled Video")
    duration = entry.get("duration", 0)
    
    # Create filename
    slug = f"{date}--{safe_slug(title)}--{vid}.md"
    path = PAGES_DIR / slug

    # Fetch transcript
    print(f"Processing: {title}")
    try:
        if YouTubeTranscriptApi is None:
            body = "*Transcript API not available.*"
            print(f"  ⚠ Transcript API not available")
        else:
            api = YouTubeTranscriptApi()
            segs = api.fetch(vid)
            body = "\n\n".join(seg["text"] for seg in segs)
            print(f"  ✓ Transcript found ({len(segs)} segments)")
    except NoTranscriptFound:
        body = "*No transcript available for this video.*"
        print(f"  ⚠ No transcript available")
    except Exception as e:
        body = f"*Error fetching transcript: {str(e)}*"
        print(f"  ✗ Transcript error: {e}")

    # Generate markdown content
    md = TEMPLATE.format(
        title=title.replace('"', '\\"'),
        date=date,
        video_id=vid,
        duration=format_duration(duration),
        body=body
    )

    # Check if content has changed (avoid unnecessary writes)
    new_hash = hashlib.sha1(md.encode()).hexdigest()
    if path.exists():
        existing_hash = hashlib.sha1(path.read_bytes()).hexdigest()
        if existing_hash == new_hash:
            print(f"  → No changes")
            return False  # no change

    # Write the file
    path.write_text(md, encoding="utf-8")
    print(f"  ✓ Page updated: {slug}")
    return True

def main():
    """Main synchronization function."""
    print("Starting YouTube channel sync...")
    
    videos = list_videos()
    if not videos:
        print("No videos found or error occurred")
        return
    
    changed = False
    processed = 0
    
    for entry in videos:
        try:
            if write_page(entry):
                changed = True
            processed += 1
        except Exception as e:
            print(f"Error processing video {entry.get('id', 'unknown')}: {e}")
            continue
    
    print(f"\nProcessed {processed} videos")
    if changed:
        print("✓ Wiki updated with new content")
    else:
        print("✨ No changes needed")

if __name__ == "__main__":
    main()

