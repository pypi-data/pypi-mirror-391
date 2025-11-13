@echo off
REM 关闭命令回显，使输出更简洁

REM 创建 data 目录（若不存在）
mkdir data 2>nul

REM 下载 SyncNet 模型文件到 data 目录
echo 正在下载 syncnet_v2.model...
curl -fL "http://www.robots.ox.ac.uk/~vgg/software/lipsync/data/syncnet_v2.model" -o "data\syncnet_v2.model"

REM 下载示例视频文件到 data 目录
echo 正在下载 example.avi...
curl -fL "http://www.robots.ox.ac.uk/~vgg/software/lipsync/data/example.avi" -o "data\example.avi"

REM 创建 detectors/s3fd/weights 嵌套目录（若不存在）
mkdir detectors\s3fd\weights 2>nul

REM 下载人脸检测器权重文件到对应目录
echo 正在下载 sfd_face.pth...
curl -fL "https://www.robots.ox.ac.uk/~vgg/software/lipsync/data/sfd_face.pth" -o "detectors\s3fd\weights\sfd_face.pth"

echo 所有文件下载完成！