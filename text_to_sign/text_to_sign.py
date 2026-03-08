"""
Text-to-Sign Language Video Sequence Generator
Uses OpenRouter API to intelligently convert natural English text 
into playable sign language video sequences.
"""

import json
import os
import requests
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.2-3b-instruct:free"  # Free Llama model - confirmed working

# Paths
SCRIPT_DIR = Path(__file__).parent
INDEX_FILE = SCRIPT_DIR / "WLASL_Processed_Videos" / "processed_index.json"
VIDEO_DIR = SCRIPT_DIR / "WLASL_Processed_Videos"


# ============================================================
# LOAD VOCABULARY
# ============================================================

def load_vocabulary():
    """Load the vocabulary index from JSON file."""
    if not INDEX_FILE.exists():
        raise FileNotFoundError(f"Index file not found: {INDEX_FILE}")
    
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        raw_index = json.load(f)
    
    # Convert to vocab_json format: token -> video path
    vocab = {}
    for token, videos in raw_index.items():
        if videos:  # Take first video if multiple exist
            vocab[token.upper()] = str(VIDEO_DIR / videos[0])
    
    return vocab


# ============================================================
# SYSTEM PROMPT FOR API
# ============================================================

SYSTEM_PROMPT = """You are an expert Sign Language NLP translator.

Your job is to convert English text into a VALID, PLAYABLE video sequence using ONLY the available vocabulary.

RULES:
1. NORMALIZATION:
   - Convert tokens to UPPERCASE
   - Remove punctuation
   - Expand contractions (I'm → I AM)
   - Remove filler words (is, are, was, the, a, an, to) if not in vocabulary

2. SIGN LANGUAGE STRUCTURE:
   - Prefer: TIME → SUBJECT → OBJECT → VERB
   - Drop tense markers if not available
   - Use concept-based translation

3. TOKEN MATCHING:
   - ONLY use tokens that exist in the provided vocabulary
   - Singularize plurals (dogs → DOG)
   - Convert verbs to base form (eating → EAT)
   - If no match exists → DROP the word or suggest closest alternative

4. FAIL-SAFE:
   - NEVER return empty sequence if any match is possible
   - Return at least one valid token

OUTPUT FORMAT (STRICT JSON ONLY - NO MARKDOWN):
{
  "original_text": "<original user text>",
  "normalized_text": "<clean sign-ready text>",
  "selected_tokens": ["TOKEN1", "TOKEN2"],
  "suggestions": "<friendly message if words were dropped or substituted>",
  "video_sequence": ["path1.mp4", "path2.mp4"]
}
"""


# ============================================================
# API CALL
# ============================================================

