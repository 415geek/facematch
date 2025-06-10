import streamlit as st
import requests
import time
import os
import re

# 读取 API Token
APITOKEN = os.getenv("FACECHECK_API_KEY")
TESTING_MODE = False  # 改成 True 可测试（不消耗点数）

def is_valid_phone(phone):
    return bool(re.fullmatch(r"\d{10,15}", phone))

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
        st.write(f"{response.get('message')} | 进度: {response.get('progress')}%")
        time.sleep(1)

# ───────────── 页面设置 ─────────────
st.set_page_config(page_title="AI FaceMatch 人脸搜索", layout="centered")
st.title("🔍 AI 人脸搜索引擎 by c8geek")
st.write("Build with ❤️ in San Francisco")

# ───────────── 用户手机号验证 ─────────────
if "phone_verified" not in st.session_state:
    st.session_state.phone_verified = False
if "search_count" not in st.session_state:
    st.session_state.search_count = 0

if not st.session_state.phone_verified:
    phone = st.text_input("📱 请输入您的手机号（仅用于防刷验证）", max_chars=20)
    if phone:
        if is_valid_phone(phone):
            st.session_state.phone_verified = True
            st.success("✅ 手机号格式有效，验证通过！")
        else:
            st.error("❌ 手机号格式无效，请输入10~15位纯数字，不含+号或空格")
            st.stop()
    else:
        st.stop()

# ───────────── 使用条款 ─────────────
with st.expander("📜 使用条款与免责说明", expanded=True):
    st.markdown("""
我确认我已年满18岁，并同意以下内容：

- 我不会使用本服务跟踪、骚扰、威胁、勒索或针对任何人  
- 我不会上传18岁以下未成年人的照片  
- 我不会将本服务用于任何非法或不道德用途   
- 我将对我使用本服务的行为承担全部法律责任  

c8geek 不对搜索结果的准确性做任何保证。  
我放弃就使用结果对 c8geek 提起任何诉讼的权利。

✅ 勾选并点击“开始搜索”即表示我接受此协议。  
❌ 如果您不同意，请立即退出网站。
    """)

agreed = st.checkbox("✅ 我同意以上使用条款")

# ───────────── 主搜索逻辑 ─────────────
if agreed:
    uploaded_file = st.file_uploader("📷 请上传一张清晰的人脸照片 (jpg/png)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        temp_path = "uploaded_face.jpg"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        st.image(temp_path, caption="📷 上传照片", width=300)

        if st.button("🔍 开始搜索"):
            if st.session_state.search_count >= 5:
                st.warning("⚠️ 您的免费搜索次数已用尽（5次）。如需继续使用，请联系管理员。")
            else:
                with st.spinner("深网搜索中 (Social Media, Government, 等)..."):
                    error, results = search_by_face(temp_path)

                st.session_state.search_count += 1
                st.info(f"🎯 当前已使用次数：{st.session_state.search_count}/5")

                if error:
                    st.error(error)
                elif results:
                    st.success("✅ 匹配结果：")
                    for idx, match in enumerate(results):
                        score = match.get("score", 0)
                        page_url = match.get("url", "")
                        thumb_b64 = match.get("base64", "")

                        st.markdown(f"### 匹配结果 {idx + 1}")
                        st.markdown(f"**匹配指数:** {score}")
                        st.markdown(f"[🔗 匹配来源]({page_url})")

                        if thumb_b64:
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
                            st.image("https://via.placeholder.com/150?text=No+Image", width=150)

                        st.markdown("---")
                else:
                    st.warning("😕 未找到任何匹配项")
else:
    st.warning("⚠️ 请勾选同意使用条款才能继续")
