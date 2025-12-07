import sys
import argparse
import re
import os
import time
import glob
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import yt_dlp
import gemini_bridge
import google.generativeai as genai

# Setup Colorama if available (optional for standalone)
try:
    from colorama import Fore, Style, init
    init()
except ImportError:
    class Fore: RED = GREEN = YELLOW = CYAN = MAGENTA = ""
    class Style: RESET_ALL = BRIGHT = ""

def extract_video_id(url: str) -> str:
    """Extracts Video ID from various YouTube URL formats."""
    # Standard: v=...
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
    if match: return match.group(1)
    
    # Short: youtu.be/...
    match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if match: return match.group(1)
    
    return url # Assume it's the ID/URL if no pattern matches

def get_transcript(video_id: str) -> str:
    """Fetches transcript text using youtube-transcript-api."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        return formatter.format_transcript(transcript_list)
    except Exception:
        return ""

def download_audio_stream(url: str) -> str:
    """
    Downloads audio from the URL using yt-dlp.
    Returns path to the downloaded file.
    """
    print(f"{Fore.CYAN}[GOD MODE] Transcript unavailable. Engaging Deep Stream Download (Audio)...{Style.RESET_ALL}")
    
    # 1. Cleanup old downloads
    for f in glob.glob("vision_temp_audio.*"):
        try: os.remove(f)
        except: pass

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 'vision_temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Find the file (it might have extended with .mp3)
        if os.path.exists("vision_temp_audio.mp3"):
            return "vision_temp_audio.mp3"
        elif os.path.exists("vision_temp_audio.m4a"):
            return "vision_temp_audio.m4a"
        
        return ""
    except Exception as e:
        print(f"{Fore.RED}[DOWNLOAD ERROR] {e}{Style.RESET_ALL}")
        return ""

def analyze_media(file_path: str, url: str) -> str:
    """
    Uploads media to Gemini and generates analysis.
    """
    print(f"{Fore.CYAN}[GOD MODE] Uploading {file_path} to Gemini Cortex...{Style.RESET_ALL}")
    
    try:
        # 1. Upload File
        video_file = genai.upload_file(file_path)
        
        # 2. Wait for processing
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(1)
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            raise ValueError(f"File processing failed: {video_file.state.name}")

        print(f"\n{Fore.GREEN}[GOD MODE] Media Processed. Analyzing...{Style.RESET_ALL}")
        
        # 3. Generate Content
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            "You are an elite intelligence analyst listening to this audio stream. "
            "Your mission is to summarize the content. "
            "Ignore silence and intro music. Focus on the tactical information, technical details, and core message. "
            "Format output as a Briefing: 'EXECUTIVE SUMMARY', 'KEY POINTS', 'ACTIONABLE INTEL'."
        )
        
        response = model.generate_content([video_file, prompt])
        
        # 4. Cleanup Remote File? (Gemini auto-cleans up after 48h, but we can be polite)
        # genai.delete_file(video_file.name) 
        
        return response.text

    except Exception as e:
        return f"[GEMINI MULTIMODAL ERROR] {e}"

import memory_core

def vision_pipeline(url: str):
    print(f"{Fore.MAGENTA}>>> VISION BRIDGE ENGAGED: {url}{Style.RESET_ALL}")
    
    # AUTHENTICATION
    creds = gemini_bridge.authenticate_oauth()
    api_key = None
    if not creds:
        try:
            import google.auth
            creds, _ = google.auth.default()
        except: pass
        if not creds:
             api_key = gemini_bridge.load_env_file() or gemini_bridge.get_api_key(argparse.Namespace(api_key=None, key_file=None))
    
    if not creds and not api_key:
        print(f"{Fore.RED}[AUTH ERROR] Run 'gemini_bridge.py' first.{Style.RESET_ALL}")
        return

    if creds: genai.configure(credentials=creds)
    elif api_key: genai.configure(api_key=api_key)


    # PATH 1: TRANSCRIPT (Fast, YouTube Only)
    video_id = extract_video_id(url)
    transcript_text = get_transcript(video_id)

    if transcript_text:
        print(f"{Fore.GREEN}[FAST PATH] Text Transcript found ({len(transcript_text)} chars).{Style.RESET_ALL}")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"Summarize this video transcript tactically:\n\n{transcript_text[:30000]}" # Limit context slightly if massive
        )
        print("\n" + "="*60)
        print(response.text)
        print("="*60 + "\n")
        
        # LOG TO MEMORY
        memory_core.append_log("VISION", f"Analyzed {url}\n\n{response.text}", "SUMMARY")
        return

    # PATH 2: GOD MODE (Audio Download -> Multimodal)
    audio_path = download_audio_stream(url)
    if audio_path:
        summary = analyze_media(audio_path, url)
        print("\n" + "="*60)
        print(summary)
        print("="*60 + "\n")
        
        # LOG TO MEMORY
        memory_core.append_log("VISION", f"Analyzed {url} (Audio Analysis)\n\n{summary}", "SUMMARY")
        
        # Local Cleanup
        try: os.remove(audio_path)
        except: pass
    else:
        print(f"{Fore.RED}[FAILURE] Could not extract transcript OR audio stream from {url}.{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="Outlaw Exotix Universal Vision")
    parser.add_argument("url", help="Video URL (YouTube, Twitch, etc.)")
    args = parser.parse_args()
    
    vision_pipeline(args.url)

if __name__ == "__main__":
    main()
