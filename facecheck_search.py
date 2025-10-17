# facecheck_search.py  —— 纯工具：不包含任何 Streamlit UI
import os, time, requests

APITOKEN = os.getenv("FACECHECK_API_KEY")

def search_by_face(image_path: str, topk: int = 50, demo: bool = False, shady_only: bool = False):
    """
    上传图片 → 轮询搜索 → 返回按 score 排序后的 Top-K 列表
    返回: (error_str_or_None, items_list_or_None)
    """
    if not APITOKEN:
        return "FACECHECK_API_KEY 未配置", None

    site = 'https://facecheck.id'
    headers = {'accept': 'application/json', 'Authorization': APITOKEN}

    # 1) 上传
    try:
        with open(image_path, 'rb') as f:
            files = {'images': f, 'id_search': (None, '')}  # 字段名必须是 images
            up = requests.post(f'{site}/api/upload_pic', headers=headers, files=files, timeout=60)
        upj = up.json()
    except Exception as e:
        return f'upload_pic 失败: {e}', None

    if upj.get('error'):
        return f"upload_pic error: {upj['error']} ({upj.get('code','')})", None

    id_search = upj.get('id_search') or (upj.get("input") or [{}])[0].get("id_pic")
    if not id_search:
        return "upload_pic: 缺少 id_search", None

    # 2) 轮询搜索（demo=False 才是正式索引；True 为测试索引）
    payload = {
        'id_search': id_search,
        'with_progress': True,
        'status_only': False,
        'demo': bool(demo),
        'shady_only': bool(shady_only)  # 开了会过滤掉很多站点，通常不要开
    }

    while True:
        try:
            rsp = requests.post(f'{site}/api/search', headers=headers, json=payload, timeout=60)
            js = rsp.json()
        except Exception as e:
            return f'search 请求失败: {e}', None

        if js.get('error'):
            return f"search error: {js['error']} ({js.get('code','')})", None
        if js.get('output') and js['output'].get('items'):
            items = js['output']['items']
            break
        time.sleep(1)

    # 3) 排序 & 截取 Top-K
    items = sorted(items, key=lambda x: x.get('score', 0), reverse=True)[:topk]
    return None, itemsf
