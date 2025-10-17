# app.py — FaceCheck Top-K (gallery style + LinkedIn button)
import os
import streamlit as st
from urllib.parse import urlparse
from facecheck_search import search_by_face

# ---------------- Page header ----------------
st.set_page_config(page_title="AI 人脸匹配", layout="wide")
st.title("🔍 AI 人脸匹配")

# 开发者信息 + LinkedIn 按钮（与文字等高等大）
st.markdown(
    """
    <div style='display:flex; align-items:center; font-size:15px; margin-top:-10px;'>
        <span>Developed by <b>c8geek</b></span>
        <a href="https://www.linkedin.com/in/lingyu-maxwell-lai" target="_blank" style="
            text-decoration:none;
            margin-left:8px;
            color:#0A66C2;
            display:inline-flex;
            align-items:center;
            font-size:15px;
        ">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png"
                 width="15" height="15" style="margin-right:4px;"/>
            LinkedIn
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("上传一张清晰的人脸，点击缩略图即可跳转到来源页面。")

# ---------------- Sidebar ----------------
st.sidebar.header("设置")
topk = st.sidebar.slider("返回数量 Top-K", min_value=10, max_value=100, value=50, step=5)
dedupe = st.sidebar.toggle("同域名去重（保留最高分）", value=True)

# ---------------- Helpers ----------------
def normalize_url(raw_url):
    if isinstance(raw_url, dict):
        return raw_url.get("value", "")
    return raw_url or ""

def normalize_b64(b64):
    if not b64:
        return ""
    return b64 if b64.startswith("data:image") else f"data:image/webp;base64,{b64}"

def render_thumb_link(col, b64, url, score, rank):
    # 点击缩略图新开页；固定裁剪，观感类似官网
    if not b64 or not url:
        return
    html = f"""
    <div style="text-align:center; margin-bottom:12px;">
      <a href="{url}" target="_blank" rel="noopener">
        <img src="{b64}" alt="thumb #{rank}"
             style="width: 210px; height: 210px; object-fit: cover; border-radius: 8px; border: 1px solid #333;" />
      </a>
      <div style="margin-top:6px; font-size:13px; opacity:0.8;">#{rank} — {score:.1f}</div>
    </div>
    """
    col.markdown(html, unsafe_allow_html=True)

# ---------------- Token 提示 ----------------
if not os.getenv("FACECHECK_API_KEY"):
    st.warning("未检测到 FACECHECK_API_KEY，请在环境变量或 Streamlit Secrets 中配置。")

# ---------------- 上传与检索 ----------------
f = st.file_uploader("上传一张人脸照片（jpg/png）", type=["jpg", "jpeg", "png"])
if f:
    tmp = "uploaded_face.jpg"
    with open(tmp, "wb") as w:
        w.write(f.getbuffer())
    st.image(tmp, caption="Uploaded", width=300)

    if st.button("开始搜索", use_container_width=True):
        with st.spinner("搜索中…"):
            # 生产索引：demo=False；不在 UI 暴露此开关
            err, items = search_by_face(tmp, topk=topk, demo=False, shady_only=False)

        if err:
            st.error(err)
        elif not items:
            st.info("未找到匹配结果。")
        else:
            # 同域名去重（保留该域名最高分）
            if dedupe:
                best_by_domain = {}
                for it in items:
                    url = normalize_url(it.get("url"))
                    domain = urlparse(url).netloc or "unknown"
                    if domain not in best_by_domain or it.get("score", 0) > best_by_domain[domain].get("score", 0):
                        best_by_domain[domain] = it
                items = sorted(best_by_domain.values(), key=lambda x: x.get("score", 0), reverse=True)

            st.success(f"找到 {min(len(items), topk)} 条候选")
            cols = st.columns(5)
            for i, it in enumerate(items[:topk], 1):
                col = cols[(i - 1) % 5]
                score = it.get("score", 0)
                url = normalize_url(it.get("url"))
                b64 = normalize_b64(it.get("base64", ""))
                render_thumb_link(col, b64, url, score, i)
