import boto3
import os
PROFILE_BUCKET = {
    "default": "cor-infra-bucket",
    "xxxxxxx": "xxx-infra-bucket",
}
path = r"wordpress-server-construction-with-kusanagi-docker/core-fargate/wordpress-server-construction/kusanagi"
folder = f"cloud-formation/template/kusanagi"


def _get_local_files(path):
    local_files = []
    for root, _, files in os.walk(path):
        for file in files:
            local_files.append(os.path.join(root, file).replace("\\", "/"))
    return local_files


def _upload_file(s3_client, local_files, path, bucket, folder):
    for file_name in local_files:
        object_name = file_name.replace(path, folder)

        s3_client.upload_file(file_name, bucket, object_name)
        print(f"{object_name} は {bucket} にアップロードされた")


def main(profile_name):
    print(f"{profile_name} のアップロード開始")
    region_name: str = "ap-northeast-1"
    session = boto3.Session(profile_name=profile_name,
                            region_name=region_name)
    s3_client = session.client("s3")
    local_files = _get_local_files(path)

    bucket = PROFILE_BUCKET[profile_name]

    _upload_file(s3_client, local_files, path, bucket, folder)


if __name__ == '__main__':

    for profile_name in PROFILE_BUCKET:

        main(profile_name)
