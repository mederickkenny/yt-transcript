#!/usr/bin/env python3
import sys
import subprocess
import platform
import argparse
import requests
from youtube_transcript_api import YouTubeTranscriptApi


def format_transcript(fetched_transcript):
    """Format transcript with proper paragraphs based on >> markers and deduplication"""
    all_text = []
    last_text = None

    # First pass: collect all text with deduplication
    for snippet in fetched_transcript:
        text = snippet.text.strip()

        # Skip duplicates
        if text == last_text:
            continue

        all_text.append(text)
        last_text = text

    # Join everything together
    full_text = ' '.join(all_text)

    # Split on >> markers (these indicate new paragraphs/speakers)
    paragraphs = full_text.split('>>')

    # Clean up each paragraph: strip whitespace, remove empty ones
    cleaned_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para:
            cleaned_paragraphs.append(para)

    return '\n\n'.join(cleaned_paragraphs)


def copy_to_clipboard(text):
    """Copy text to clipboard based on platform"""
    try:
        system = platform.system()
        if system == 'Darwin':  # macOS
            subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
        elif system == 'Linux':
            subprocess.run(['xclip', '-selection', 'clipboard'],
                         input=text.encode('utf-8'), check=True)
        elif system == 'Windows':
            subprocess.run(['clip'], input=text.encode('utf-8'), check=True)
        print("  ✓ Copied to clipboard!")
        return True
    except Exception:
        print("  ✗ Clipboard copy failed")
        return False


def fetch_video_title(video_id):
    """Fetch video title from YouTube using oEmbed API"""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('title', '')
    except Exception as e:
        print(f"  Warning: Could not fetch video title: {e}")
        return ''


def sanitize_filename(title, max_length=100):
    """Sanitize video title for use in filename"""
    import re

    if not title:
        return ''

    # Replace invalid filename characters with hyphen
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '-')

    # Replace multiple spaces/hyphens with single hyphen
    title = re.sub(r'[\s\-]+', '-', title)

    # Remove leading/trailing hyphens and spaces
    title = title.strip('- ')

    # Truncate to max length
    if len(title) > max_length:
        title = title[:max_length].rstrip('- ')

    return title


def get_transcript(video_url, output_file=None):
    try:
        # Extract video ID
        video_id = video_url.split('v=')[-1].split('&')[0]

        # Get transcript using the API
        print(f"Fetching transcript for video ID: {video_id}")
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id, languages=['en'])

        # Format it
        clean_text = format_transcript(fetched_transcript)

        # Stats
        word_count = len(clean_text.split())
        paragraph_count = len(clean_text.split('\n\n'))
        print(f"✓ Transcript fetched")
        print(f"  Words: {word_count}")
        print(f"  Paragraphs: {paragraph_count}")

        # Copy to clipboard (always)
        copy_to_clipboard(clean_text)

        # Save to file (optional)
        if output_file is not None:
            # If output_file is empty string, use default name
            if output_file == '':
                # Fetch video title for filename
                video_title = fetch_video_title(video_id)
                sanitized_title = sanitize_filename(video_title)

                # Format: {title}-[video_id]-transcript.txt or fallback
                if sanitized_title:
                    output_file = f"{sanitized_title}-[{video_id}]-transcript.txt"
                else:
                    # Fallback if title fetch fails
                    output_file = f"{video_id}_transcript.txt"
                    print("  Using video ID as filename (title unavailable)")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(clean_text)
            print(f"  ✓ Saved to {output_file}")

    except Exception as e:
        print(f"✗ Error: {e}")
        if "Subtitles are disabled" in str(e):
            print("  This video doesn't have transcripts available.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch YouTube video transcripts and copy to clipboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  ytt https://youtube.com/watch?v=dQw4w9WgXcQ
  ytt -o https://youtube.com/watch?v=dQw4w9WgXcQ
  ytt -o my_video.txt https://youtube.com/watch?v=dQw4w9WgXcQ
        '''
    )

    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument(
        '-o', '--output',
        nargs='?',
        const='',  # Default value when -o is used without argument
        default=None,  # Value when -o is not used at all
        metavar='FILE',
        help='Save transcript to file (default: {video-title}-[video-id]-transcript.txt)'
    )

    args = parser.parse_args()

    get_transcript(args.url, args.output)


if __name__ == "__main__":
    main()