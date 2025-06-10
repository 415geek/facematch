import streamlit as st
import requests
import time
import os
import re

# 读取 API 密钥（推荐通过 Streamlit Secrets 管理）
APITOKEN = os.getenv("FACECHECK_API_KEY")
TESTING_MODE = False  # 设置为 True 则使用 demo 模式（不消耗点数）

# ─────────────────────────────────────────────
def search_by_face(image_path):
    site = 'https://facecheck.id'
    headers = {'accept': 'application/json', 'Authorization': APITOKEN}
    files = {'images': open(image_path, 'rb'), 'id_search': (None, '')}

    response = requests.post(site + '/api/upload_pic', headers=headers, files=files).json()
    if response.get("error"):
        return f"{response['error']} ({response.get('code', 'Error')})", None

    id_search = response.get('id_search') or response.get("input", [{}])[0].get("id_pic")
    st.info(f"{response.get('message', '已上传')} | ID: {id_search}")

    json_data = {
        'id_search': id_search,
        'with_progress': True,
        'status_only': False,
        'demo': TESTING_MODE,
        'shady_only': True
    }

    while True:
        resp = requests.post(site + '/api/search', headers=headers, json=json_data).json()
        if resp.get('error'):
            return f"{resp['error']} ({resp.get('code', '')})", None
        if resp.get('output') and resp['output'].get('items'):
            return None, resp['output']['items']
        st.write(f"{resp.get('message', '搜索中...')} | 进度: {resp.get('progress', 0)}%")
        time.sleep(1)
# ─────────────────────────────────────────────
st.set_page_config(page_title="FaceMatch AI 人脸搜索", layout="centered")
st.title("🔍 AI 人脸搜索引擎 by c8geek")
st.write("Build with ❤️ in San Francisco")

# 📜 使用条款
with st.expander("📜 使用条款与免责声明", expanded=True):
    st.markdown("""
我确认我已年满18岁，并同意以下内容：

- 我不会使用本服务跟踪、骚扰、威胁、勒索或针对任何人  
- 我不会上传18岁以下未成年人的照片  
- 我不会将本服务用于任何非法或不道德用途   
- 我将对我使用本服务的行为承担全部法律责任  

**⚖️ 合规声明：** 本服务不对搜索结果的准确性做任何保证。  
**🛡️ 放弃追责：** 我放弃就使用结果对 AIFACEMATCH 提起任何诉讼的权利。

✅ 勾选并点击“开始搜索”即表示我接受此协议。  
❌ 如果您不同意，请立即退出网站。
""")

agreed = st.checkbox("✅ 我已阅读并同意上述条款")

if not agreed:
    st.warning("⚠️ 请勾选同意条款后才能继续使用。")
else:
    uploaded_file = st.file_uploader("📷 请上传一张清晰的人脸照片 (jpg/png)", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        temp_path = "uploaded_face.jpg"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        st.image(temp_path, caption="Uploaded Image", width=300)

        if st.button("🔍 开始搜索"):
            with st.spinner("正在进行深网人脸搜索..."):
                error, results = search_by_face(temp_path)

            if error:
                st.error(error)
            elif results:
                st.success("✅ 匹配结果如下：")
                for idx, match in enumerate(results):
                    score = match.get("score", 0)
                    thumb_b64 = match.get("base64", "")
                    raw_url = match.get("url", "")
                    if isinstance(raw_url, dict):
                        page_url = raw_url.get("value", "")
                    else:
                        page_url = raw_url
   
                    st.markdown(f"### Match {idx + 1}")
                    st.markdown(f"**匹配指数:** {score}")
                    if page_url:
                        st.markdown(f'<a href="{page_url}" target="_blank">🔗 匹配来源</a>', unsafe_allow_html=True)

                    if thumb_b64:
                        if thumb_b64.startswith("data:image"):
                            b64_url = thumb_b64
                        else:
                            b64_url = f"data:image/webp;base64,{thumb_b64}"

                        st.markdown(
                            f"""
                            <div style='
                                width: 150px;
                                height: 150px;
                                background-image: url("{b64_url}");
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
                st.warning("未找到匹配结果，请尝试更清晰的照片。")
