import streamlit as st
import requests
import time
import base64

# 🔐 Your FaceCheck ID API token
APITOKEN = 'C6bJH/K+14uXdBGTixe4uze6TJwgbl2Y8r1mKdQUcp4nnz7wyOj+v8672c2OrnJRBMz++ZsPMUs='  # <-- Replace this
TESTING_MODE = False  # Set to False for real results (uses credits)

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
        st.write(f"{response['message']} | Progress: {response['progress']}%")
        time.sleep(1)

# ───────────────────────────────────────────────
# Streamlit UI
st.set_page_config(page_title="FaceMatch", layout="centered")
st.title("🔍  AI人脸匹配 By c8geek")
st.write("Build with ❤️ in San Francisco.")

uploaded_file = st.file_uploader("请上传一张清晰的人脸照片", type=["jpg", "jpeg", "png"])

if uploaded_file:
    temp_path = "uploaded_face.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
    st.image(temp_path, caption="Uploaded Image", width=300)

    if st.button("开始匹配"):
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
                st.markdown(f"[🔗 查看匹配结果出处]({page_url})")

                if image_url_direct:
                    st.image(image_url_direct, width=150, caption="Matched Image (URL)")
                elif thumb_b64:
                    try:
                        st.image(f"data:image/jpeg;base64,{thumb_b64}", width=150, caption="Matched Image (Base64)")
                    except Exception as e:
                        st.warning(f"⚠️ Base64 decode failed: {e}")
                else:
                    st.warning("⚠️ No image preview available for this match.")

                st.markdown("---")
        else:
            st.warning("No results found.")
