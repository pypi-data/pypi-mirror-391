import io
import json
import logging
import time

import requests
from bizyairsdk import tensor_to_bytesio
from comfy_api.latest._input_impl import VideoFromFile

from bizyengine.bizyair_extras.utils.audio import save_audio
from bizyengine.core import BizyAirBaseNode, pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.client import send_request
from bizyengine.core.common.env_var import BIZYAIR_X_SERVER

from .utils.aliyun_oss import parse_upload_token, upload_file_without_sdk

_GRSAI_FAILED_STATUS = ["failed"]


def veo_create_task_and_wait_for_completion(data, model, prompt, headers):
    # 创建任务
    create_task_url = f"{BIZYAIR_X_SERVER}/proxy_inference/GRSAI/{model}"
    json_payload = json.dumps(data).encode("utf-8")
    logging.debug(f"json_payload: {json_payload}")
    create_api_resp = send_request(
        url=create_task_url,
        data=json_payload,
        headers=headers,
    )
    logging.debug(f"create task api resp: {create_api_resp}")

    # 检查任务创建是否成功
    if (
        "code" not in create_api_resp
        or create_api_resp["code"] != 0
        or "data" not in create_api_resp
        or "id" not in create_api_resp["data"]
    ):
        raise ValueError(f"Invalid response: {create_api_resp}")

    # 轮询获取结果，最多等待1小时
    task_id = create_api_resp["data"]["id"]
    logging.info(f"Veo3.1 task created, task_id: {task_id}")
    start_time = time.time()
    status_url = f"{BIZYAIR_X_SERVER}/proxy_inference/GRSAI/{model}/{task_id}"
    while time.time() - start_time < 3600:
        time.sleep(10)
        try:
            status_api_resp = send_request(
                method="GET",
                url=status_url,
                headers=headers,
            )
            logging.debug(f"status api resp: {status_api_resp}")
        except Exception as e:
            logging.error(f"Veo3.1 task {task_id} status api error: {e}")
            continue

        if (
            "data" in status_api_resp
            and "status" in status_api_resp["data"]
            and status_api_resp["data"]["status"] == "succeeded"
            and "url" in status_api_resp["data"]
            and status_api_resp["data"]["url"]
        ):
            video_url = status_api_resp["data"]["url"]
            logging.info(f"Veo3.1 task {task_id} success, video_url: {video_url}")
            # 下载视频
            video_resp = requests.get(video_url, stream=True, timeout=3600)
            video_resp.raise_for_status()  # 非 2xx 会抛异常
            return (VideoFromFile(io.BytesIO(video_resp.content)),)
        if (
            "data" not in status_api_resp
            or "status" not in status_api_resp["data"]
            or "code" not in status_api_resp
            or status_api_resp["code"] != 0
        ):
            raise ValueError(f"Invalid response: {status_api_resp}")
        if status_api_resp["data"]["status"] in _GRSAI_FAILED_STATUS:
            raise ValueError(f"Veo3.1 task failed: {status_api_resp}")
        logging.debug(
            f"Veo3.1 task {task_id} status: {status_api_resp['data']['status']}"
        )

    raise ValueError(f"Veo3.1 task timed out, request ID: {task_id}")


class Veo_V3_1_I2V_API(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "first_frame_image": ("IMAGE", {"tooltip": "首帧图片"}),
                "model": (["veo3.1-fast", "veo3.1-pro"], {"default": "veo3.1-fast"}),
            },
            "optional": {
                "last_frame_image": ("IMAGE", {"tooltip": "尾帧图片"}),
                "aspect_ratio": (
                    ["9:16", "16:9"],
                    {"default": "16:9"},
                ),
            },
        }

    NODE_DISPLAY_NAME = "Veo3.1 Image To Video"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    CATEGORY = "☁️BizyAir/External APIs/Veo"
    FUNCTION = "api_call"

    def api_call(self, first_frame_image, model, prompt, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])
        prompt_id = extra_data["prompt_id"]
        headers["X-BIZYAIR-PROMPT-ID"] = prompt_id
        headers["X-Bizyair-Async-Result"] = "enable"

        # 参数
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        last_frame_image = kwargs.get("last_frame_image", None)

        input = {
            "webHook": "-1",
            "aspectRatio": aspect_ratio,
            "model": model,
        }
        if prompt is not None and prompt.strip() != "":
            input["prompt"] = prompt
        else:
            raise ValueError("Prompt is required")

        # 上传图片
        if first_frame_image is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}_first.png&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            input["firstFrameUrl"] = upload_file_without_sdk(
                tensor_to_bytesio(first_frame_image), **auth_info
            )
        if last_frame_image is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}_last.png&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            input["lastFrameUrl"] = upload_file_without_sdk(
                tensor_to_bytesio(last_frame_image), **auth_info
            )

        # 调用API
        return veo_create_task_and_wait_for_completion(
            data=input, model=model, prompt=prompt, headers=headers
        )


