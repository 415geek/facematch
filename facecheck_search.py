# facecheck_search.py — 工具模块：与 FaceCheck API 交互（含进度回调）
import os
import time
import requests

APITOKEN = os.getenv("FACECHECK_API_KEY")

def search_by_face(
    image_path: str,
    topk: int = 50,
    demo: bool = False,
    shady_only: bool = False,
    progress_cb=None,   # 新增：进度回调，形如 cb(percent:int, message:str)
):
    """
    上传图片 -> 轮询搜索 -> 返回按 score 排序后的 Top-K
    返回: (error_str_or_None, items_list_or_None)
    """
    if not APITOKEN:
        return "FACECHECK_API_KEY 未配置", None

    site = "https://facecheck.id"
    headers = {"accept": "application/json", "Authorization": APITOKEN}

    # --- 1) 上传图片 ---
    try:
        if progress_cb:
            progress_cb(0, "上传图片中…")
        with open(image_path, "rb") as f:
            files = {"images": f, "id_search": (None, "")}  # 字段必须是 images
            up = requests.post(f"{site}/api/upload_pic", headers=headers, files=files, timeout=60)
        upj = up.json()
    except Exception as e:
        return f"upload_pic 失败: {e}", None

    if upj.get("error"):
        return f"upload_pic error: {upj['error']} ({upj.get('code', '')})", None

    id_search = upj.get("id_search") or (upj.get("input") or [{}])[0].get("id_pic")
    if not id_search:
        return "upload_pic: 缺少 id_search", None

    # --- 2) 轮询搜索 ---
    payload = {
        "id_search": id_search,
        "with_progress": True,
        "status_only": False,
        "demo": bool(demo),            # False = 生产索引；True = 测试索引
        "shady_only": bool(shady_only) # 开启会过滤大量站点，一般不建议
    }

    if progress_cb:
        progress_cb(1, "开始检索…")

    items = []
    while True:
        try:
            rsp = requests.post(f"{site}/api/search", headers=headers, json=payload, timeout=60)
            js = rsp.json()
        except Exception as e:
            return f"search 请求失败: {e}", None

        if js.get("error"):
            return f"search error: {js['error']} ({js.get('code', '')})", None

        # 进度回调
        prog = int(js.get("progress", 0) or 0)
        msg = js.get("message", "检索中…")
        if progress_cb:
            # 保证 0~100
            prog = min(max(prog, 0), 100)
            progress_cb(prog, msg)

        out = js.get("output")
        if out and out.get("items"):
            items = out["items"]
            if progress_cb:
                progress_cb(100, "完成")
            break

        time.sleep(1)

    # --- 3) 排序 & 截取 Top-K ---
    items = sorted(items, key=lambda x: x.get("score", 0), reverse=True)[:topk]
    return None, items
