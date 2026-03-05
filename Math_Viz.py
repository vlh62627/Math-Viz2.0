import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, ImageEnhance, ImageFilter
import datetime
import io

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="VizAI Math Engine V4",
    page_icon="📐",
    layout="wide"
)

# -------------------------------
# CSS & KaTeX Rendering
# -------------------------------
st.markdown("""
<style>
.main{background:#f9fafc;}
.math-header{color:#1E3A8A;font-size:40px;font-weight:700;margin-bottom:0px;}
.attribution{color:#666;font-size:0.95rem;}
.result-card{background:white;padding:25px;border-radius:12px;border:1px solid #e3e3e3;box-shadow:0px 4px 12px rgba(0,0,0,0.06);margin-top:10px;}
.solve-btn button{background:#1E3A8A;color:white;font-weight:bold;border-radius:10px;height:3.5em;width:100%;}
.katex{font-size:1.2rem; line-height:1.5;}
</style>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.4/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.4/dist/contrib/auto-render.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
  renderMathInElement(document.body);
});
</script>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<div class='math-header'>📐 VizAI Math Engine V4</div>", unsafe_allow_html=True)
st.markdown("<div class='attribution'>Handwritten & Typed Math Solver • Developed by Vijay</div>", unsafe_allow_html=True)

# -------------------------------
# SESSION STATE
# -------------------------------
if "version" not in st.session_state: st.session_state.version=0
if "mode" not in st.session_state: st.session_state.mode="input"
if "history" not in st.session_state: st.session_state.history=[]
if "answer" not in st.session_state: st.session_state.answer=""

# -------------------------------
# RESET FUNCTION
# -------------------------------
def reset_app():
    st.session_state.version += 1
    st.session_state.mode = "input"
    st.session_state.answer=""
    for key in list(st.session_state.keys()):
        if key.startswith("text_") or key.startswith("upload_") or key.startswith("cam_"):
            del st.session_state[key]

# -------------------------------
# GEMINI CLIENT
# -------------------------------
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# -------------------------------
# SIDEBAR HISTORY
# -------------------------------
with st.sidebar:
    st.header("📚 Solution History")
    if len(st.session_state.history)==0:
        st.caption("No solutions yet")
    for item in st.session_state.history[::-1]:
        with st.expander(item["time"]):
            st.write("**Problem**")
            st.write(item["problem"])
            st.write("**Answer**")
            st.markdown(f"<div class='katex'>{item['answer']}</div>", unsafe_allow_html=True)

# -------------------------------
# MODEL OPTIONS
# -------------------------------
st.divider()
col1,col2 = st.columns(2)
with col1:
    model_choice = st.selectbox(
        "🧠 AI Reasoning Engine",
        ["gemma-3-27b-it","gemini-2.0-flash-lite","gemini-2.0-flash"]
    )
with col2:
    complexity = st.select_slider(
        "Explanation Detail",
        ["Brief","Standard","Comprehensive"],
        value="Standard"
    )

# -------------------------------
# INPUT SECTION
# -------------------------------
st.subheader("Provide Math Problem")
text_key = f"text_{st.session_state.version}"
upload_key = f"upload_{st.session_state.version}"
cam_key = f"cam_{st.session_state.version}"

has_img = (st.session_state.get(upload_key) is not None) or (st.session_state.get(cam_key) is not None)
has_text = st.session_state.get(text_key,"").strip() != ""

typed_problem = st.text_area(
    "Type problem",
    placeholder="Example: integrate x^2 dx",
    key=text_key,
    disabled=has_img
)

st.markdown("### OR")
tab1,tab2 = st.tabs(["Upload Image","Take Photo"])
with tab1:
    uploaded = st.file_uploader(
        "Upload math photo",
        type=["png","jpg","jpeg"],
        key=upload_key,
        disabled=has_text
    )
with tab2:
    camera = st.camera_input(
        "Take photo",
        key=cam_key,
        disabled=has_text
    )
source = camera if camera else uploaded

# -------------------------------
# IMAGE PREPROCESSING (Handwriting Ready)
# -------------------------------
def preprocess(img):
    img = img.convert("L")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    img = img.filter(ImageFilter.SHARPEN)
    img.thumbnail((1024,1024))
    return img

content=[]
problem_text=""
if source and not has_text:
    img = Image.open(source)
    img = preprocess(img)
    st.image(img,width=220)
    st.caption("Problem Loaded from Image")
    
    # Convert PIL image to bytes for Gemini
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    content.append(img_bytes)
    
    problem_text="Image Problem"
elif typed_problem and not has_img:
    content.append(f"TEXT PROBLEM: {typed_problem}")
    problem_text=typed_problem

# -------------------------------
# SOLVE (STREAMING)
# -------------------------------
if content:
    if st.button("🚀 Solve"):
        st.session_state.mode="result"
        st.session_state.answer=""

        with st.spinner("AI solving..."):
            try:
                prompt = f"""
You are an elite mathematics reasoning engine capable of handwritten and typed problems.

PROCESS:
1. Detect math domain.
2. Validate symbols.
3. Solve step-by-step.
4. Verify results.

OUTPUT:
- Simple arithmetic → only final result
- Complex → ## Problem Identification ## Step Derivation ## Final Answer (LaTeX)
Explanation depth: {complexity}
"""

                if "gemini" in model_choice:
                    response = client.models.generate_content(
                        model=model_choice,
                        config=types.GenerateContentConfig(
                            system_instruction=prompt
                        ),
                        contents=content
                    )
                else:
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=[prompt]+content
                    )

                answer = response.text
                st.session_state.answer=answer
                st.session_state.history.append({
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "problem": problem_text,
                    "answer": answer
                })
            except Exception as e:
                st.error(e)

# -------------------------------
# RESULT DISPLAY
# -------------------------------
if st.session_state.mode=="result":
    st.divider()
    st.subheader("Solution")
    
    # Only text/LaTeX in result card
    st.markdown(f"<div class='result-card'><div class='katex'>{st.session_state.answer}</div></div>", unsafe_allow_html=True)
    
    with st.expander("📖 Expand Solution Steps"):
        st.markdown(f"<div class='katex'>{st.session_state.answer}</div>", unsafe_allow_html=True)
    
    st.download_button(
        "📥 Download Solution",
        st.session_state.answer,
        file_name="solution.txt"
    )
    
    st.button("🔄 Solve Another Problem", on_click=reset_app)
else:
    st.info("Enter a math problem or upload an image to begin.")

# -------------------------------
# FOOTER
# -------------------------------
st.divider()
st.caption(f"Engine running: {model_choice}")
