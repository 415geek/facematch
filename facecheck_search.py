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
        st.write(f'{response["message"]} | Progress: {response["progress"]}%')
        time.sleep(1)

# ───────────────────────────────────────────────
st.set_page_config(page_title="FaceMatch Search", layout="centered")
st.title("🔍 AIFACEMATCH - AI Face Search Engine")

# ✅ Legal waiver
with st.expander("📜 Terms of Use & Liability Waiver", expanded=True):
    st.markdown("""
    我确认我已年满18岁，并同意以下内容：

- 我不会使用本服务跟踪、骚扰、威胁、勒索或针对任何人  
- 我不会上传18岁以下未成年人的照片  
- 我不会将本服务用于任何非法或不道德用途  
- 我不是欧盟成员国的公民或居民  
- 我将对我使用本服务的行为承担全部法律责任  

c8geek 不对搜索结果的准确性做任何保证。  
我放弃就使用结果对 c8geek 提起任何诉讼的权利。

勾选并点击“同意以上的使用条款”即表示我接受此协议。

❌ 如果您不同意，请立即退出网站。.
    """)

agreed = st.checkbox("✅ 同意以上的使用条款")

if not agreed:
    st.warning("⚠️ 必须同意上述使用规则才能使用.")
else:
    uploaded_file = st.file_uploader("📷 请上传一张清晰的人脸照片 (jpg/png)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        temp_path = "uploaded_face.jpg"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        st.image(temp_path, caption="Uploaded Image", width=300)

        if st.button("🔍 开始搜索"):
            with st.spinner("深网搜索中(Social Media,Govt Record etc...)"):
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
                    st.markdown(f"**匹配指数:** {score}")
                    st.markdown(f"[🔗 匹配来源]({page_url})")

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
