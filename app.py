import os, streamlit as st
from facecheck_search import search_by_face

st.set_page_config(page_title="FaceMatch (FaceCheck API)", layout="centered")
st.title("🔍 FaceMatch (FaceCheck API)")
st.caption("关闭测试模式可获得和官网接近的结果（会扣点）")

# 侧边栏开关
demo = st.sidebar.toggle("测试模式（demo）", value=False, help="只扫小索引，不扣点，结果不准")
topk = st.sidebar.slider("返回数量", 10, 100, 50, 5)
shady_only = st.sidebar.toggle("仅可疑站点(shady_only)", value=False, help="多数场景不要开")

# API token 检查
if not os.getenv("FACECHECK_API_KEY"):
    st.warning("未检测到 FACECHECK_API_KEY，请在 Secrets 或环境变量中配置。")

uploaded = st.file_uploader("上传一张清晰人脸照片（jpg/png）", type=["jpg","jpeg","png"])
if uploaded:
    tmp = "uploaded_face.jpg"
    with open(tmp, "wb") as f:
        f.write(uploaded.getbuffer())
    st.image(tmp, caption="Uploaded", width=260)

    if st.button("开始搜索"):
        with st.spinner("搜索中…"):
            err, items = search_by_face(tmp, topk=topk, demo=demo, shady_only=shady_only)

        if err:
            st.error(err)
        elif not items:
            st.info("未找到匹配结果。")
        else:
            st.success(f"找到 {len(items)} 条候选")
            cols = st.columns(5)
            for i, it in enumerate(items, 1):
                col = cols[(i-1) % 5]
                score = it.get('score', 0)
                # 结果里的 url 可能是字符串或 {value: "..."}
                raw_url = it.get('url', '')
                url = raw_url.get('value', '') if isinstance(raw_url, dict) else raw_url
                b64 = it.get('base64', '')
                if b64 and not b64.startswith("data:image"):
                    b64 = f"data:image/webp;base64,{b64}"

                col.markdown(f"**#{i} — {score:.1f}**")
                if b64:
                    col.markdown(f"![thumb]({b64})")
                if url:
                    col.markdown(f"[来源链接]({url})")
