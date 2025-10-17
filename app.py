import streamlit as st
from facecheck_search import search_by_face

st.set_page_config(page_title="FaceMatch AI", layout="centered")
st.title("🔍 FaceMatch (FaceCheck API)")

api_ok = True
if not os.getenv("FACECHECK_API_KEY"):
    st.warning("未检测到 FACECHECK_API_KEY 环境变量，请在 Secrets 或环境变量里配置。")
    api_ok = False

uploaded = st.file_uploader("上传一张清晰的人脸照片", type=["jpg","jpeg","png"])
if uploaded and api_ok:
    tmp = "uploaded_face.jpg"
    with open(tmp, "wb") as f:
        f.write(uploaded.getbuffer())
    st.image(tmp, caption="Uploaded", width=280)

    if st.button("开始搜索"):
        with st.spinner("搜索中…"):
            err, items = search_by_face(tmp, topk=50)

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
                url = it.get('url', '') if isinstance(it.get('url'), str) else (it.get('url',{}).get('value',''))
                b64 = it.get('base64','')
                if not b64.startswith("data:image"):
                    b64 = f"data:image/webp;base64,{b64}"
                col.markdown(f"**#{i} — {score:.1f}**")
                col.markdown(f"![thumb]({b64})")
                if url:
                    col.markdown(f"[来源链接]({url})")
