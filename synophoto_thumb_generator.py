#!/usr/bin/python
# -*- coding:UTF-8 -*-

import os
import sys
import subprocess
import argparse
import glob
import json
import time
import datetime

# 定义 ffprobe路径
ffprobe_path = '/var/packages/ffmpeg6/target/bin/ffprobe'
# 定义 视频文件格式
types = ['.mp4','.avi','.wmv','.mkv','.flv','.mov','.rmvb','.amv','.m1v','.m2ts','.m2v','.m4v','.swf','.ts']

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--OverWrite", action="store_true", help="Overwrite SYNOPHOTO_THUMB_X.jpg files even existed")
parser.add_argument("-p", "--path", type=str, help="Specify the directory path to process", default=None)
parser.add_argument("-r", "--repair", action="store_true", help="Try to repair corrupted video files")
parser.add_argument("-s", "--skip_errors", action="store_true", help="Skip problematic files and continue processing")
parser.add_argument("-t", "--time", type=float, help="Specify screenshot time in seconds (default: 1)", default=1)
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
args = parser.parse_args()

# 获取要处理的路径
if args.path:
    process_path = os.path.abspath(args.path)
else:
    # 默认使用脚本所在路径
    process_path = os.path.dirname(os.path.abspath(__file__))

# 创建日志文件
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, f"thumbnail_log.txt")

# 日志函数
def log_message(message, error=False, always_log=False):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {'ERROR: ' if error else ''}{message}"
    
    # 控制台输出
    if error or always_log or args.verbose:
        print(log_entry)
    
    # 日志文件写入 - 现在与控制台输出保持一致
    if error or always_log or args.verbose:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{log_entry}\n")