def call_openrouter(user_text: str, vocab: dict) -> dict:
    """Send text and vocabulary to OpenRouter API for translation."""
    
    # Build the user message with vocabulary
    vocab_list = list(vocab.keys())
    
    user_message = f"""
USER TEXT: "{user_text}"

AVAILABLE VOCABULARY ({len(vocab_list)} tokens):
{json.dumps(vocab_list, indent=2)}

VOCABULARY WITH PATHS:
{json.dumps(vocab, indent=2)}

Convert the user text into a valid sign language video sequence.
Return ONLY valid JSON, no markdown formatting.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Text-to-Sign Translator"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1,  # Low temperature for deterministic output
        "max_tokens": 2000
    }
    
    # Retry logic for rate limiting
    max_retries = 3
    base_delay = 2  # seconds
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
            
            # Handle rate limiting with retry
            if response.status_code == 429:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff: 2, 4, 8 seconds
                    print(f"\n⏳ Rate limited. Waiting {delay}s before retry ({attempt + 1}/{max_retries})...")
                    import time
                    time.sleep(delay)
                    continue
                else:
                    return {"error": "Rate limit exceeded. Please wait a minute and try again."}
            
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Clean up response (remove markdown if present)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries and "429" in str(e):
                delay = base_delay * (2 ** attempt)
                print(f"\n⏳ Rate limited. Waiting {delay}s before retry ({attempt + 1}/{max_retries})...")
                import time
                time.sleep(delay)
                continue
            return {"error": f"API request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse API response: {str(e)}", "raw_response": content}


# ============================================================
# MAIN FUNCTION
# ============================================================

def text_to_sign(user_text: str) -> dict:
    """
    Convert user text to sign language video sequence.
    
    Args:
        user_text: Natural English text to convert
        
    Returns:
        Dictionary containing:
        - original_text: The input text
        - normalized_text: Cleaned sign-ready text
        - selected_tokens: List of matched tokens
        - video_sequence: List of video file paths
        - suggestions: Any helpful messages about word substitutions
    """
    # Load vocabulary
    vocab = load_vocabulary()
    
    # Call API for translation
    result = call_openrouter(user_text, vocab)
    
    # ============================================================
    # VALIDATION: Filter out invalid tokens
    # ============================================================
    if "error" not in result:
        # Validate selected_tokens - only keep tokens that exist in vocab
        original_tokens = result.get("selected_tokens", [])
        valid_tokens = []
        invalid_tokens = []
        
        for token in original_tokens:
            token_upper = token.upper()
            if token_upper in vocab:
                valid_tokens.append(token_upper)
            else:
                invalid_tokens.append(token)
        
        # Build video sequence from VALID tokens only
        valid_video_sequence = []
        for token in valid_tokens:
            video_path = vocab.get(token)
            if video_path and os.path.exists(video_path):
                valid_video_sequence.append(video_path)
            else:
                # Token exists in vocab but video file is missing
                invalid_tokens.append(f"{token} (file missing)")
                valid_tokens.remove(token)
        
        # Update result with validated data
        result["selected_tokens"] = valid_tokens
        result["video_sequence"] = valid_video_sequence
        
        # Add warning about invalid tokens
        if invalid_tokens:
            warning = f"Removed invalid tokens: {invalid_tokens}"
            existing_suggestions = result.get("suggestions", "")
            result["suggestions"] = f"{existing_suggestions} ⚠️ {warning}".strip()
    
    return result


def display_result(result: dict):
    """Pretty print the translation result."""
    print("\n" + "=" * 60)
    print("📝 TEXT-TO-SIGN TRANSLATION RESULT")
    print("=" * 60)
    
    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        if "raw_response" in result:
            print(f"\n📄 Raw Response:\n{result['raw_response']}")
        return
    
    print(f"\n📌 Original Text: {result.get('original_text', 'N/A')}")
    print(f"🔤 Normalized Text: {result.get('normalized_text', 'N/A')}")
    print(f"\n🎯 Selected Tokens: {result.get('selected_tokens', [])}")
    
    if result.get('suggestions'):
        print(f"\n💡 Suggestions: {result['suggestions']}")
    
    print("\n🎬 Video Sequence:")
    for i, video in enumerate(result.get('video_sequence', []), 1):
        exists = "✅" if os.path.exists(video) else "❌"
        print(f"   {i}. {exists} {video}")
    
    print("\n" + "=" * 60)


# ============================================================
# VIDEO PLAYBACK - Professional Sign Language Video Player
# ============================================================

class SignVideoPlayer:
    """
    Professional video sequence player with pre-loaded frames.
    
    Features:
        - Pre-loads all frames for seamless playback
        - Full keyboard controls
        - Visual HUD overlay
        - Speed control
        - Seek and replay functionality
    """
    
    def __init__(self, video_paths: list, window_name: str = "Sign Language Player"):
        self.video_paths = [v for v in video_paths if os.path.exists(v)]
        self.window_name = window_name
        self.frames = []           # All frames in sequence
        self.frame_markers = []    # (start_idx, end_idx, video_name) for each video
        self.total_frames = 0
        self.base_fps = 30
        
        # Playback state
        self.current_frame = 0
        self.paused = False
        self.speed = 1.0
        self.running = True
        
    def load_frames(self) -> bool:
        """Pre-load all video frames into memory."""
        try:
            import cv2
            self.cv2 = cv2
        except ImportError:
            print("\n❌ OpenCV not installed. Install with: pip install opencv-python")
            return False
        
        if not self.video_paths:
            print("\n❌ No valid video files to load.")
            return False
        
        print(f"\n📥 Loading {len(self.video_paths)} videos into memory...")
        
        for video_path in self.video_paths:
            video_name = os.path.basename(video_path)
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                print(f"   ⚠️  Skipping: {video_name}")
                continue
            
            # Get FPS from first video
            if not self.frames:
                self.base_fps = cap.get(cv2.CAP_PROP_FPS) or 30
            
            start_idx = len(self.frames)
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize for consistent display
                height, width = frame.shape[:2]
                max_dim = 720
                if max(height, width) > max_dim:
                    scale = max_dim / max(height, width)
                    frame = cv2.resize(frame, (int(width * scale), int(height * scale)))
                
                self.frames.append(frame)
                frame_count += 1
            
            cap.release()
            
            if frame_count > 0:
                end_idx = len(self.frames) - 1
                self.frame_markers.append((start_idx, end_idx, video_name))
                print(f"   ✅ Loaded: {video_name} ({frame_count} frames)")
        
        self.total_frames = len(self.frames)
        
        if self.total_frames == 0:
            print("\n❌ No frames loaded!")
            return False
        
        print(f"\n✅ Loaded {self.total_frames} total frames from {len(self.frame_markers)} videos")
        return True
    
    def get_current_sign_info(self) -> tuple:
        """Get current sign name and progress within that sign."""
        for idx, (start, end, name) in enumerate(self.frame_markers):
            if start <= self.current_frame <= end:
                progress = (self.current_frame - start) / max(1, end - start)
                return idx + 1, len(self.frame_markers), name, progress
        return 0, 0, "Unknown", 0
    
    def draw_hud(self, frame):
        """Draw heads-up display overlay on frame."""
        cv2 = self.cv2
        h, w = frame.shape[:2]
        
        # Get current sign info
        sign_num, total_signs, sign_name, sign_progress = self.get_current_sign_info()
        
        # Semi-transparent overlay background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 70), (0, 0, 0), -1)
        cv2.rectangle(overlay, (0, h - 50), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Top HUD - Current sign info
        sign_text = f"Sign {sign_num}/{total_signs}: {sign_name}"
        cv2.putText(frame, sign_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Speed indicator
        speed_text = f"Speed: {self.speed:.1f}x"
        if self.paused:
            speed_text = "⏸ PAUSED"
        cv2.putText(frame, speed_text, (w - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Overall progress bar (bottom)
        bar_y = h - 35
        bar_height = 8
        bar_margin = 20
        bar_width = w - 2 * bar_margin
        
        # Background bar
        cv2.rectangle(frame, (bar_margin, bar_y), (bar_margin + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        # Progress fill
        progress = self.current_frame / max(1, self.total_frames - 1)
        fill_width = int(bar_width * progress)
        cv2.rectangle(frame, (bar_margin, bar_y), (bar_margin + fill_width, bar_y + bar_height), (0, 200, 0), -1)
        
        # Sign segment markers
        for start, end, _ in self.frame_markers:
            marker_x = bar_margin + int(bar_width * (start / max(1, self.total_frames - 1)))
            cv2.line(frame, (marker_x, bar_y - 3), (marker_x, bar_y + bar_height + 3), (255, 255, 0), 2)
        
        # Current position indicator
        pos_x = bar_margin + int(bar_width * progress)
        cv2.circle(frame, (pos_x, bar_y + bar_height // 2), 8, (255, 255, 255), -1)
        
        # Frame counter
        frame_text = f"Frame: {self.current_frame + 1}/{self.total_frames}"
        cv2.putText(frame, frame_text, (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Controls hint
        controls = "[SPACE]Pause [←→]Seek [+−]Speed [R]Replay [N]Next [Q]Quit"
        cv2.putText(frame, controls, (w - 480, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        return frame
    
    def jump_to_sign(self, sign_index: int):
        """Jump to the start of a specific sign."""
        if 0 <= sign_index < len(self.frame_markers):
            self.current_frame = self.frame_markers[sign_index][0]
    
    def get_current_sign_index(self) -> int:
        """Get the index of the current sign being played."""
        for idx, (start, end, _) in enumerate(self.frame_markers):
            if start <= self.current_frame <= end:
                return idx
        return 0
    
    def play(self) -> bool:
        """Main playback loop with full controls."""
        cv2 = self.cv2
        
        # Create window
        try:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, 800, 600)
        except cv2.error:
            print("\n⚠️  OpenCV display not available. Creating merged video...")
            return self.play_merged_video()
    
    def play_merged_video(self) -> bool:
        """
        Fallback: Merge all frames into a single video file and play with system player.
        This gives you FULL control via VLC/Windows Media Player (pause, slow-mo, seek, etc.)
        """
        import tempfile
        cv2 = self.cv2
        
        # Create temp file for merged video
        temp_dir = tempfile.gettempdir()
        merged_path = os.path.join(temp_dir, "sign_sequence_merged.mp4")
        
        print(f"\n📼 Creating merged video...")
        print(f"   Output: {merged_path}")
        
        # Get frame dimensions from first frame
        if not self.frames:
            print("   ❌ No frames to merge!")
            return False
        
        h, w = self.frames[0].shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = self.base_fps  # Use original FPS (you can slow down in player)
        out = cv2.VideoWriter(merged_path, fourcc, fps, (w, h))
        
        if not out.isOpened():
            print("   ❌ Failed to create video writer!")
            return False
        
        # Write all frames with sign labels overlay
        print(f"   Writing {self.total_frames} frames...")
        
        for frame_idx, frame in enumerate(self.frames):
            # Add sign label overlay
            frame_with_label = frame.copy()
            
            # Find which sign this frame belongs to
            for sign_idx, (start, end, video_name) in enumerate(self.frame_markers):
                if start <= frame_idx <= end:
                    # Add semi-transparent bar at top
                    overlay = frame_with_label.copy()
                    cv2.rectangle(overlay, (0, 0), (w, 50), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.5, frame_with_label, 0.5, 0, frame_with_label)
                    
                    # Add text
                    sign_name = video_name.replace('.mp4', '').split('_')[0].upper()
                    label = f"Sign {sign_idx + 1}/{len(self.frame_markers)}: {sign_name}"
                    cv2.putText(frame_with_label, label, (10, 35), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    break
            
            out.write(frame_with_label)
        
        out.release()
        
        print(f"\n✅ Merged video created!")
        print(f"\n🎬 Opening with your default video player...")
        print("=" * 60)
        print("  💡 TIPS FOR PLAYBACK:")
        print("     • VLC: Press [ or ] for slow/fast speed")
        print("     • VLC: Press E for frame-by-frame")
        print("     • VLC: Press SPACE to pause")
        print("     • VLC: Use scroll to seek")
        print("     • Windows Media Player: Use slider for seek")
        print("=" * 60)
        
        # Open with default player
        try:
            os.startfile(merged_path)
            print(f"\n✅ Video opened! File saved at:\n   {merged_path}")
            return True
        except Exception as e:
            print(f"\n❌ Failed to open video: {e}")
            print(f"   You can manually open: {merged_path}")
            return False


def play_video_sequence(video_paths: list, window_name: str = "Sign Language Player", use_merged: bool = True) -> bool:
    """
    Play a sequence of sign language videos.
    
    By default, creates a single merged video file for seamless playback with
    your default video player (VLC recommended for best controls).
    
    Args:
        video_paths: List of video file paths to play in sequence
        window_name: Name for the window (used for OpenCV mode)
        use_merged: If True (default), merge videos and play with system player.
                   If False, try OpenCV display (may fail in some environments).
        
    Returns:
        True if playback completed, False on error
    """
    # Create player instance
    player = SignVideoPlayer(video_paths, window_name)
    
    # Load all frames
    if not player.load_frames():
        return False
    
    # Use merged video mode by default (works everywhere)
    if use_merged:
        return player.play_merged_video()
    
    # Otherwise try OpenCV display
    return player.play()


# ============================================================
# INTERACTIVE MODE
# ============================================================

def main():
    """Run interactive text-to-sign translator with video playback."""
    print("\n" + "=" * 60)
    print("🤟 TEXT-TO-SIGN LANGUAGE TRANSLATOR")
    print("=" * 60)
    
    # Load and display vocabulary stats
    try:
        vocab = load_vocabulary()
        print(f"\n✅ Loaded vocabulary: {len(vocab)} signs available")
        print(f"📁 Video directory: {VIDEO_DIR}")
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return
    
    print("\n📝 Enter text to translate (or 'quit' to exit)")
    print("   After translation, videos will play automatically!")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n🎤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            print("\n⏳ Translating...")
            result = text_to_sign(user_input)
            display_result(result)
            
            # Play videos if translation was successful
            if "error" not in result and result.get("video_sequence"):
                play_choice = input("\n▶️  Play videos? (Y/n): ").strip().lower()
                if play_choice != 'n':
                    play_video_sequence(result["video_sequence"])
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
