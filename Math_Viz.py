import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="VizAI Math Engine", page_icon="📐", layout="centered")

# Custom CSS for the Laboratory look
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .math-header { color: #1E3A8A; font-family: 'Helvetica', sans-serif; margin-bottom: 0px; text-align: center; }
    .attribution { color: #555; text-align: center; font-size: 0.9rem; margin-bottom: 30px; }
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        height: 3.5em; 
        background-color: #1E3A8A; 
        color: white; 
        font-weight: bold;
        font-size: 1.1rem;
    }
    .result-box { background-color: #ffffff; padding: 25px; border-radius: 10px; border: 1px solid #ddd; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Header & Attribution
st.markdown("<h1 class='math-header'>📐 VizAI Math Engine</h1>", unsafe_allow_html=True)
st.markdown("<p class='attribution'>❤️ Developed by Vijay</p>", unsafe_allow_html=True)

# 3. Setup API Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 4. Engine Parameters
with st.expander("🛠️ Advanced Engine Settings"):
    col_a, col_b = st.columns(2)
    with col_a:
        model_choice = st.selectbox("LLM Model", ["gemini-2.0-flash-lite", "gemini-2.0-flash"])
    with col_b:
        complexity = st.select_slider("Reasoning Detail", options=["Brief", "Standard", "Comprehensive"], value="Standard")

st.write("---")

# 5. File Upload Section
st.subheader("1. Upload Problem")
uploaded_file = st.file_uploader("Upload an image (Handwritten or Printed)", type=["png", "jpg", "jpeg"])

# 6. Solving Process (Only triggered if file is uploaded)
if uploaded_file:
    # Preview image
    img = Image.open(uploaded_file)
    st.image(img, caption="Target Problem Loaded", use_container_width=True)
    
    st.write("") # Spacing
    
    # "Solve" Button appears here
    if st.button("🚀 Solve"):
        with st.spinner("Analyzing image and calculating..."):
            try:
                # Prompt Engineering for the Math Engine
                system_instructions = (
                    f"You are a mathematical reasoning engine. Provide a {complexity} solution. "
                    "Follow this structure:\n"
                    "## PROBLEM IDENTIFICATION\n"
                    "## THEOREMS & FORMULAS\n"
                    "## STEP-BY-STEP DERIVATION\n"
                    "## FINAL RESULT (in LaTeX)"
                )

                # API Call
                response = client.models.generate_content(
                    model=model_choice,
                    config=types.GenerateContentConfig(system_instruction=system_instructions),
                    contents=[img]
                )
                
                # Display Result
                st.markdown("---")
                st.subheader("2. Solution Report")
                st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Engine Error: {e}")
else:
    st.info("Please upload a problem image to unlock the Solve button.")

# 7. Technical Footer
st.markdown("---")
st.caption("Status: LLM Engine Ready | Multimodal Inference Active")