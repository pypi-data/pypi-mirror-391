import os
import json
import zipfile
import inspect
from typing import Dict, Any

def unzip_data():
    package_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    unzipdone_path = os.path.join(package_dir,"data", "unzipdone")  # os.getcwd() 是当前脚本运行目录
    if os.path.exists(unzipdone_path):
        print("already unzipped")
        return
    volume_dir = os.path.join(package_dir, "data")
    volume_prefix = "data.zip"
    output_dir = "./data"
    volume_files = [f for f in os.listdir(volume_dir) if f.startswith(volume_prefix)]
    volume_files.sort(key=lambda x: int(x.split('.')[-1]) if x.split('.')[-1].isdigit() else 999)
    if not volume_files:
        raise FileNotFoundError(f"未找到前缀为 {volume_prefix} 的分卷文件")
    merged_zip_path = f"{volume_prefix}.merged.zip"  # 合并后的临时文件
    with open(merged_zip_path, 'wb') as merged_zip:
        for vol_file in volume_files:
            vol_path = os.path.join(volume_dir, vol_file)
            print(f"正在合并分卷：{vol_path}")
            with open(vol_path, 'rb') as f:
                merged_zip.write(f.read())  # 逐字节写入合并
    os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在
    with zipfile.ZipFile(merged_zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
        print(f"解压完成！文件已保存到：{output_dir}")
    os.remove(merged_zip_path)
    print(f"已删除临时合并文件：{merged_zip_path}")
    with open(unzipdone_path, 'w') as f:
        # 可写入解压完成时间（可选），也可以留空（仅作为标记）
        f.write(f"解压完成时间：{os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}")

def load_survey_papers() -> Dict[str, Any]:
    unzip_data()
    package_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    data_file_path = os.path.join(package_dir, "data", "surveys_arxiv_paper_db.json")
    with open(data_file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_survey_paper_ids() -> list:
    data = load_survey_papers()
    return list(data.get("survey_paper_info", {}).keys())

def get_survey_paper_by_id(paper_id: str) -> Dict[str, Any]:
    data = load_survey_papers()
    return data.get("survey_paper_info", {}).get(paper_id, {})

def load_arxiv_papers() -> Dict[str, Any]:
    unzip_data()
    package_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    data_file_path = os.path.join(package_dir, "data", "arxiv_paper_db_with_cc.json")
    with open(data_file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_arxiv_paper_ids() -> list:
    data = load_survey_papers()
    return list(data.get("cs_paper_info", {}).keys())

def get_arxiv_paper_by_id(paper_id: str) -> Dict[str, Any]:
    data = load_survey_papers()
    return data.get("cs_paper_info", {}).get(paper_id, {})