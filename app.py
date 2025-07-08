import streamlit as st
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# Set page config
st.set_page_config(
    page_title="AgriScan Plant Doctor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a2f1a 0%, #3d6b3d 100%);
        color: #fff;
    }
    h1, h2, h3 {
        color: #d4f0d4 !important;
    }
    .block-container {
        background: rgba(0, 20, 0, 0.85);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(to bottom, #4CAF50, #2E7D32) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        padding: 10px 24px !important;
    }
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 15px;
        padding: 10px;
        border-radius: 10px;
        background: rgba(0, 30, 0, 0.7);
    }
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    .results-card {
        background: rgba(30, 58, 30, 0.7);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        animation: fadeIn 0.5s ease;
    }
    .disease-name {
        font-size: 1.5rem;
        color: #ffcc66;
        margin-bottom: 5px;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .image-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin-top: 20px;
    }
    .sample-img {
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Disease data
CLASS_NAMES = [
    "Tomato Bacterial Spot",
    "Tomato Early Blight",
    "Tomato Late Blight",
    "Tomato Leaf Mold",
    "Tomato Septoria Leaf Spot",
    "Tomato Spider Mites",
    "Tomato Target Spot",
    "Tomato Yellow Leaf Curl Virus",
    "Tomato Mosaic Virus",
    "Healthy Tomato"
]

SAMPLE_IMAGES = {
    "Early Blight": "https://github.com/ravirajsinh45/plant_disease_dataset/raw/master/tomato/Tomato_Early_blight.JPG",
    "Late Blight": "https://github.com/ravirajsinh45/plant_disease_dataset/raw/master/tomato/Tomato_Late_blight.JPG",
    "Healthy": "https://github.com/ravirajsinh45/plant_disease_dataset/raw/master/tomato/Healthy.JPG"
}

# Mock disease detection
def detect_disease(image):
    diseases = CLASS_NAMES.copy()
    np.random.shuffle(diseases)
    confidences = np.random.rand(len(CLASS_NAMES))
    confidences = confidences / confidences.sum()
    top_indices = np.argsort(confidences)[::-1][:3]
    results = []
    for idx in top_indices:
        results.append({
            "disease": CLASS_NAMES[idx],
            "confidence": confidences[idx]
        })
    return results

# Treatment recommendations
def get_treatments(disease_name):
    treatments = []
    if "Healthy" in disease_name:
        treatments = [
            "Continue regular monitoring",
            "Apply balanced NPK fertilizer",
            "Maintain proper watering schedule"
        ]
    elif "Early Blight" in disease_name:
        treatments = [
            "Remove infected leaves immediately",
            "Apply copper-based fungicide weekly"
        ]
    elif "Late Blight" in disease_name:
        treatments = [
            "Apply chlorothalonil immediately",
            "Destroy severely infected plants"
        ]
    else:
        treatments = [
            "Apply neem oil spray every 7 days",
            "Remove affected plant parts"
        ]
    return treatments

# Main app
def main():
    if "camera_active" not in st.session_state:
        st.session_state.camera_active = False
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "results" not in st.session_state:
        st.session_state.results = None
    
    st.title("🌱 AgriScan Plant Doctor")
    st.subheader("Detect plant diseases and get treatment recommendations")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📷 Scan Plant Leaf")
        cam_option = st.radio("Select input method:", 
                             ["Use Camera", "Upload Image", "Use Sample"], 
                             index=0, horizontal=True)
        
        if cam_option == "Use Camera":
            st.session_state.camera_active = True
            st.session_state.results = None
            
            ctx = webrtc_streamer(
                key="example",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                video_frame_callback=None,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
            )
            
            if ctx.video_receiver and st.button("🌿 Capture Leaf", use_container_width=True):
                st.session_state.processing = True
                with st.spinner("Analyzing leaf..."):
                    time.sleep(2)
                    st.session_state.results = detect_disease(None)
                    st.session_state.processing = False
                    st.session_state.camera_active = False
                    st.experimental_rerun()
        
        elif cam_option == "Upload Image":
            uploaded_file = st.file_uploader("Upload a plant leaf image", 
                                           type=["jpg", "jpeg", "png"])
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Leaf", use_column_width=True)
                
                if st.button("🔍 Analyze Image", use_container_width=True):
                    st.session_state.processing = True
                    with st.spinner("Analyzing leaf..."):
                        time.sleep(2)
                        st.session_state.results = detect_disease(image)
                        st.session_state.processing = False
                        st.experimental_rerun()
        
        elif cam_option == "Use Sample":
            st.markdown("### Sample Images")
            cols = st.columns(3)
            for i, (name, url) in enumerate(SAMPLE_IMAGES.items()):
                with cols[i]:
                    st.image(url, caption=name, use_column_width=True)
            
            cols = st.columns(3)
            with cols[0]:
                if st.button("Test Early Blight", use_container_width=True):
                    st.session_state.results = [{
                        "disease": "Tomato Early Blight",
                        "confidence": 0.92
                    }]
            with cols[1]:
                if st.button("Test Late Blight", use_container_width=True):
                    st.session_state.results = [{
                        "disease": "Tomato Late Blight",
                        "confidence": 0.88
                    }]
            with cols[2]:
                if st.button("Test Healthy Leaf", use_container_width=True):
                    st.session_state.results = [{
                        "disease": "Healthy Tomato",
                        "confidence": 0.95
                    }]
        
        status_dot_color = "#ff9800"
        status_text = "Ready to scan"
        if st.session_state.processing:
            status_dot_color = "#FFC107"
            status_text = "Analyzing leaf..."
        elif st.session_state.camera_active:
            status_dot_color = "#4CAF50"
            status_text = "Camera active - ready to scan"
        
        st.markdown(
            f"""
            <div class="status-indicator">
                <div class="status-dot" style="background: {status_dot_color};"></div>
                <span>{status_text}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        if st.session_state.results:
            st.markdown("### 🔍 Diagnosis Results")
            primary_disease = st.session_state.results[0]["disease"]
            confidence = st.session_state.results[0]["confidence"]
            
            st.markdown(
                f"""
                <div class="results-card">
                    <div class="disease-name">{primary_disease}</div>
                    <div class="confidence">Confidence: {(confidence * 100):.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            treatments = get_treatments(primary_disease)
            st.markdown("#### 💊 Treatment Recommendations")
            st.markdown("\n".join([f"- {t}" for t in treatments]))
            
            st.markdown("#### 🌱 Prevention Tips")
            st.markdown("""
            - Rotate crops annually
            - Water early in the day
            - Inspect plants weekly
            - Sterilize tools after use
            """)
            
            if st.button("🔄 New Scan", use_container_width=True):
                st.session_state.results = None
                st.session_state.camera_active = False
                st.session_state.processing = False
                st.experimental_rerun()
        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 50px; opacity: 0.7;">
                <h3>Waiting for Scan Results</h3>
                <div style="font-size: 5rem; margin: 20px;">🌿</div>
                <p>Results will appear here after analysis</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #aaa;'>"
        "AgriScan - AI-powered Plant Health Assistant | Demo v1.0"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
