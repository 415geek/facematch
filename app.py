import streamlit as st
from face_utils import query_facecheck, query_faceplusplus

st.set_page_config(page_title="FaceMatcher", layout="centered")
st.title("🔍 Multi-Engine Face Matcher")
st.write("Upload a face photo to match across platforms.")

uploaded_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with open("temp_input.jpg", "wb") as f:
        f.write(uploaded_file.read())
    st.image("temp_input.jpg", caption="Uploaded Image", width=300)

    with st.spinner("Querying FaceCheck ID..."):
        facecheck_result = query_facecheck("temp_input.jpg")
        st.subheader("🎯 FaceCheck ID Result")
        st.json(facecheck_result)

    with st.spinner("Querying Face++..."):
        faceplusplus_result = query_faceplusplus("temp_input.jpg")
        st.subheader("🎯 Face++ Result")
        st.json(faceplusplus_result)