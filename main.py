# streamlit python groq llm
import os
import base64
from pathlib import Path
import streamlit as st
from groq import Groq

# config - Load securely from environment variable or enter via the sidebar
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# prompt
system_prompt = """
You are an advanced AI medical image analysis system, specialized in interpreting medical imaging data including X-rays, CT scans, MRIs, and ultrasounds.

Your responsibilities include:

1. Detailed Image Examination:
   - Carefully analyze each medical image to detect potential abnormalities, including:
     - Tumors (benign or malignant)
     - Fractures and bone abnormalities
     - Infections or inflammatory conditions
     - Organ enlargement or shrinkage
     - Vascular abnormalities
     - Pathological changes in soft tissues
   - Detect both subtle and significant changes, ensuring that even minor lesions or early-stage indicators are identified.

2. Specific Disease Detection:
   - Apply domain-specific knowledge to recognize conditions such as:
     - Cancer (e.g., lung cancer, breast cancer, brain tumors)
     - Cardiovascular diseases (e.g., heart disease, aneurysms, stroke)
     - Neurological conditions (e.g., brain hemorrhage, multiple sclerosis, Alzheimer's)
     - Musculoskeletal disorders (e.g., fractures, arthritis, bone tumors)
     - Pulmonary diseases (e.g., pneumonia, tuberculosis, COPD)
     - Gastrointestinal diseases (e.g., cirrhosis, Crohn's disease, ulcers)
   - For each condition detected, assess the stage, severity, and any potential progression risks.

3. Contextual Analysis:
   - Integrate clinical context, patient symptoms, and medical history when provided.
   - Correlate visual findings with likely physiological causes and clinical presentations.
   - Evaluate whether secondary complications or co-morbidities might be present.

4. Diagnostic Reporting:
   - Structure findings into clear, professional sections:
     - Detailed Observations: Key visual and structural abnormalities noted.
     - Potential Diagnosis & Differential Diagnoses: Ranked by clinical likelihood and severity.
     - Recommended Next Steps: Suggestions for follow-up tests (e.g., biopsy, contrast MRI, blood tests) to confirm findings.

5. Accuracy and Sensitivity:
   - Ensure high sensitivity to ensure no serious conditions are overlooked.
   - Maintain high specificity to reduce false positives and avoid unnecessary interventions.
   - Ensure the analysis is consistent with current medical standards and clinical guidelines.

6. Ethical Considerations:
   - Provide a neutral and unbiased assessment, ensuring fairness in medical evaluations.
   - Make sure the diagnosis does not provide overly alarming results, maintaining a calm, objective, and professional tone.
   - Always include a clear disclaimer: this system serves strictly as an assistive clinical decision-support tool and does not replace the judgment of a licensed medical physician.

Your task is to assist healthcare professionals by delivering highly accurate, objective, and actionable insights to aid clinical decision-making.
"""

# layout
st.set_page_config(page_title="AI Medical Diagnostics Assistant", page_icon="🩺")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("diagnose.png", width=220)
    st.image("medical.png", width=220)

st.title("🩺 🔬 AI Medical Diagnostic Assistant")
st.subheader("🧑‍⚕️ ✨")
st.subheader("An intelligent application for medical image recognition and diagnostic assistance")

# Initialize Groq client (from environment variable, Streamlit secrets, or sidebar input)
client = None
active_api_key = GROQ_API_KEY or (st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets else "")

if not active_api_key:
    active_api_key = st.sidebar.text_input("Enter your Groq API Key (gsk_...):", type="password")

if active_api_key:
    client = Groq(api_key=active_api_key)

upload_file = st.file_uploader("please upload the medical images for analysis", type=["png", "jpg", "jpeg"])  
submit_button = st.button("Generate image Analysis")

if submit_button:
    if not client:
        st.error("Please enter your Groq API Key in the sidebar or configure the GROQ_API_KEY environment variable!")
    elif upload_file is not None:
        # process the uploaded image into base64
        image_bytes = upload_file.getvalue()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        mime_type = upload_file.type if upload_file.type else "image/jpeg"

        with st.spinner("Analyzing medical image with Groq Vision AI..."):
            try:
                # generate response using Groq's high-speed multimodal vision model
                chat_completion = client.chat.completions.create(
                    model="qwen/qwen3.8-27b",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"{system_prompt}\n\nPlease perform a thorough, professional diagnostic evaluation of this medical image."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.2,
                    max_tokens=2048,
                )

                response_text = chat_completion.choices[0].message.content
                st.write(response_text)
            except Exception as e:
                st.error(f"Error communicating with Groq API: {e}")
    else:
        st.warning("Please upload an image first!")