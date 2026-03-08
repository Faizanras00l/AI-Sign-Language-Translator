"""
Flask API Server for ASL Learning Platform
Connects the HTML/CSS/JS frontend to Python backends:
- page2.html -> sign_to_text_api.py (Sign-to-Text)
- page3.html -> text_to_sign.py (Text-to-Sign)
- page4.html -> chatbot.py (AI Chatbot)
"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS

# Add module folders to Python path
SCRIPT_DIR = Path(__file__).parent
TEXT_TO_SIGN_DIR = SCRIPT_DIR / "text_to_sign"
CHATBOT_DIR = SCRIPT_DIR / "chat_bot"
SIGN_TO_TEXT_DIR = SCRIPT_DIR / "sign_to_text"
sys.path.insert(0, str(TEXT_TO_SIGN_DIR))
sys.path.insert(0, str(CHATBOT_DIR))
sys.path.insert(0, str(SIGN_TO_TEXT_DIR))

# Import backend functions
from text_to_sign import text_to_sign, load_vocabulary
from chatbot import chat_response, load_vocabulary as load_chatbot_vocab
import sign_to_text_api  # Sign-to-text model API

# Flask app setup
app = Flask(__name__)

# Enable CORS for all routes - this prevents browser blocking requests
# Allows requests from file:// protocol, localhost, and any origin during development
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Path to the processed videos folder
VIDEO_DIR = TEXT_TO_SIGN_DIR / "WLASL_Processed_Videos"


# ============================================================
# STATIC FILE SERVING (HTML/CSS/JS)
# ============================================================

@app.route('/')
def index():
    """Serve the main index page."""
    return send_from_directory(SCRIPT_DIR / 'templates', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """
    Serve static files (HTML, CSS, JS) from the project directory.
    This allows accessing pages via http://localhost:5000/page3.html
    which avoids cross-origin issues with video loading.
    """
    # Define safe file extensions to serve
    safe_extensions = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf'}
    
    file_ext = os.path.splitext(filename)[1].lower()
    
    # Only serve files with safe extensions
    if file_ext in safe_extensions:
        if file_ext == '.html':
            file_path = SCRIPT_DIR / 'templates' / filename
            if file_path.exists():
                return send_from_directory(SCRIPT_DIR / 'templates', filename)
        else:
            file_path = SCRIPT_DIR / 'static' / filename
            if file_path.exists():
                return send_from_directory(SCRIPT_DIR / 'static', filename)
    
    return "File not found", 404


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files."""
    return send_from_directory(SCRIPT_DIR / 'static' / 'css', filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files."""
    return send_from_directory(SCRIPT_DIR / 'static' / 'js', filename)


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve asset files (images, etc)."""
    return send_from_directory(SCRIPT_DIR / 'static' / 'assets', filename)


# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running."""
    try:
        vocab = load_vocabulary()
        return jsonify({
            "status": "healthy",
            "message": "Text-to-Sign API is running",
            "vocabulary_size": len(vocab)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/translate', methods=['POST', 'OPTIONS'])
def translate_text():
    """
    Main translation endpoint.
    
    Request Body (JSON):
        {"text": "Hello World"}
    
    Response (JSON):
        {
            "success": true,
            "original_text": "Hello World",
            "normalized_text": "HELLO WORLD",
            "selected_tokens": ["HELLO", "WORLD"],
            "video_urls": ["/videos/hello_001.mp4", "/videos/world_002.mp4"],
            "suggestions": "Translation complete!"
        }
    """
    from datetime import datetime
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'text' field in request body"
            }), 400
        
        user_text = data['text'].strip()
        
        if not user_text:
            return jsonify({
                "success": False,
                "error": "Text cannot be empty"
            }), 400
        
        # ============================================================
        # ENHANCED TERMINAL LOGGING
        # ============================================================
        timestamp = datetime.now().strftime("%H:%M:%S")
        print("\n" + "=" * 60)
        print(f"🆕 NEW TRANSLATION REQUEST @ {timestamp}")
        print("=" * 60)
        print(f"📝 Input Text: \"{user_text}\"")
        print("-" * 60)
        
        # Call the translation function from text_to_sign.py
        result = text_to_sign(user_text)
        
        # Check for errors from the translation
        if "error" in result:
            print(f"❌ Translation Error: {result['error']}")
            print("=" * 60 + "\n")
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
        
        # Log translation details
        print(f"🔤 Normalized: \"{result.get('normalized_text', 'N/A')}\"")
        print(f"🎯 Tokens Found: {result.get('selected_tokens', [])}")
        
        if result.get('suggestions'):
            print(f"💡 Suggestions: {result.get('suggestions')}")
        
        # Convert absolute file paths to web-accessible URLs
        video_urls = []
        print("-" * 60)
        print("🎬 Videos to play:")
        
        for i, video_path in enumerate(result.get("video_sequence", []), 1):
            # Extract just the filename from the full path
            video_filename = os.path.basename(video_path)
            video_url = f"/videos/{video_filename}"
            video_urls.append(video_url)
            print(f"   {i}. {video_filename}")
        
        if not video_urls:
            print("   ⚠️  No matching videos found!")
        
        # Build success response
        response = {
            "success": True,
            "original_text": result.get("original_text", user_text),
            "normalized_text": result.get("normalized_text", ""),
            "selected_tokens": result.get("selected_tokens", []),
            "video_urls": video_urls,
            "suggestions": result.get("suggestions", "")
        }
        
        print("-" * 60)
        print(f"✅ SUCCESS: {len(video_urls)} video(s) ready for playback")
        print("=" * 60 + "\n")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Translation error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/videos/<path:filename>', methods=['GET'])
def serve_video(filename):
    """
    Serve video files with ON-DEMAND conversion to H.264 for browser compatibility.
    
    Flow:
    1. Check if H.264 version exists in cache
    2. If not, convert original to H.264 using FFmpeg
    3. Serve the H.264 version
    """
    import subprocess
    import imageio_ffmpeg
    
    # Paths
    original_video = VIDEO_DIR / filename
    cache_dir = VIDEO_DIR / "_web_cache"
    cached_video = cache_dir / filename
    
    # Create cache directory if it doesn't exist
    cache_dir.mkdir(exist_ok=True)
    
    # Check if original video exists
    if not original_video.exists():
        print(f"❌ Video not found: {original_video}")
        return jsonify({"error": f"Video not found: {filename}"}), 404
    
    # Check if cached (H.264) version exists
    if cached_video.exists():
        print(f"📦 Serving cached video: {filename}")
        return send_from_directory(cache_dir, filename, mimetype='video/mp4')
    
    # Convert to H.264 on-the-fly
    try:
        print(f"🔄 Converting video to H.264: {filename}")
        
        # Get path to bundled FFmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        # FFmpeg command for H.264 conversion (fast, web-compatible)
        cmd = [
            ffmpeg_path,
            '-y',                      # Overwrite output
            '-i', str(original_video), # Input file
            '-c:v', 'libx264',         # H.264 video codec
            '-preset', 'fast',         # Fast encoding
            '-crf', '23',              # Quality (lower = better, 23 is default)
            '-c:a', 'aac',             # AAC audio codec
            '-movflags', '+faststart', # Enable streaming
            str(cached_video)          # Output file
        ]
        
        # Run conversion
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            # Fall back to original video
            return send_from_directory(VIDEO_DIR, filename, mimetype='video/mp4')
        
        print(f"✅ Conversion complete: {filename}")
        return send_from_directory(cache_dir, filename, mimetype='video/mp4')
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ Conversion timeout for: {filename}")
        return send_from_directory(VIDEO_DIR, filename, mimetype='video/mp4')
    except Exception as e:
        print(f"❌ Conversion error: {str(e)}")
        return send_from_directory(VIDEO_DIR, filename, mimetype='video/mp4')


@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    """
    Return list of all available signs in the vocabulary.
    Useful for debugging or showing available words to user.
    """
    try:
        vocab = load_vocabulary()
        return jsonify({
            "success": True,
            "vocabulary": list(vocab.keys()),
            "count": len(vocab)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================
# SIGN-TO-TEXT API ENDPOINTS
# ============================================================

@app.route('/api/sign-to-text/analyze-webcam', methods=['POST', 'OPTIONS'])
def analyze_webcam():
    """
    Analyze frames from webcam for sign language recognition.
    
    Request Body (JSON):
        {
            "frames": ["data:image/jpeg;base64,...", ...],
            "timestamp": 1234567890
        }
    
    Response (JSON):
        {
            "success": true,
            "predictions": [
                {"sign": "HELLO", "confidence": 8.5},
                {"sign": "HI", "confidence": 4.2}
            ],
            "top_sign": "HELLO",
            "confidence": 8.5,
            "frames_analyzed": 32
        }
    """
    from datetime import datetime
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data or 'frames' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'frames' field in request body"
            }), 400
        
        frames = data['frames']
        
        if not isinstance(frames, list) or len(frames) == 0:
            return jsonify({
                "success": False,
                "error": "Frames must be a non-empty array"
            }), 400
        
        # Log request
        timestamp = datetime.now().strftime("%H:%M:%S")
        print("\n" + "=" * 60)
        print(f"📹 WEBCAM ANALYSIS REQUEST @ {timestamp}")
        print("=" * 60)
        print(f"📊 Frames received: {len(frames)}")
        print("-" * 60)
        
        # Call sign-to-text API
        result = sign_to_text_api.analyze_frames(frames)
        
        if result.get('success'):
            print(f"✅ Top prediction: {result.get('top_sign')} ({result.get('confidence')}%)")
            print(f"📋 All predictions: {result.get('predictions')}")
            print("=" * 60 + "\n")
        else:
            print(f"❌ Error: {result.get('error')}")
            print("=" * 60 + "\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Webcam analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/api/sign-to-text/analyze-video', methods=['POST', 'OPTIONS'])
def analyze_video():
    """
    Analyze uploaded video file for sign language recognition.
    
    Request: multipart/form-data with 'video' file
    
    Response (JSON):
        {
            "success": true,
            "detected_signs": [
                {"sign": "HELLO", "confidence": 9.2, "timestamp": 0.5, "segment": 1},
                {"sign": "FRIEND", "confidence": 5.8, "timestamp": 2.1, "segment": 3}
            ],
            "translation": "HELLO FRIEND",
            "video_duration": 4.5,
            "total_segments": 5
        }
    """
    from datetime import datetime
    import tempfile
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Check if video file is in request
        if 'video' not in request.files:
            return jsonify({
                "success": False,
                "error": "No video file provided"
            }), 400
        
        video_file = request.files['video']
        
        if video_file.filename == '':
            return jsonify({
                "success": False,
                "error": "Empty filename"
            }), 400
        
        # Log request
        timestamp = datetime.now().strftime("%H:%M:%S")
        print("\n" + "=" * 60)
        print(f"🎥 VIDEO UPLOAD ANALYSIS REQUEST @ {timestamp}")
        print("=" * 60)
        print(f"📁 Filename: {video_file.filename}")
        print(f"📊 Size: {len(video_file.read())} bytes")
        video_file.seek(0)  # Reset file pointer
        print("-" * 60)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_path = temp_file.name
            video_file.save(temp_path)
        
        print(f"💾 Saved to: {temp_path}")
        print("🔍 Analyzing video...")
        
        # Call sign-to-text API
        result = sign_to_text_api.analyze_video_file(temp_path)
        
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        if result.get('success'):
            print(f"✅ Detected {len(result.get('detected_signs', []))} signs")
            print(f"📝 Translation: {result.get('translation')}")
            print("=" * 60 + "\n")
        else:
            print(f"❌ Error: {result.get('error')}")
            print("=" * 60 + "\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Video analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


# ============================================================
# CHATBOT API ENDPOINTS
# ============================================================

# Store conversation histories (in-memory, per session)
chat_sessions = {}

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    """
    Chatbot endpoint for AI-powered conversations.
    
    Request Body (JSON):
        {
            "message": "Hello, what can you do?",
            "session_id": "optional-session-id"
        }
    
    Response (JSON):
        {
            "success": true,
            "response": "I am the ASL Learning Platform assistant...",
            "session_id": "abc123"
        }
    """
    from datetime import datetime
    import uuid
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'message' field in request body"
            }), 400
        
        user_message = data['message'].strip()
        session_id = data.get('session_id')
        
        # Generate session_id if not provided or null
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400
        
        # ============================================================
        # ENHANCED TERMINAL LOGGING
        # ============================================================
        timestamp = datetime.now().strftime("%H:%M:%S")
        print("\n" + "=" * 60)
        print(f"💬 NEW CHAT MESSAGE @ {timestamp}")
        print("=" * 60)
        print(f"📝 User: \"{user_message[:100]}{'...' if len(user_message) > 100 else ''}\"")
        print(f"🔑 Session: {session_id[:8] if session_id else 'NEW'}...")
        print("-" * 60)
        
        # Get conversation history for this session
        history = chat_sessions.get(session_id, [])
        
        # Call chatbot
        result = chat_response(user_message, history)
        
        # Defensive check - ensure result is a dict
        if result is None:
            print("❌ chat_response returned None!")
            result = {
                "success": False,
                "error": "Internal error: chatbot returned None",
                "response": "Sorry, I had an internal error. Please try again.",
                "history": history
            }
        
        if result.get('success'):
            # Update session history
            chat_sessions[session_id] = result['history']
            
            print(f"🤖 Bot: \"{result['response'][:100]}{'...' if len(result['response']) > 100 else ''}\"")
            print("-" * 60)
            print(f"✅ SUCCESS: Response sent")
            print("=" * 60 + "\n")
            
            return jsonify({
                "success": True,
                "response": result['response'],
                "session_id": session_id
            })
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            print("=" * 60 + "\n")
            
            return jsonify({
                "success": False,
                "error": result.get('error', 'Chat failed'),
                "response": result.get('response', 'Sorry, something went wrong.'),
                "session_id": session_id
            }), 500
            
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear conversation history for a session."""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    
    if session_id and session_id in chat_sessions:
        del chat_sessions[session_id]
        return jsonify({"success": True, "message": "Chat history cleared"})
    
    return jsonify({"success": True, "message": "No history to clear"})


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 ASL LEARNING PLATFORM - API SERVER")
    print("=" * 60)
    
    # Verify video directory exists
    if VIDEO_DIR.exists():
        video_count = len(list(VIDEO_DIR.glob("*.mp4")))
        print(f"✅ Video directory: {video_count} videos available")
    else:
        print(f"⚠️  Video directory not found")
    
    # Load vocabularies
    try:
        vocab = load_vocabulary()
        print(f"✅ Text-to-Sign vocabulary: {len(vocab)} signs")
    except Exception as e:
        print(f"❌ Failed to load vocabulary: {e}")
    
    try:
        chatbot_vocab = load_chatbot_vocab()
        print(f"✅ Chatbot vocabulary: {len(chatbot_vocab)} words")
    except Exception as e:
        print(f"❌ Failed to load chatbot vocab: {e}")
    
    # Initialize sign-to-text model
    try:
        print("\n" + "-" * 60)
        sign_to_text_api.initialize()
        print("-" * 60)
    except Exception as e:
        print(f"⚠️  Failed to load sign-to-text model: {e}")
        print("   Sign-to-text endpoints will be available but may error")
    
    print("\n" + "-" * 60)
    print("📡 API Endpoints:")
    print("   GET  /health                            - Check server status")
    print("   POST /api/translate                     - Text to sign videos")
    print("   POST /api/sign-to-text/analyze-webcam   - Webcam sign recognition")
    print("   POST /api/sign-to-text/analyze-video    - Video upload analysis")
    print("   POST /api/chat                          - AI Chatbot")
    print("   GET  /api/vocabulary                    - List available signs")
    print("   GET  /videos/<file>                     - Serve video files")
    print("-" * 60)
    print("\n🌐 Server starting on http://localhost:5000")
    print("   Press Ctrl+C to stop\n")
    
    # Run the Flask development server
    # host='0.0.0.0' allows access from any IP (useful for testing)
    # debug=True enables auto-reload on code changes
    app.run(host='0.0.0.0', port=5000, debug=True)