# 检查视频文件是否有效
def is_valid_video(video_path):
    try:
        cmd = [ffprobe_path, '-v', 'error', '-show_entries', 
               'format=duration', '-of', 'json', video_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            log_message(f"Video validation failed for {video_path}: {result.stderr}", error=True)
            return False
            
        data = json.loads(result.stdout)
        return 'format' in data and 'duration' in data['format']
    except Exception as e:
        log_message(f"Exception during video validation for {video_path}: {str(e)}", error=True)
        return False

# 尝试修复视频文件
def try_repair_video(video_path):
    try:
        repaired_path = f"{video_path}.repaired.mp4"
        
        # 使用ffmpeg尝试修复视频
        cmd = f'ffmpeg -v warning -i "{video_path}" -c copy -movflags faststart "{repaired_path}"'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            log_message(f"Repair failed for {video_path}: {result.stderr}", error=True)
            if os.path.exists(repaired_path):
                os.remove(repaired_path)
            return None
            
        # 验证修复后的文件
        if is_valid_video(repaired_path):
            log_message(f"Successfully repaired {video_path}", always_log=args.verbose)
            return repaired_path
        else:
            log_message(f"Repair attempt did not produce a valid video: {video_path}", error=True)
            if os.path.exists(repaired_path):
                os.remove(repaired_path)
            return None
    except Exception as e:
        log_message(f"Exception during repair attempt for {video_path}: {str(e)}", error=True)
        return None

# 定义函数SynoPhotoThumb，用于生成缩略图
def SynoPhotoThumb(path_to_process):
    log_message(f"Processing directory: {path_to_process}", always_log=True)
    
    # 统计数据
    stats = {
        "processed": 0,
        "skipped": 0,
        "errors": 0,
        "repaired": 0,
        "total": 0
    }
    
    # 用于显示进度的变量
    files_to_process = []
    for dirpath, dirnames, filenames in os.walk(path_to_process):
        if '@eaDir' in dirpath or '#recycle' in dirpath:
            continue
        for name in filenames:
            _, ext = os.path.splitext(name)
            if ext.lower() in types:
                files_to_process.append(os.path.join(dirpath, name))
    
    total_files = len(files_to_process)
    if total_files > 0:
        log_message(f"Found {total_files} video files to process", always_log=True)
    else:
        log_message("No video files found to process", always_log=True)
        return stats
    
    processed_files = 0
    last_progress = -1
    
    # 遍历指定路径下的所有文件和子目录
    for dirpath, dirnames, filenames in os.walk(path_to_process):
        # 跳过@eaDir文件夹和#recycle目录
        dirnames[:] = [d for d in dirnames if d != '@eaDir' and d != '#recycle']
        
        # 如果当前路径包含#recycle，跳过此目录
        if '#recycle' in dirpath:
            continue
            
        # 删除要跳过的文件
        skip_files = ['SYNOPHOTO_FILM_H264.mp4', 'SYNOPHOTO_FILM_M.mp4', 'SYNOPHOTO_FILM_MPEG4.mp4']
        for skip_file in skip_files:
            if skip_file in filenames:
                filenames.remove(skip_file)
        
        # 遍历当前目录下的所有文件
        for name in filenames:
            # 获取文件扩展名
            _, ext = os.path.splitext(name)
            # 如果文件的扩展名在types集合中，那么就为这个文件生成缩略图
            if ext.lower() in types:
                videopath = os.path.join(dirpath, name)
                rootpath = dirpath
                videoname = name
                
                # 增加计数器并显示进度
                processed_files += 1
                current_progress = int(processed_files / total_files * 100)
                if current_progress % 10 == 0 and current_progress != last_progress:
                    log_message(f"Progress: {current_progress}% ({processed_files}/{total_files})", always_log=True)
                    last_progress = current_progress
                
                stats["total"] += 1
                
                # 确保缩略图的目录存在
                thumb_dir = os.path.join(rootpath, '@eaDir', videoname)
                os.makedirs(thumb_dir, exist_ok=True)
                
                thumb_m_path = os.path.join(thumb_dir, 'SYNOPHOTO_THUMB_M.jpg')
                
                # 删除所有.fail文件
                fail_files = glob.glob(os.path.join(thumb_dir, "*.fail"))
                for fail_file in fail_files:
                    try:
                        os.remove(fail_file)
                    except Exception as e:
                        log_message(f"Error removing {fail_file}: {str(e)}", error=True)
                
                # 检查视频文件是否有效
                video_to_use = videopath
                if not is_valid_video(videopath):
                    log_message(f"Invalid video file detected: {videopath}", error=True)
                    
                    if args.repair:
                        repaired_video = try_repair_video(videopath)
                        if repaired_video:
                            video_to_use = repaired_video
                            stats["repaired"] += 1
                        elif not args.skip_errors:
                            log_message(f"Skipping {videopath} due to corruption", error=True)
                            stats["errors"] += 1
                            continue
                    elif not args.skip_errors:
                        log_message(f"Skipping {videopath} due to corruption", error=True)
                        stats["errors"] += 1
                        continue
                
                # 创建SYNOPHOTO_THUMB_M.jpg缩略图
                if (not os.path.exists(thumb_m_path)) or args.OverWrite:
                    # 使用指定秒数的帧作为缩略图
                    shellM = f'ffmpeg -loglevel warning -ss {args.time} -i "{video_to_use}" -y -vframes 1 -vf scale=-1:480 "{thumb_m_path}"'
                    try:
                        resultM = subprocess.run(shellM, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        if resultM.returncode != 0:
                            log_message(f'Error creating thumbnail for {videoname}: {resultM.stderr}', error=True)
                            stats["errors"] += 1
                        else:
                            stats["processed"] += 1
                    except Exception as e:
                        log_message(f'Exception while creating thumbnail for {videoname}: {str(e)}', error=True)
                        stats["errors"] += 1
                else:
                    stats["skipped"] += 1
                
                # 如果使用的是修复后的视频，清理临时文件
                if video_to_use != videopath and os.path.exists(video_to_use):
                    try:
                        os.remove(video_to_use)
                    except Exception as e:
                        log_message(f"Error removing temporary file {video_to_use}: {str(e)}", error=True)
                
                # 检查目录是否为空，如果为空就删除，意味着缩略图创建失败
                try:
                    if os.path.exists(thumb_dir) and not os.listdir(thumb_dir):
                        os.rmdir(thumb_dir)
                except Exception as e:
                    log_message(f"Error checking/removing directory {thumb_dir}: {str(e)}", error=True)
    
    # 打印统计信息
    log_message("=" * 50, always_log=True)
    log_message(f"Process Summary:", always_log=True)
    log_message(f"  Total video files processed: {stats['total']}", always_log=True)
    log_message(f"  Thumbnails successfully created: {stats['processed']}", always_log=True)
    log_message(f"  Files skipped (already exist): {stats['skipped']}", always_log=True)
    log_message(f"  Errors encountered: {stats['errors']}", always_log=True)
    if args.repair:
        log_message(f"  Files successfully repaired: {stats['repaired']}", always_log=True)
    log_message("=" * 50, always_log=True)
    
    return stats

# 执行主函数
start_time = time.time()
log_message("Starting SynoPhotoThumb Generator", always_log=True)
log_message(f"Processing path: {process_path}", always_log=True)
log_message(f"Options: Overwrite={args.OverWrite}, Repair={args.repair}, Skip Errors={args.skip_errors}, Screenshot Time={args.time}s", always_log=True)

stats = SynoPhotoThumb(process_path)

end_time = time.time()
duration = end_time - start_time
log_message(f'SynoPhotoThumb Generator Finished! Total time: {duration:.2f} seconds', always_log=True)
log_message(f'Log file: {log_file}', always_log=True)
