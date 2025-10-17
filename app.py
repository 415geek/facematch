# app.py — Streamlit 入口（FaceCheck Top-50）
import os
import streamlit as st
from urllib.parse import urlparse
from facecheck_search import search_by_face

st.set_page_config(page_title="FaceMatch (FaceCheck API)", layout="centered")
st.title("🔍 FaceMatch (FaceCheck API)")
st.caption("关闭测试模式可获得与官网更接近的结果（会扣点）。")

# ---- 侧边栏参数 ----
demo = st.sidebar.toggle("测试模式 demo（不扣点，结果不准）", value=False)
shady_only = st.sidebar.toggle("仅可疑站点（shady_only）", value=False,
                               help="开启会过滤掉大量正常站点，一般不要开")
topk = st.sidebar.slider("返回数量 Top-K", min_value=10, max_value=100, value=50, step=5)
dedupe = st.sidebar.toggle("同域名去重（保留最高分）", value=True)

# ---- 环境检查 ----
if not os.getenv("FACECHECK_API_KEY"):
    st.warning("未检测到 FACECHECK_API_KEY。请在本地环境变量或 Streamlit Secrets 中配置。")

# ---- 文件上传 ----
f = st.file_uploader("上传一张清晰人脸照片（jpg/png）", type=["jpg", "jpeg", "png"])
if f:
    tmp = "uploaded_face.jpg"
    with open(tmp, "wb") as w:
        w.write(f.getbuffer())
    st.image(tmp, caption="Uploaded", width=260)

    if st.button("开始搜索"):
        with st.spinner("搜索中…"):
            err, items = search_by_face(tmp, topk=topk, demo=demo, shady_only=shady_only)

        if err:
            st.error(err)
            st.stop()

        if not items:
            st.info("未找到匹配结果。")
            st.stop()

        # 可选：同域名去重（保留该域名下分数最高的一条）
        if dedupe:
            best_by_domain = {}
            for it in items:
                raw = it.get("url", "")
                url = raw.get("value", "") if isinstance(raw, dict) else raw
                domain = urlparse(url).netloc or "unknown"
                if domain not in best_by_domain or it.get("score", 0) > best_by_domain[domain].get("score", 0):
                    best_by_domain[domain] = it
            items = sorted(best_by_domain.values(), key=lambda x: x.get("score", 0), reverse=True)

        st.success(f"找到 {len(items)} 条候选")
        cols = st.columns(5)

        for i, it in enumerate(items[:topk], 1):
            col = cols[(i - 1) % 5]
            score = it.get("score", 0)

            raw_url = it.get("url", "")
            url = raw_url.get("value", "") if isinstance(raw_url, dict) else raw_url

            b64 = it.get("base64", "")
            if b64 and not b64.startswith("data:image"):
                b64 = f"data:image/webp;base64,{b64}"

            col.markdown(f"**#{i} — {score:.1f}**")
            if b64:
                col.markdown(f"![thumb]({b64})")
            if url:
                col.markdown(f"[来源链接]({url})")
