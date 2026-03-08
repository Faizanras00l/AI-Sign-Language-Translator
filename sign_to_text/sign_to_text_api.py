"""
Sign-to-Text API Module
========================
Flask API integration for ASL sign language recognition.
Bridges the frontend (page2.html) with the I3D model (live_demo_fixed.py).
"""

import os
import sys
import cv2
import torch
import torch.nn.functional as F
import numpy as np
import json
import base64
from pathlib import Path

# Add sign to text directory to path
SCRIPT_DIR = Path(__file__).parent
SIGN_TO_TEXT_DIR = SCRIPT_DIR  # We are already inside sign_to_text/ now
sys.path.insert(0, str(SIGN_TO_TEXT_DIR))

# Import from pytorch files
from pytorch_i3d import InceptionI3d
from videotransforms import CenterCrop

# ============================================================================
# Configuration
# ============================================================================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = SIGN_TO_TEXT_DIR / "asl_model_weights.pt"
DICTIONARY_PATH = SIGN_TO_TEXT_DIR / "nslt_2000.json"
WLASL_PATH = SIGN_TO_TEXT_DIR / "WLASL_v0.3.json"

# Model parameters
NUM_CLASSES = 2000
NUM_FRAMES = 32  # Temporal depth for I3D
TOP_K = 3
MIN_CONFIDENCE = 3.0  # Minimum confidence percentage

# Global model instance (loaded once at startup)
_model = None
_class_names = None

# ============================================================================
# Model Loading
# ============================================================================
def load_model():
    """Load the Inception I3D model with pretrained weights."""
    global _model
    
    if _model is not None:
        return _model
    
    print(f"[Sign2Text] Loading model from {MODEL_PATH}...")
    
    _model = InceptionI3d(num_classes=NUM_CLASSES, in_channels=3)
    _model = _model.to(DEVICE)
    
    if MODEL_PATH.exists():
        checkpoint = torch.load(str(MODEL_PATH), map_location=DEVICE)
        _model.load_state_dict(checkpoint)
        print(f"[Sign2Text] ✓ Model weights loaded successfully")
    else:
        print(f"[Sign2Text] ⚠ Warning: Model file not found at {MODEL_PATH}")
        print("[Sign2Text]   Using randomly initialized weights")
    
    _model.eval()
    return _model


def load_dictionary():
    """Load the NSLT-2000 dictionary mapping class IDs to sign names."""
    global _class_names
    
    if _class_names is not None:
        return _class_names
    
    print(f"[Sign2Text] Loading dictionary from {DICTIONARY_PATH}...")
    
    _class_names = {}
    if WLASL_PATH.exists():
        try:
            with open(WLASL_PATH, 'r', encoding='utf-8') as f:
                wlasl_data = json.load(f)
            
            # WLASL_v0.3.json is an array where index = class_id
            for idx, item in enumerate(wlasl_data):
                if 'gloss' in item:
                    _class_names[idx] = item['gloss']
            
            print(f"[Sign2Text] ✓ Loaded {len(_class_names)} sign names from WLASL_v0.3.json")
        except Exception as e:
            print(f"[Sign2Text] ⚠ Could not load WLASL metadata: {e}")
    
    # Fallback: use generic names if no mapping found
    if not _class_names:
        _class_names = {i: f"Sign_{i}" for i in range(NUM_CLASSES)}
    
    return _class_names


def initialize():
    """Initialize model and dictionary. Call this at Flask startup."""
    print("\n" + "=" * 60)
    print("  Initializing Sign-to-Text Backend")
    print("=" * 60)
    
    model = load_model()
    class_names = load_dictionary()
    
    print(f"[Sign2Text] Device: {DEVICE}")
    print(f"[Sign2Text] Model classes: {NUM_CLASSES}")
    print(f"[Sign2Text] Dictionary entries: {len(class_names)}")
    print("=" * 60 + "\n")
    
    return model, class_names


# ============================================================================
# Frame Processing
# ============================================================================
def preprocess_frames(frames, target_size=224):
    """
    Convert list of frames to model-ready tensor.
    
    Input: List of T frames, each H x W x 3 (uint8, BGR or RGB)
    Output: Tensor of shape (1, 3, T, 224, 224) - normalized, channels-first
    """
    video_np = np.array(frames, dtype=np.float32)
    video_np = video_np / 255.0
    
    cropper = CenterCrop(target_size)
    video_np = cropper(video_np)
    
    video_tensor = torch.from_numpy(video_np)
    video_tensor = video_tensor.permute(0, 3, 1, 2)
    video_tensor = video_tensor.unsqueeze(0)
    video_tensor = video_tensor.permute(0, 2, 1, 3, 4)
    
    return video_tensor


def pad_or_truncate_frames(frames, target_length=NUM_FRAMES):
    """Ensure frames list has exactly target_length frames."""
    if len(frames) < target_length:
        # Repeat last frame to pad
        padded = frames + [frames[-1]] * (target_length - len(frames))
    else:
        # Take last target_length frames
        padded = frames[-target_length:]
    return padded


