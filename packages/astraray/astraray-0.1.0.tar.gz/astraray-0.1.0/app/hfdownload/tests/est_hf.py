import os

from app.hfdownload.hf import HFDownload


def test_hf_download_real():
    """
    真实环境测试：验证HFDownload能正确获取并下载指定的.md文件。
    """
    # 配置下载参数
    # 重要：请将此repo_id替换为一个你确定包含.md文件且允许访问的公开仓库
    test_repo_id = "Comfy-Org/Qwen-Image_ComfyUI"  # 示例仓库，请按需更改
    # 指定本地存储目录
    local_download_dir = r"D:\qwen_im"  # 可更改为你希望的路径

    hf_downloader = HFDownload(
        repo_id=test_repo_id,
        repo_type="model",
        local_dir=local_download_dir,
        endpoint="https://huggingface.co",  # 国内用户可考虑使用 "https://hf-mirror.com"
        allow_patterns=[".*md"],  # 允许所有Markdown文件
        ignore_patterns=[".*safetensors"],  # 忽略Safetensors模型文件
        revision="main",
    )

    # 指定要扫描的远程目录，例如根目录或某个子目录（如"split_files"）
    target_remote_dir = (
        "."  # 从仓库根目录开始。如果测试特定子文件夹，可改为 "split_files"
    )

    print(
        f"开始扫描仓库 {test_repo_id} 中的文件 (目录: '{target_remote_dir}')..."
    )
    print(
        "文件匹配规则: allow_patterns='.*md', ignore_patterns='.*safetensors'"
    )
    print("-" * 60)

    try:
        # 调用生成器，设置 is_recursive=True 以递归搜索，is_download=True 以下载文件
        downloaded_files = []
        for (
            remote_file_path,
            local_save_path,
        ) in hf_downloader.get_files_in_dir(
            target_remote_dir, is_recursive=True, is_download=True
        ):
            print(f"[找到匹配文件] 远程路径: {remote_file_path}")
            print(f"          保存至: {local_save_path}")
            downloaded_files.append((remote_file_path, local_save_path))
            print("-" * 40)

        # 测试结果总结
        print("\n" + "=" * 60)
        print("测试完成！")
        print(f"总共找到并下载了 {len(downloaded_files)} 个匹配的.md文件。")

        # 验证：检查文件是否确实下载到本地
        if downloaded_files:
            print("\n本地文件验证:")
            for remote_path, local_path in downloaded_files:
                if os.path.exists(local_path):
                    print(f"[✓] 文件已成功下载: {os.path.basename(local_path)}")
                else:
                    print(f"[!] 文件未找到，可能下载失败: {local_path}")
        else:
            print(
                "未找到任何匹配的.md文件。这可能是因为指定目录下没有.md文件，或者allow_patterns/ignore_patterns设置过于严格。"
            )

    except Exception as e:
        print(f"\n[!] 测试过程中发生错误: {e}")
