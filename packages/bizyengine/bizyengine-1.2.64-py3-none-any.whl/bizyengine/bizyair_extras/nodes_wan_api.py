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

_FAILED_STATUS = ["FAILED", "CANCELED", "UNKNOWN"]


def wan_create_task_and_wait_for_completion(data, model, prompt, headers):
    # 创建任务
    create_task_url = f"{BIZYAIR_X_SERVER}/proxy_inference/Wan/{model}"
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
        "request_id" not in create_api_resp
        or "output" not in create_api_resp
        or "task_status" not in create_api_resp["output"]
        or "task_id" not in create_api_resp["output"]
    ):
        raise ValueError(f"Invalid response: {create_api_resp}")
    # 检查任务状态，是否已经报错，如果报错则抛出异常
    if create_api_resp["output"]["task_status"] in _FAILED_STATUS:
        raise ValueError(f"Wan2.5 create task failed: {create_api_resp}")

    # 轮询获取结果，最多等待1小时
    task_id = create_api_resp["output"]["task_id"]
    logging.info(
        f'Wan2.5 task created, task_id: {task_id}, request_id: {create_api_resp["request_id"]}'
    )
    start_time = time.time()
    status_url = f"{BIZYAIR_X_SERVER}/proxy_inference/Wan/{model}/{task_id}"
    while time.time() - start_time < 3600:
        time.sleep(10)
        try:
            status_api_resp = send_request(
                method="GET",
                url=status_url,
                headers=headers,
            )
        except Exception as e:
            logging.error(f"Wan2.5 task {task_id} status api error: {e}")
            continue

        if "output" in status_api_resp and "video_url" in status_api_resp["output"]:
            video_url = status_api_resp["output"]["video_url"]
            logging.info(f"Wan2.5 task {task_id} success, video_url: {video_url}")
            actual_prompt = status_api_resp["output"].get("actual_prompt", prompt)
            # 下载视频
            video_resp = requests.get(video_url, stream=True, timeout=3600)
            video_resp.raise_for_status()  # 非 2xx 会抛异常
            return (VideoFromFile(io.BytesIO(video_resp.content)), actual_prompt)
        if (
            "output" not in status_api_resp
            or "task_status" not in status_api_resp["output"]
        ):
            raise ValueError(f"Invalid response: {status_api_resp}")
        if status_api_resp["output"]["task_status"] in _FAILED_STATUS:
            raise ValueError(f"Wan2.5 task failed: {status_api_resp}")
        logging.debug(
            f"Wan2.5 task {task_id} status: {status_api_resp['output']['task_status']}"
        )

    raise ValueError(f"Wan2.5 task timed out, request ID: {task_id}")


class Wan_V2_5_I2V_API(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "audio": ("AUDIO",),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "resolution": (
                    ["480P", "720P", "1080P"],
                    {"default": "1080P"},
                ),
                "duration": ([5, 10], {"default": 5}),
                "prompt_extend": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "是否开启prompt智能改写。开启后使用大模型对输入prompt进行智能改写。对于较短的prompt生成效果提升明显，但会增加耗时。",
                    },
                ),
                "auto_audio": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "是否由模型自动生成声音，优先级低于audio参数。",
                    },
                ),
            },
        }

    NODE_DISPLAY_NAME = "Wan2.5 Image To Video"
    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "actual_prompt")
    CATEGORY = "☁️BizyAir/External APIs/WanVideo"
    FUNCTION = "api_call"

    def api_call(self, image, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])
        prompt_id = extra_data["prompt_id"]
        headers["X-BIZYAIR-PROMPT-ID"] = prompt_id
        headers["X-Bizyair-Async-Result"] = "enable"

        # 参数
        prompt = kwargs.get("prompt", "")
        negative_prompt = kwargs.get("negative_prompt", "")
        audio = kwargs.get("audio", None)
        resolution = kwargs.get("resolution", "1080P")
        duration = kwargs.get("duration", 5)
        prompt_extend = kwargs.get("prompt_extend", True)
        auto_audio = kwargs.get("auto_audio", True)

        input = {}
        if prompt is not None and prompt.strip() != "":
            input["prompt"] = prompt
        if negative_prompt is not None and negative_prompt.strip() != "":
            input["negative_prompt"] = negative_prompt

        # 上传图片&音频
        if image is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}.png&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            input["img_url"] = upload_file_without_sdk(
                tensor_to_bytesio(image), **auth_info
            )
        if audio is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}.flac&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            audio_bytes = save_audio(audio)
            input["audio_url"] = upload_file_without_sdk(audio_bytes, **auth_info)

        # 调用API
        model = "wan2.5-i2v-preview"
        data = {
            "model": model,
            "input": input,
            "parameters": {
                "resolution": resolution,
                "prompt_extend": prompt_extend,
                "duration": duration,
                "audio": auto_audio,
            },
        }

        return wan_create_task_and_wait_for_completion(
            data=data, model=model, prompt=prompt, headers=headers
        )


class Wan_V2_5_T2V_API(BizyAirBaseNode):
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
            },
            "optional": {
                "audio": ("AUDIO",),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "size": (
                    [
                        "832*480",
                        "480*832",
                        "624*624",
                        "1280*720",
                        "720*1280",
                        "960*960",
                        "1088*832",
                        "832*1088",
                        "1920*1080",
                        "1080*1920",
                        "1440*1440",
                        "1632*1248",
                        "1248*1632",
                    ],
                    {"default": "1920*1080"},
                ),
                "duration": ([5, 10], {"default": 5}),
                "prompt_extend": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "是否开启prompt智能改写。开启后使用大模型对输入prompt进行智能改写。对于较短的prompt生成效果提升明显，但会增加耗时。",
                    },
                ),
                "auto_audio": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "是否由模型自动生成声音，优先级低于audio参数。",
                    },
                ),
            },
        }

    NODE_DISPLAY_NAME = "Wan2.5 Text To Video"
    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "actual_prompt")
    CATEGORY = "☁️BizyAir/External APIs/WanVideo"
    FUNCTION = "api_call"

    def api_call(self, prompt, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])
        prompt_id = extra_data["prompt_id"]
        headers["X-BIZYAIR-PROMPT-ID"] = prompt_id
        headers["X-Bizyair-Async-Result"] = "enable"

        # 参数
        negative_prompt = kwargs.get("negative_prompt", "")
        audio = kwargs.get("audio", None)
        size = kwargs.get("size", "1920*1080")
        duration = kwargs.get("duration", 5)
        prompt_extend = kwargs.get("prompt_extend", True)
        auto_audio = kwargs.get("auto_audio", True)

        input = {}
        if prompt is not None and prompt.strip() != "":
            input["prompt"] = prompt
        if negative_prompt is not None and negative_prompt.strip() != "":
            input["negative_prompt"] = negative_prompt

        # 上传音频
        if audio is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}.flac&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            audio_bytes = save_audio(audio)
            input["audio_url"] = upload_file_without_sdk(audio_bytes, **auth_info)

        # 调用API
        model = "wan2.5-t2v-preview"
        data = {
            "model": model,
            "input": input,
            "parameters": {
                "size": size,
                "prompt_extend": prompt_extend,
                "duration": duration,
                "audio": auto_audio,
            },
        }
        return wan_create_task_and_wait_for_completion(
            data=data, model=model, prompt=prompt, headers=headers
        )
