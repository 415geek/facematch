import streamlit as st
import requests
import time
import os

# ✅ 读取 FaceCheck API 密钥
APITOKEN = os.getenv("FACECHECK_API_KEY")
TESTING_MODE = False

# ✅ 搜索函数
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

# ───────────── 页面配置 ─────────────
st.set_page_config(page_title="FaceMatch AI 人脸搜索", layout="centered")
st.title("🔍 AI 人脸搜索引擎 by c8geek")
st.write("Build with ❤️ in San Francisco")

# ───────────── Session 初始化 ─────────────
if "phone_verified" not in st.session_state:
    st.session_state.phone_verified = False
if "search_count" not in st.session_state:
    st.session_state.search_count = 0

# ───────────── 手机号验证 ─────────────
import re

# ───────────── 手机号验证 ─────────────
if not st.session_state.phone_verified:
    phone = st.text_input("📱 手机号码登录", max_chars=20)

    def is_valid_phone(p):
        return bool(re.fullmatch(r"\d{10,15}", p))  # 至少10位，最多15位纯数字

    if phone and is_valid_phone(phone):
        st.session_state.phone_verified = True
        st.success("✅ 手机号格式有效，验证成功！")
    elif phone:
        st.error("❌ 手机号格式无效，请输入10位以上纯数字手机号（不含+或空格）")
        st.stop()
    else:
        st.stop()

# ───────────── 使用条款 ─────────────
with st.expander("📜 使用条款与法律免责声明", expanded=True):
    st.markdown("""
我确认我已年满18岁，并同意以下内容：

- 我不会使用本服务跟踪、骚扰、威胁、勒索或针对任何人  
- 我不会上传18岁以下未成年人的照片  
- 我不会将本服务用于任何非法或不道德用途   
- 我将对我使用本服务的行为承担全部法律责任  

c8geek 不对搜索结果的准确性做任何保证。  
我放弃就使用结果对 c8geek 提起任何诉讼的权利。

✅ 勾选并点击“同意以上的使用条款”即表示我接受此协议。

❌ 如果您不同意，请立即退出网站。
    """)

agreed = st.checkbox("✅ 同意以上的使用条款")

# ───────────── 限制免费搜索次数 ─────────────
if st.session_state.search_count >= 5:
    st.error("⚠️ 您的免费搜索次数已达上限（5次）。请联系管理员或通过其他方式获取更多权限。")
    st.stop()

# ───────────── 上传并搜索 ─────────────
if agreed:
    uploaded_file = st.file_uploader("📷 请上传一张清晰的人脸照片 (jpg/png)", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        temp_path = "uploaded_face.jpg"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        st.image(temp_path, caption="Uploaded Image", width=300)

        if st.button("🔍 开始搜索"):
            st.session_state.search_count += 1  # 增加搜索计数
            with st.spinner("深网搜索中（社交媒体、政府数据库等）..."):
                error, results = search_by_face(temp_path)

            if error:
                st.error(error)
            elif results:
                st.success(f"✅ 匹配结果（本次为第 {st.session_state.search_count} 次搜索）:")
                for idx, match in enumerate(results):
                    score = match.get("score", 0)
                    page_url = match.get("url", {}).get("value", "")
                    thumb_b64 = match.get("base64", "")

                    st.markdown(f"### Match {idx + 1}")
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
                        st.image("https://via.placeholder.com/150?text=No+Image", width=150, caption="Image not available")

                    st.markdown("---")
            else:
                st.warning("未找到匹配结果。")
else:
    st.warning("⚠️ 您必须先勾选使用条款才能继续")
