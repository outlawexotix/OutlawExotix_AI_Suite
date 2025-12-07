import sys
import argparse
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import gemini_bridge
import google.generativeai as genai

def extract_video_id(url: str) -> str:
    """Extracts Video ID from various YouTube URL formats."""
    # Standard: v=...
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
    if match: return match.group(1)
    
    # Short: youtu.be/...
    match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if match: return match.group(1)
    
    return url # Assume it's the ID if no pattern matches

def get_transcript(video_id: str) -> str:
    """Fetches transcript text."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript_list)
        return text
    except Exception as e:
        print(f"[TRANSCRIPT ERROR] Could not retrieve caption: {e}")
        return ""

def summarize_video(video_url: str):
    video_id = extract_video_id(video_url)
    print(f"[{video_id}] Fetching transcript...")
    
    transcript_text = get_transcript(video_id)
    if not transcript_text:
        return

    print(f"[{video_id}] Transcript retrieved ({len(transcript_text)} chars). Analyzing...")

    # Reuse Auth from Gemini Bridge
    creds = gemini_bridge.authenticate_oauth()
    api_key = None
    
    if not creds:
        # Fallback to ADC/Env checks from gemini_bridge logic
        # We'll just instantiate a parser to reuse the logic or do it manually
        # Simpler: Try ADC manually here if oauth failed
        try:
            import google.auth
            creds, _ = google.auth.default()
        except Exception:
            pass
            
        if not creds:
            # Fallback to API Key
             api_key = gemini_bridge.load_env_file() or gemini_bridge.get_api_key(argparse.Namespace(api_key=None, key_file=None))
    
    if not creds and not api_key:
        print("[AUTH ERROR] No credentials found. Run 'gemini_bridge.py' to setup auth.")
        return

    # Configure Gemini
    if creds:
        genai.configure(credentials=creds)
    elif api_key:
        genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    system_prompt = (
        "You are an elite intelligence analyst. "
        "Your mission is to summarize the following video transcript. "
        "Identify key tactical insights, technical details, and the core message. "
        "Format output as a Briefing: 'EXECUTIVE SUMMARY', 'KEY POINTS', 'ACTIONABLE INTEL'."
    )
    
    prompt = f"{system_prompt}\n\n[TRANSCRIPT START]\n{transcript_text}\n[TRANSCRIPT END]"

    try:
        response = model.generate_content(prompt)
        print("\n" + "="*60)
        print(f" VIDEO INTELLIGENCE: {video_id}")
        print("="*60)
        print(response.text)
        print("="*60 + "\n")
    except Exception as e:
        print(f"[GEMINI ERROR] {e}")

def main():
    parser = argparse.ArgumentParser(description="Outlaw Exotix YouTube Vision")
    parser.add_argument("url", help="YouTube Video URL")
    args = parser.parse_args()
    
    summarize_video(args.url)

if __name__ == "__main__":
    main()