def decode_base64_frame(base64_string):
    """
    Decode base64 image string to numpy array.
    
    Input: "data:image/jpeg;base64,/9j/4AAQ..." or just base64 data
    Output: numpy array (H, W, 3) in BGR format
    """
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',', 1)[1]
    
    # Decode base64 to bytes
    img_bytes = base64.b64decode(base64_string)
    
    # Convert bytes to numpy array
    nparr = np.frombuffer(img_bytes, np.uint8)
    
    # Decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    return img


# ============================================================================
# Inference
# ============================================================================
def get_top_predictions(video_tensor, top_k=TOP_K):
    """
    Run model inference and get top-k predictions with confidence scores.
    
    Returns:
        List of tuples: (sign_name, confidence_score)
    """
    model = load_model()
    class_names = load_dictionary()
    
    with torch.no_grad():
        video_tensor = video_tensor.to(DEVICE)
        logits = model(video_tensor)
        logits = logits.mean(dim=2)
        probs = F.softmax(logits, dim=1)
        top_probs, top_indices = torch.topk(probs, top_k, dim=1)
        top_probs = top_probs[0].cpu().numpy()
        top_indices = top_indices[0].cpu().numpy()
    
    predictions = []
    for idx, prob in zip(top_indices, top_probs):
        idx = int(idx)
        sign_name = class_names.get(idx, f"Sign_{idx}")
        confidence = float(prob) * 100
        predictions.append((sign_name, confidence))
    
    return predictions


# ============================================================================
# Public API Functions (called from Flask routes)
# ============================================================================
def analyze_frames(base64_frames):
    """
    Analyze a sequence of frames from webcam.
    
    Args:
        base64_frames: List of base64-encoded image strings
    
    Returns:
        dict with predictions, top_sign, and confidence
    """
    try:
        # Decode all frames
        frames = []
        for b64_frame in base64_frames:
            frame = decode_base64_frame(b64_frame)
            if frame is None:
                raise ValueError("Failed to decode frame")
            frames.append(frame)
        
        # Ensure we have exactly NUM_FRAMES
        if len(frames) < 8:
            return {
                'success': False,
                'error': f'Not enough frames. Need at least 8, got {len(frames)}'
            }
        
        frames = pad_or_truncate_frames(frames, NUM_FRAMES)
        
        # Preprocess and run inference
        video_tensor = preprocess_frames(frames)
        predictions = get_top_predictions(video_tensor)
        
        # Format response
        predictions_list = [
            {'sign': sign, 'confidence': round(conf, 2)}
            for sign, conf in predictions
        ]
        
        top_sign, top_confidence = predictions[0] if predictions else (None, 0)
        
        return {
            'success': True,
            'predictions': predictions_list,
            'top_sign': top_sign,
            'confidence': round(top_confidence, 2),
            'frames_analyzed': len(frames)
        }
    
    except Exception as e:
        print(f"[Sign2Text] Error in analyze_frames: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def analyze_video_file(video_path):
    """
    Analyze a video file and detect all signs in it.
    
    Args:
        video_path: Path to video file
    
    Returns:
        dict with detected_signs, translation, and metadata
    """
    try:
        if not os.path.exists(video_path):
            return {
                'success': False,
                'error': f'Video file not found: {video_path}'
            }
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {
                'success': False,
                'error': 'Could not open video file'
            }
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / video_fps if video_fps > 0 else 0
        
        print(f"[Sign2Text] Processing video: {total_frames} frames, {video_fps:.2f} fps, {duration:.2f}s")
        
        # Read all frames
        all_frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            all_frames.append(frame)
        cap.release()
        
        if len(all_frames) < NUM_FRAMES:
            if len(all_frames) < 8:
                return {
                    'success': False,
                    'error': f'Video too short ({len(all_frames)} frames). Need at least 8 frames.'
                }
            # Pad short video
            all_frames = pad_or_truncate_frames(all_frames, NUM_FRAMES)
        
        # Process with sliding window
        stride = NUM_FRAMES // 2
        detected_signs = []
        last_prediction = None
        segment_count = 0
        
        for start_idx in range(0, len(all_frames) - NUM_FRAMES + 1, stride):
            segment_count += 1
            end_idx = start_idx + NUM_FRAMES
            segment_frames = all_frames[start_idx:end_idx]
            
            # Calculate timestamp
            timestamp = start_idx / video_fps if video_fps > 0 else start_idx / 30
            
            try:
                video_tensor = preprocess_frames(segment_frames)
                predictions = get_top_predictions(video_tensor)
                
                if predictions and predictions[0][1] >= MIN_CONFIDENCE:
                    top_sign, confidence = predictions[0]
                    
                    # Only add if different from last prediction (avoid duplicates)
                    if top_sign != last_prediction:
                        detected_signs.append({
                            'sign': top_sign,
                            'confidence': round(confidence, 2),
                            'timestamp': round(timestamp, 2),
                            'segment': segment_count
                        })
                        last_prediction = top_sign
            except Exception as e:
                print(f"[Sign2Text] Warning: Error processing segment {segment_count}: {e}")
        
        # Build translation sentence
        translation = " ".join([s['sign'] for s in detected_signs]) if detected_signs else ""
        
        return {
            'success': True,
            'detected_signs': detected_signs,
            'translation': translation,
            'video_duration': round(duration, 2),
            'total_segments': segment_count,
            'total_frames': total_frames
        }
    
    except Exception as e:
        print(f"[Sign2Text] Error in analyze_video_file: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }
