# SynoPhotoThumb Generator

一个用于Synology NAS的Python脚本，用于自动生成视频文件的缩略图，使它们在Synology Photos中正确显示。

## 功能特点

- 批量为视频文件生成SYNOPHOTO_THUMB_M.jpg缩略图
- 自动删除.fail文件，修复Photos中的视频预览问题
- 支持多种视频格式：mp4, avi, wmv, mkv, flv, mov等
- 可自定义截图时间点
- 支持损坏视频文件的检测和修复
- 自动跳过回收站(#recycle)目录
- 简洁的进度显示和错误报告

## 使用要求

- Synology NAS设备
- ffmpeg 6 已安装（通常通过Synology套件中心安装）
- Python 3.x

## 使用方法

1. 将脚本下载到您的NAS
2. 通过SSH连接到NAS，或在NAS上的任务计划中执行
3. 运行脚本，使用以下命令和参数

### 命令行参数

```
python synophoto_thumb_generator.py [-h] [-o] [-p PATH] [-r] [-s] [-t TIME] [-v]

可选参数:
  -h, --help            显示帮助信息
  -o, --OverWrite       覆盖已存在的缩略图文件
  -p PATH, --path PATH  指定要处理的目录路径，默认为脚本所在目录
  -r, --repair          尝试修复已损坏的视频文件
  -s, --skip_errors     遇到问题文件时跳过并继续处理其他文件
  -t TIME, --time TIME  指定截图时间点（秒），默认为1秒
  -v, --verbose         启用详细日志记录
```

### 使用示例

```bash
# 基本使用，处理指定目录
python synophoto_thumb_generator.py -p /volume1/photo

# 处理指定目录并尝试修复损坏的视频
python synophoto_thumb_generator.py -p /volume1/photo -r

# 处理指定目录，跳过错误文件，使用视频的第5秒作为缩略图
python synophoto_thumb_generator.py -p /volume1/photo -s -t 5

# 处理指定目录并强制覆盖所有现有缩略图
python synophoto_thumb_generator.py -p /volume1/photo -o

# 启用详细日志输出
python synophoto_thumb_generator.py -p /volume1/photo -v
```

## 日志和故障排除

- 脚本在执行目录下创建带时间戳的日志文件
- 默认情况下，只记录错误信息和处理摘要
- 使用-v参数可以启用详细日志
- 错误信息会提供详细的故障描述，有助于排除问题

## 工作原理

1. 扫描指定目录下的所有视频文件
2. 为每个视频文件创建@eaDir目录结构
3. 使用ffmpeg从视频中提取指定时间点的帧作为缩略图
4. 删除所有.fail文件
5. 生成处理统计和日志报告

## 注意事项

- 脚本会自动跳过Synology系统生成的特殊文件，如SYNOPHOTO_FILM_H264.mp4等
- 对于无法正常读取的视频文件，可以尝试使用-r参数修复
- 处理大量视频文件时，可能需要较长时间
- 建议先在小范围测试后再处理大量文件

## 常见问题

**Q: 生成缩略图后在Photos中仍然看不到预览**  
A: 尝试使用-o参数重新生成缩略图，并确保删除了.fail文件

**Q: 脚本报告"moov atom not found"错误**  
A: 这表示视频文件损坏，尝试使用-r参数修复

**Q: 如何在任务计划中自动运行?**  
A: 在Synology控制面板的任务计划中创建用户定义的脚本，指定完整的Python路径和脚本路径

## 许可证

此脚本供个人使用，请遵循相关软件的使用条款。

## 致谢

- 感谢 https://zhuanlan.zhihu.com/p/5825221275 
