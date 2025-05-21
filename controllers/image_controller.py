from pathlib import Path
from urllib.request import urlretrieve
from settings import IMG_DIR


def progress(block_num: float, block_size: float, total_size: float):
    downloaded = block_num * block_size
    percent = min(int(100 * downloaded / total_size), 100)
    print(f"\r{percent}% [{downloaded}/{total_size}]", end="")


def get_image_path(os_variant: str) -> Path:
    if os_variant == "ubuntu20.04":
        version = "20.04"
    elif os_variant == "ubuntu22.04":
        version = "22.04"
    elif os_variant == "ubuntu24.04":
        version = "24.04"
    else:
        raise Exception(f"OS variant '{os_variant}' doesn't exist.")
    
    return Path(f"{IMG_DIR}/ubuntu-{version}-server-cloudimg-amd64.img")


def download_from_url(target_url: str, target_path: Path):
    try:
        target_url = f"{target_url}"
        if not target_path.is_file():
            print(f"'{target_path.name}' image not found\nStarting download...")
            urlretrieve(target_url, target_path, reporthook=progress)
            print("")
        else:
            print(f"Found image `{target_url}`.")
    except Exception as e:
        print(f"Couldn't download file `{target_url}`: {e}")


def import_image(os_variant: str = "ubuntu22.04"):
    image_path = get_image_path(os_variant)

    if os_variant == "ubuntu20.04":
        target_url = f"https://cloud-images.ubuntu.com/releases/20.04/release/{image_path.name}"
    elif os_variant == "ubuntu22.04":
        target_url = f"https://cloud-images.ubuntu.com/releases/22.04/release/{image_path.name}"
    elif os_variant == "ubuntu24.04":
        target_url = f"https://cloud-images.ubuntu.com/releases/24.04/release/{image_path.name}"

    download_from_url(
        target_url=target_url,
        target_path=image_path
    )
