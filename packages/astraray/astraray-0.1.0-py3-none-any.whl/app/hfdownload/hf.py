# /// script
# dependencies = [
#   "huggingface-hub",
# ]
# ///

try:
    import dotenv

    dotenv.load_dotenv("./.env", override=True)
except Exception as e:
    print(e)

import os
import re
from pathlib import Path
from typing import Generator, Literal

from huggingface_hub import HfFileSystem

HF_TOKEN = os.environ.get("HF_TOKEN")  # 官方环境变量
HUGGINGFACE_TOKEN = os.environ.get(
    "HUGGINGFACE_TOKEN"
)  # 社区和部分依赖习惯用名

# transformers自动下载模型要在import transformers之前，设置HF_ENDPOINT环境变量
# os.environ["XDG_CACHE_HOME"] = user_setting["XDG_CACHE_HOME"]
# os.environ["MODELSCOPE_CACHE"] = f"{user_setting['XDG_CACHE_HOME']}/modelscope"  # ms-swift这个训练大模型的项目可设置MODELSCOPE_CACHE改模型和数据集下载路径，因为是基于modelscope的
# os.environ["HF_ENDPOINT"] = https://hf-mirror.com

# 输token : huggingface-cli login  改为hf auth login --token $HF_TOKEN --add-to-git-credential
# 查询登录用户名：hf auth whoami


class HFDownload:
    def __init__(
        self,
        repo_id: str,
        local_dir: str | Path,
        repo_type: Literal["model", "dataset"] = "model",
        allow_patterns: list[str] | None = None,
        ignore_patterns: list[str] | None = None,
        endpoint: Literal[
            "https://huggingface.co", "https://hf-mirror.com"
        ] = "https://huggingface.co",
        token: bool | str | None = None,
        revision: str | None = None,
    ) -> None:
        """
        初始化仓库对象

        Args:
            repo_id (str): 仓库ID
            local_dir (str | Path): 本地目录路径
            repo_type (Literal["model", "dataset"], optional): 仓库类型，默认为"model"。可以是"model"或"dataset"。
            allow_patterns (list[str], optional): 允许的正则表达式列表，默认为None。 注意:是远程仓库的hf全路径做正则
            ignore_patterns (list[str], optional): 忽略的正则表达式列表，默认为None。 注意:是远程仓库的hf全路径做正则
            endpoint (Literal["https://huggingface.co", "https://hf-mirror.com"], optional): 端点，默认为"https://huggingface.co"。
            token (bool | str | None, optional): 访问令牌，默认为None。
            revision (str | None, optional): 版本号，默认为None。
        """
        if token is not None:
            self.token = token
        elif HF_TOKEN != "":
            self.token = HF_TOKEN
        elif HUGGINGFACE_TOKEN != "":
            self.token = HUGGINGFACE_TOKEN
        else:
            self.token = None

        self.repo_id = repo_id

        if isinstance(local_dir, str):
            self.local_dir = Path(local_dir)
        if repo_type == "dataset":
            self.repo_type = "datasets/"
        else:
            self.repo_type = ""
        self.header = f"{self.repo_type}{self.repo_id}".split("/")

        self.revision = revision
        self.allow_patterns = allow_patterns
        self.ignore_patterns = ignore_patterns
        self.fs = HfFileSystem(token=self.token, endpoint=endpoint)

    def _match_path(self, string: str) -> bool:
        try:
            if self.ignore_patterns is not None:
                if len(self.ignore_patterns) > 0:
                    for pattern in self.ignore_patterns:
                        if re.match(pattern, string):
                            return False

            res = False
            if self.allow_patterns is not None:
                if len(self.allow_patterns) > 0:
                    for pattern in self.allow_patterns:
                        if re.match(pattern, string):
                            res = True
                            break
                else:
                    res = True
            else:
                res = True
            return res
        except Exception as e:
            raise ValueError(f"{e} ignore_patterns或allow_patterns格式错误")

    def get_files_in_dir(
        self,
        dir_path: str,
        is_recursive: bool = True,
        is_download: bool = False,
        is_resume_download: bool = True,
    ) -> Generator[tuple[str, Path], None, None]:
        if dir_path != "":
            dir_path = f"/{dir_path}"
        else:
            pass
        paths = self.fs.ls(
            f"{self.repo_type}{self.repo_id}{dir_path}",
            detail=False,
            revision=self.revision,
        )
        for path in paths:
            if self.fs.isfile(path):
                if self._match_path(path):
                    save_path = path.split("/")[len(self.header) :]
                    save_path = "/".join(save_path)
                    save_path = self.local_dir / save_path
                    if is_download:
                        if is_resume_download:
                            expected_size = self.fs.info(
                                path, revision=self.revision
                            )["size"]
                            if save_path.exists():
                                local_size = save_path.stat().st_size
                                # print(f"{local_size}/{expected_size}")
                                if local_size != expected_size:
                                    self.fs.get_file(
                                        rpath=path, lpath=save_path
                                    )
                                else:
                                    pass
                            else:
                                self.fs.get_file(rpath=path, lpath=save_path)
                        else:
                            self.fs.get_file(rpath=path, lpath=save_path)
                    yield (path, save_path)
            else:
                if is_recursive:
                    temp_dir_path = path.split("/")[len(self.header) :]
                    temp_dir_path = "/".join(temp_dir_path)
                    yield from self.get_files_in_dir(
                        dir_path=temp_dir_path,
                        is_recursive=is_recursive,
                        is_download=is_download,
                        is_resume_download=is_resume_download,
                    )


if __name__ == "__main__":
    hf = HFDownload(
        repo_id="Comfy-Org/Qwen-Image_ComfyUI",
        repo_type="model",
        local_dir=r"D:\qwen_im",
        endpoint="https://hf-mirror.com",  # "https://huggingface.co",
        allow_patterns=[".*"],
        ignore_patterns=[
            ".*qwen_image_bf16.safetensors",
            ".*qwen_2.5_vl_7b.safetensors",
        ],
        revision="main",
    )

    for file, savepath in hf.get_files_in_dir(
        "split_files", is_recursive=True, is_download=True
    ):
        print(file)
        pass
