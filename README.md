<div align="center">
  
# 🌐 Signed VISION: A Complete ASL Interactive & Accessibility Platform

*An advanced, multi-modal web application designed to bridge the communication gap between the Deaf and hearing communities through real-time AI computer vision, extensive dataset sequencing, and large language models.*

---
</div>

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Core Architecture & Folder Structure](#-core-architecture--folder-structure)
3. [Module Analysis: Detailed Breakdown](#-module-analysis-detailed-breakdown)
   - [A. Main Web Server (Working)](#a-main-web-server-working)
   - [B. Text-to-Sign Module (Working)](#b-text-to-sign-module-working)
   - [C. Sign-to-Text Module (Working & Experimental)](#c-sign-to-text-module-working--experimental)
   - [D. AI Chatbot Assistant (Working)](#d-ai-chatbot-assistant-working)
4. [Dataset & Data Engineering (Text-to-Sign)](#-dataset--data-engineering-text-to-sign)
5. [Neural Network Weights & Models](#-neural-network-weights--models)
6. [Experimental vs. Production Files](#-experimental-vs-production-files)
7. [Installation & Setup Guide](#-installation--setup-guide)
8. [GitHub Deployment Strategy](#-github-deployment-strategy)
9. [Troubleshooting & FAQ](#-troubleshooting--faq)
10. [Future Scope](#-future-scope)

---

## 🎯 1. Project Overview

**Signed VISION** is a comprehensive, full-stack application that provides bi-directional sign language translation and intelligent accessibility support. The core objective of this project is to create an intuitive, locally-run web interface capable of understanding human gestures (Sign-to-Text), translating written English into high-quality ASL video sequences (Text-to-Sign), and providing contextual AI assistance (Chatbot).

By utilizing deep learning algorithms (specifically 3D Convolutional Neural Networks), massive curated video datasets, and modern web frameworks, Signed VISION stands as a robust platform for both ASL learners and individuals relying on ASL as their primary mode of communication.

---

## 🏗️ 2. Core Architecture & Folder Structure

To ensure maximum compatibility, this repository maintains its original, explicit folder structure. This allows researchers and developers to easily identify the historical progression of the modules. 

```text
WLASL Complete/Complete Full stack/
│
├── app.py                      # Main Flask application (Routing & API integration)
├── index.html                  # Landing page
├── home.html                   # Secondary landing/portal
├── page2.html                  # Interface: Sign-to-Text Web UI
├── page3.html                  # Interface: Text-to-Sign Web UI
├── page4.html                  # Interface: AI Chatbot Web UI
│
├── assets/                     # Global static assets (Images, icons, logos)
├── css/                        # Global Cascading Style Sheets
├── js/                         # Global JavaScript files for frontend logic
│
├── home page/                  # [Experimental/Deprecated] Old homepage iterations
│
├── sign to text/               # MODULE 1: Computer Vision & ASL Recognition
│   ├── asl_model_weights.pt    # Critical: 57MB PyTorch 3D-CNN Model Weights
│   ├── sign_to_text_api.py     # Production API logic for gesture recognition
│   ├── pytorch_i3d.py          # Network architecture definition (I3D Model)
│   ├── videotransforms.py      # Spatial/Temporal video transformations
│   ├── live_demo_fixed.py      # [Experimental] OpenCV live webcam loop test script
│   ├── WLASL_v0.3.json         # Dataset annotations for retraining (11MB)
│   └── nslt_2000.json          # Subset annotations for testing
│
├── text to sign/               # MODULE 2: English to ASL Video Translation
│   ├── text_to_sign.py         # Production API logic for sequencing videos
│   └── WLASL_Processed_Videos/ # Critical: ~2000 MP4 ASL demonstration videos
│       ├── _web_cache/         # Auto-generated H.264 cached versions
│       └── [word].mp4          # Individual sign files (e.g., hello_27172.mp4)
│
└── chat bot/                   # MODULE 3: LLM Integration
    ├── chatbot.py              # Production API logic for OpenRouter LLM
    └── processed_index.json    # Vocabulary index used by the LLM for context
```

---

## 🔍 3. Module Analysis: Detailed Breakdown

The platform operates via a centralized Flask server that routes requests to dedicated Python backend modules. Here is a detailed analysis of how each component functions.

### A. Main Web Server (Working)
**Location:** `/app.py`

This is the orchestration layer of the application. It serves the raw HTML, CSS, and JS files directly from the root structure to the browser while simultaneously exposing RESTful API endpoints. 
- **Routes Hosted:** `/` (index), `/<filename>`, `/css/*`, `/js/*`, `/assets/*`.
- **API Endpoints:**
  - `POST /api/translate`: Accepts English text, parses it, and returns a sequenced list of MP4 paths using the `text to sign` logic.
  - `POST /api/sign-to-text/analyze-video`: Accepts a video upload, triggers the PyTorch I3D model, and returns confidence scores and translations.
  - `POST /api/chat`: Handles interaction with the Mistral LLM.
- **Dynamic Optimization:** The server includes an on-the-fly (`/videos/<filename>`) FFmpeg conversion route that caches `.mp4` files into browser-friendly H.264 format, preventing video format playback issues in modern browsers (Chrome/Safari/Edge).

### B. Text-to-Sign Module (Working)
**Location:** `/text to sign/text_to_sign.py`

This module solves the complex problem of translating written English into a coherent sequence of ASL videos. 
1. **NLP Processing:** The user's input text is gathered and normalized (converted to uppercase, stripped of complex punctuation).
2. **Tokenization & Stop Words:** The system breaks the sentence into individual words (tokens) and strips away English-specific filler words (like "the", "a", "is") that do not have direct 1:1 translations in conceptual ASL syntax.
3. **Fuzzy Matching:** Sometimes users type "talking", but the dataset only has "talk". The algorithm uses sophisticated stemming and lemma approximation along with an internal dictionary to find the closest match.
4. **Sequence Assembly:** Once the tokens are matched to the internal vocabulary, the script queries the `WLASL_Processed_Videos` directory, concatenates the paths, and returns them to the frontend where they are seamlessly played back-to-back using JavaScript promises.

### C. Sign-to-Text Module (Working & Experimental)
**Location:** `/sign to text/sign_to_text_api.py`

This is the most computationally heavy portion of the application, relying on advanced Computer Vision techniques.
1. **The Model:** It utilizes an Inflated 3D ConvNet (I3D). Unlike 2D CNNs that only look at static images, the I3D model analyzes *spatial* dimensions (X, Y pixels) and the *temporal* dimension (Frames over Time). This is crucial for ASL, where motion vector is as important as hand shape.
2. **The Pipeline (`sign_to_text_api.py`):** 
   - A video file is received via the Flask API.
   - OpenCV (`cv2`) reads the video and extracts frames.
   - `videotransforms.py` crops, normalizes, and packages the frames into a 5-dimensional Tensor `[Batch, Channels, Time, Height, Width]`.
   - The tensor is pushed through the PyTorch model (`pytorch_i3d.py`) parameterized by `asl_model_weights.pt`.
   - The output is a Softmax probability distribution over 2000 possible classes (words).
3. **Experimental Script (`live_demo_fixed.py`):** This is a standalone `cv2` loop script used during development to test the model on a live webcam feed outside of the Flask ecosystem. While fully functional on machines with local webcams, it is bypassed in the final web architecture in favor of the API approach.

### D. AI Chatbot Assistant (Working)
**Location:** `/chat bot/chatbot.py`

To provide users with accessible help, the platform features a responsive AI.
1. **LLM Integration:** It uses the Mistral-7B-Instruct model (via the OpenRouter API) to generate human-like text.
2. **Context Injection:** When the server starts, it parses `processed_index.json` to load the exact 2000+ words the application can currently sign. 
3. **Prompt Engineering:** The backend constructs an invisible system prompt before the user's message, instructing the AI to act as an ASL tutor, explicitly injecting the loaded vocabulary, so the bot only promises to translate words it knows the system actually contains.

*(Note: API Keys have been stripped from this repository. You must provide your own in an `.env` file to use this module).*

---

## 🗄️ 4. Dataset & Data Engineering (Text-to-Sign)

The most robust part of the translation engine relies on a massive, curated video dataset.

### The WLASL Video Extraction Process
The `WLASL_Processed_Videos` directory contains approximately 2,000 `.mp4` files. Generating this repository required significant data engineering:
1. **Sourcing:** The original WLASL (Word-Level American Sign Language) dataset consists of continuous YouTube URLs and raw video drops containing thousands of varying resolutions and framerates.
2. **Sanitization:** We stripped all audio tracks to reduce filesize by ~40%, as audio is irrelevant for ASL gestures.
3. **Trimming:** Videos were trimmed down to the exact millisecond the gesture begins and ends, removing leading and trailing static frames.
4. **Resolution Normalization:** All files were scaled to a consistent, web-friendly resolution (e.g., 256x256 or 224x224 bounding boxes) and re-encoded using `libx264` for maximum browser compatibility.
5. **Naming Convention:** Files are specifically named `[word]_[unique_id].mp4` (e.g., `abandon_00010.mp4`). The backend script splits on the underscore to build its dynamic dictionary.

Due to its massive size (~600MB), this folder is tracked using **Git LFS** in this repository.

---

## 🧠 5. Neural Network Weights & Models: Deep Dive

To achieve robust real-time hand and body tracking necessary for American Sign Language recognition, Signed VISION implements a sophisticated deep learning pipeline.

### The I3D Architecture (Inflated 3D ConvNet)
The core of the gesture recognition engine lies in `pytorch_i3d.py`. 
- **Why I3D over ResNet?** Traditional 2D image classifiers (like ResNet or VGG) process single, static images. ASL, however, is deeply temporal. The sign for "Name" and "Weight" might look identical in a single freeze-frame but are distinguished entirely by their direction of movement. I3D "inflates" standard 2D convolutional kernels into 3D (X, Y, Time), allowing the network to inherently learn spatio-temporal features.
- **Layers & Parameters:** The model consists of multiple Inception blocks mapped across the temporal dimension. 

### The Weight File: `asl_model_weights.pt`
- **File Size**: ~57.4 MB
- **State Dict Structure**: This file does not contain the Python class for the model itself; rather, it contains the serialized PyTorch dictionary (`state_dict()`) mapping each layer name in `pytorch_i3d.py` to its corresponding trained Tensor.
- **Training Paradigm**: These weights were generated by training the model on the WLASL dataset over hundreds of epochs utilizing heavy data augmentation (random horizontal flips, color jitter, temporal scaling) to prevent overfitting on specific lighting conditions or skin tones.
- **Inference Mode**: During active web app usage (via `sign_to_text_api.py`), the model is loaded strictly in `.eval()` mode, freezing all dropout and batch normalization layers to ensure stable, predictable predictions.
- **Git LFS Requirement**: Due to the binary nature of `.pt` files and their large size, this file is tracked via Git Large File Storage. Attempting to manage this file via traditional Git will result in repository bloat and potential checkout corruption.

---

## 🗄️ 4. Dataset & Data Engineering (Text-to-Sign)

The translation capability of Signed VISION is powered by an extensively curated, locally hosted video dataset. The `text to sign/WLASL_Processed_Videos/` directory contains precisely 2,001 video files. 

### The Data Extraction Methodology
To create a seamless user experience, the raw WLASL dataset could not be used out-of-the-box. The data engineering pipeline involved several critical phases:

1. **URL Sourcing & Downloading**: The initial `WLASL_v0.3.json` file contained YouTube IDs and timestamps. A batch downloading script extracted the highest available resolution for thousands of words.
2. **Audio Stripping**: ASL is an inherently visual language. Audio tracks attached to the original videos consumed nearly 40% of the total file size without providing semantic value to the machine learning algorithms or the end user. FFmpeg was utilized to batch-strip all audio streams.
3. **Temporal Trimming**: A critical issue with the raw dataset was the presence of static "lead-in" and "fade-out" frames where the signer was simply standing. These frames confused temporal algorithms and made back-to-back sequenced playback look stuttered. Automated scripts trimmed the videos using the exact frame boundaries provided in the JSON annotations.
4. **Resolution Normalization**: To ensure consistent layout rendering in the `page3.html` web interface, all videos were re-encoded to a standardized bounding box ratio.
5. **H.264 Web Optimization**: Browsers (especially Safari on iOS) are notoriously strictly regulated regarding HTML5 `<video>` tag playback formats. All MP4s were aggressively compressed using `libx264` (Constant Rate Factor 23) to ensure fast buffering across varying network speeds. Furthermore, the `app.py` server contains a fallback `/videos/<path>` route that performs on-the-fly, lazy-loaded H.264 conversion into a `_web_cache/` directory if a browser rejects the raw format.
6. **Lexical Parsing Key**: The naming convention of the output files (e.g., `abandon_00010.mp4`) serves as the primary indexed database for the `text_to_sign.py` search algorithm. By parsing the filesystem natively, we bypass the need for a separate SQL or NoSQL database holding the vocabulary matrix, significantly reducing the deployment complexity of the application.

Because of the massive datasets and deep learning weights, standard `git clone` procedures will fail to capture the actual data files unless Git LFS is utilized.

### Prerequisites
- Python 3.9, 3.10, or 3.11 (Currently running 3.11)
- Git Large File Storage (Git LFS) installed on your OS.
- A functional GPU (CUDA) is highly recommended for PyTorch, though CPU inference will work (significantly slower).

### Step 1: Clone the Repository via LFS
Make sure you initialize LFS before cloning.
```bash
git lfs install
git clone https://github.com/your-username/Signed-VISION.git
cd "Signed-VISION/Complete Full stack"
```
*(Verify that `asl_model_weights.pt` is ~57MB, not a 1KB pointer file).*

### Step 2: Environment Setup
Create an isolated Python environment to prevent dependency clashes, especially with PyTorch.
```bash
python -m venv venv

# Windows Activation:
venv\Scripts\activate

# Mac/Linux Activation:
source venv/bin/activate
```

### Step 3: Install Dependencies
The `requirements.txt` contains critical packages like Flask, PyTorch, OpenCV, and imageio-ffmpeg.
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys
To use the Chatbot module, create an environment variable or a `.env` file in the root.
```bash
# Windows (CMD)
set OPENROUTER_API_KEY=your_actual_key_here

# Mac/Linux
export OPENROUTER_API_KEY="your_actual_key_here"
```

### Step 5: Boot the Server
```bash
python app.py
```
Navigate to `http://localhost:5000` in your web browser. 

---

## 🚀 8. GitHub Deployment Strategy

If you are a contributor pushing changes to this repository, you must follow the Phased Deployment strategy. Pushing 600MB of videos and weights in a single `git push` without LFS configuration will result in a hard GitHub rejection.

**The Phased Approach:**
1. **Initialize LFS Tracking:**
   `git lfs track "*.pt"`
   `git lfs track "*.mp4"`
2. **Phase 1 Commit:** Push all standard code, HTML, CSS, and Markdown files first.
3. **Phase 2 Commit:** Push the 57MB PyTorch weight file separately to ensure LFS handles the binary blob.
4. **Phase 3 Commit:** Push the `WLASL_Processed_Videos` directory containing the 2000+ MP4 files. This will trigger massive LFS bandwidth usage. Keep your computer awake during this process.

---

## ❓ 9. Troubleshooting & FAQ

**Q: The webapp works, but the sign-to-text video uploads fail with a "Size Mismatch" or "State Dict" error.**
A: Your `asl_model_weights.pt` is corrupted or is an LFS pointer. Run `git lfs pull` to download the actual 57MB file.

**Q: The text-to-sign videos are just loading forever in the browser.**
A: The Flask server uses FFmpeg to convert older MP4 files to H.264 on the fly the first time they are requested. Check the terminal running `app.py`. If you see "Converting video...", wait a moment. Subsequent loads will be instant from the `_web_cache` folder.

**Q: "ModuleNotFound: cv2" when running `app.py`.**
A: OpenCV is missing in your environment. Run `pip install opencv-python-headless` (headless is safer for Flask servers to avoid GUI conflicts).

---

## 🔭 10. Future Scope

While the current implementation of Signed VISION is highly functional, future roadmaps include:
- **WebRTC Implementation:** Migrating the experimental `live_demo_fixed.py` into a fully functioning WebRTC pipeline in `page2.html` so users can perform sign language directly into their browser webcam without uploading a file.
- **Expanded Dictionary:** Growing the Text-to-Sign database from 2,000 words to an ultimate goal of over 10,000 conversational concepts.
- **ASL Grammar Mapping:** Currently, Text-to-Sign translates English word-for-word (Signed Precise English). Future iterations will map English grammar syntax directly into true ASL temporal grammar structure (e.g., Object-Subject-Verb format).

---
<div align="center">
  <i>Developed for accessibility, research, and communication bridging.</i><br>
  <b>2026 Interactive Machine Learning Portfolio</b>
</div>
