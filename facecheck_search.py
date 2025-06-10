import streamlit as st
import requests
import time
import os

# ✅ Securely read API key from Streamlit Secrets
APITOKEN = os.getenv("FACECHECK_API_KEY")
TESTING_MODE = False  # ✅ Real mode (consumes credits)

def search_by_face(image_path):
    site = 'https://facecheck.id'
    headers = {'accept': 'application/json', 'Authorization': APITOKEN}
    files = {'images': open(image_path, 'rb'), 'id_search': None}

    response = requests.post(site + '/api/upload_pic', headers=headers, files=files).json()
    if response.get('error'):
        return f"{response['error']} ({response['code']})", None

    id_search = response['id_search']
    st.info(f"{response['message']} | ID: {id_search}")

    json_data = {
        'id_search': id_search,
        'with_progress': True,
        'status_only': False,
        'demo': TESTING_MODE
    }

    while True:
        response = requests.post(site + '/api/search', headers=headers, json=json_data).json()
        if response.get('error'):
            return f"{response['error']} ({response['code']})", None
        if response.get('output'):
            return None, response['output']['items']
        st.write(f"{response['message"]} | Progress: {response['progress']}%")
        time.sleep(1)

# ───────────────────────────────────────────────
st.set_page_config(page_title="FaceMatch Search", layout="centered")
st.title("🔍 AI 人脸搜索 by c8geek")
st.write("Build with ❤️ in San Francisco")

# ✅ Legal waiver
with st.expander("📜 Terms of Use & Liability Waiver", expanded=True):
    st.markdown("""
    I hereby affirm that I'm 18 years or older and I agree that as a result of this search:

    - I WILL NOT CONFRONT a dangerous person  
    - I WILL NOT HARASS a person  
    - I WILL NOT UPLOAD photos of persons under the age of 18  
    - I WILL NOT STALK a person  
    - I WILL NOT BLACKMAIL a person  
    - I WILL NOT USE any information in a way that would require AIFACEMATCH to report to any local government  
    - I WILL NOT USE information to make decisions about employment, housing, credit, or insurance  
    - I WILL NOT use this search for illegal activities  
    - I AFFIRM that I am not a citizen or resident of a European Union country  
    - I AFFIRM full legal responsibility for my use in accordance with my local laws  

    **Compliance and Liability Declaration:**  
    I accept full legal responsibility for my actions. AIFACEMATCH provides no warranty of accuracy.  

    **User Release and Waiver to Sue:**  
    I waive all rights to sue AIFACEMATCH or its team for any outcomes arising from use of this service.  

    > By checking the box and clicking AGREE AND SEARCH, I agree to be legally bound by this agreement.

    ❌ IF YOU DO NOT AGREE, YOU MUST DISCONTINUE USE IMMEDIATELY.
    """)

agreed = st.checkbox("✅ I have read and agree to the terms above")

if not agreed:
    st.warning("⚠️ You must agree to the Terms before using this service.")
else:
    uploaded_file = st.file_uploader("📷 请上传一张清晰的人脸照片(jpg/png)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        temp_path = "uploaded_face.jpg"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        st.image(temp_path, caption="Uploaded Image", width=300)

        if st.button("🔍 开始匹配"):
            with st.spinner("深网搜索中..."):
                error, results = search_by_face(temp_path)

            if error:
                st.error(error)
            elif results:
                st.success("✅ 匹配结果:")
                for idx, match in enumerate(results):
                    score = match.get("score", 0)
                    page_url = match.get("url", "")
                    image_url_direct = match.get("url_image", "")
                    thumb_b64 = match.get("base64", "")

                    st.markdown(f"### Match {idx + 1}")
                    st.markdown(f"**相似指数:** {score}")
                    st.markdown(f"[🔗 查看匹配出处]({page_url})")

                    if image_url_direct:
                        st.image(image_url_direct, width=150, caption="Matched Image (URL)")
                    elif thumb_b64:
                        # Render WebP base64 preview using HTML background-image
                        st.markdown(
                            f"""
                            <div style='
                                width: 150px;
                                height: 150px;
                                background-image: url("data:image/webp;base64,{thumb_b64}");
                                background-size: cover;
                                background-position: center;
                                border-radius: 10px;
                                border: 1px solid #ccc;
                                margin-bottom: 10px;
                            '></div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.image("https://via.placeholder.com/150?text=No+Image", width=150, caption="Image not available")

                    st.markdown("---")
            else:
                st.warning("No results found.")
