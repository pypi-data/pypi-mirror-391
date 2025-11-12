from webdav3.client import Client
from webdav3.exceptions import LocalResourceNotFound, RemoteResourceNotFound, ResponseErrorCode


def webdav_client(webdav_config: dict, operate: str, remote_path, local_path):
    """
    webdav_config: 配置webdav，字典类型，包含键：webdav_hostname、webdav_login、webdav_password
    operate：操作，包含：download,upload
    remote_path：远程路径
    local_path：本地路径
    """
    try:
        # 配置WebDAV，创建WebDAV客户端实例
        client = Client(webdav_config)
        # 关闭检查，否则无法上传文件
        client.webdav.disable_check = True
        match operate:
            case "download": client.download(remote_path, local_path)
            case "upload": client.upload(remote_path, local_path)

    except RemoteResourceNotFound:
        print("未发现远程目标文件，请检查路径是否正确。")
    except LocalResourceNotFound:
        print("未发现本地文件，请检查路径是否正确。")
    except ResponseErrorCode as e:
        print(e.code)