class Veo_V3_1_I2V_REF_API(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "ref_image_1": ("IMAGE", {"tooltip": "参考图片1"}),
                "model": (["veo3.1-fast"], {"default": "veo3.1-fast"}),
            },
            "optional": {
                "ref_image_2": ("IMAGE", {"tooltip": "参考图片2"}),
                "ref_image_3": ("IMAGE", {"tooltip": "参考图片3"}),
                "aspect_ratio": (["16:9"], {"default": "16:9"}),
            },
        }

    NODE_DISPLAY_NAME = "Veo3.1 Image To Video (Reference Images)"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    CATEGORY = "☁️BizyAir/External APIs/Veo"
    FUNCTION = "api_call"

    def api_call(self, ref_image_1, model, prompt, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])
        prompt_id = extra_data["prompt_id"]
        headers["X-BIZYAIR-PROMPT-ID"] = prompt_id
        headers["X-Bizyair-Async-Result"] = "enable"

        # 参数
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        ref_image_2 = kwargs.get("ref_image_2", None)
        ref_image_3 = kwargs.get("ref_image_3", None)

        input = {
            "webHook": "-1",
            "aspectRatio": aspect_ratio,
            "model": model,
        }
        if prompt is not None and prompt.strip() != "":
            input["prompt"] = prompt
        else:
            raise ValueError("Prompt is required")

        # 上传图片
        ref_images = []
        if ref_image_1 is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}_ref_1.png&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            ref_images.append(
                upload_file_without_sdk(tensor_to_bytesio(ref_image_1), **auth_info)
            )
        if ref_image_2 is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}_ref_2.png&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            ref_images.append(
                upload_file_without_sdk(tensor_to_bytesio(ref_image_2), **auth_info)
            )
        if ref_image_3 is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}_ref_3.png&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            ref_images.append(
                upload_file_without_sdk(tensor_to_bytesio(ref_image_3), **auth_info)
            )
        input["urls"] = ref_images

        # 调用API
        return veo_create_task_and_wait_for_completion(
            data=input, model=model, prompt=prompt, headers=headers
        )


class Veo_V3_1_T2V_API(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "model": (["veo3.1-fast", "veo3.1-pro"], {"default": "veo3.1-fast"}),
            },
            "optional": {
                "aspect_ratio": (
                    ["9:16", "16:9"],
                    {"default": "16:9"},
                ),
            },
        }

    NODE_DISPLAY_NAME = "Veo3.1 Text To Video"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    CATEGORY = "☁️BizyAir/External APIs/Veo"
    FUNCTION = "api_call"

    def api_call(self, prompt, model, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])
        prompt_id = extra_data["prompt_id"]
        headers["X-BIZYAIR-PROMPT-ID"] = prompt_id
        headers["X-Bizyair-Async-Result"] = "enable"

        # 参数
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")

        input = {
            "webHook": "-1",
            "aspectRatio": aspect_ratio,
            "model": model,
        }
        if prompt is not None and prompt.strip() != "":
            input["prompt"] = prompt
        else:
            raise ValueError("Prompt is required")

        # 调用API
        return veo_create_task_and_wait_for_completion(
            data=input, model=model, prompt=prompt, headers=headers
        )
