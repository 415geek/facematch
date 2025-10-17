import streamlit as st
import requests
import time, requests, os
import streamlit as st

APITOKEN = os.getenv("FACECHECK_API_KEY")
TESTING_MODE = False  # 生产检索：False

def search_by_face(image_path, topk=50):
    site = 'https://facecheck.id'
    headers = {
        'accept': 'application/json',
        'Authorization': APITOKEN
    }

    # 1) 上传图片，拿到 id_search
    with open(image_path, 'rb') as f:
        files = {'images': f, 'id_search': (None, '')}  # 字段名必须是 images
        up = requests.post(f'{site}/api/upload_pic', headers=headers, files=files, timeout=60)
    try:
        upj = up.json()
    except Exception:
        return f'upload_pic failed: HTTP {up.status_code}', None
    if upj.get('error'):
        return f"upload_pic error: {upj['error']} ({upj.get('code','')})", None

    id_search = upj.get('id_search') or (upj.get("input") or [{}])[0].get("id_pic")
    if not id_search:
        return "upload_pic: missing id_search", None
    st.info(f"已上传，搜索ID：{id_search}")

    # 2) 轮询搜索直到 output 出现（demo=False，关闭测试模式）
    payload = {
        'id_search': id_search,
        'with_progress': True,
        'status_only': False,
        'demo': False,
        'shady_only': False  # ← 关掉这个，否则很多正常结果被过滤
    }
    while True:
        rsp = requests.post(f'{site}/api/search', headers=headers, json=payload, timeout=60)
        js = rsp.json()
        if js.get('error'):
            return f"search error: {js['error']} ({js.get('code','')})", None
        if js.get('output') and js['output'].get('items'):
            items = js['output']['items']
            break
        st.write(f"{js.get('message','搜索中…')} 进度 {js.get('progress',0)}%")
        time.sleep(1)

    # 3) 按 score 排序并截取 Top-50
    items = sorted(items, key=lambda x: x.get('score', 0), reverse=True)[:topk]
    return None, items
