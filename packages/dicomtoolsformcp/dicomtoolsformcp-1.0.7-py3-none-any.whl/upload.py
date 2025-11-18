#!/usr/bin/env python3
"""
DICOM 工具 MCP 服务器主文件

基于 MCP (Model Context Protocol) 的 DICOM 医学影像文件分析工具的Python实现。
"""
import shutil
from pathlib import Path

import logging
import sys
from typing import Any, Dict
import json
from argparse import Namespace


from src.models import DICOMDirectory
from src.utils import create_upload_config
from src.core import (
    get_series_info,
    should_upload_series,
    upload_series_metadata,
    upload_dicom_files
)
from getcookie import CookieManager
# 配置MCP服务器所需的导入
try:
    from mcp.server import Server
    from mcp.server.sse import SseServerTransport
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    from pydantic import BaseModel
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import Response
except ImportError as e:
    print(f"错误: 缺少必要的MCP依赖库: {e}", file=sys.stderr)
    print("请运行: pip install mcp starlette uvicorn", file=sys.stderr)
    sys.exit(1)

# 导入DICOM工具
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))




# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例



def main():
    """输入用户名和密码修改config.json"""
    DEFAULT_CONFIG: Dict[str, Any] = {
        "max_workers": 10,
        "max_retries": 3,
        "DEFAULT_CONNECT_TIMEOUT": 3,
        "DEFAULT_READ_TIMEOUT": 5,
        "DEFAULT_RETRY_DELAY": 5,
        "DEFAULT_BATCH_SIZE": 6
    }

    import os
    from dotenv import load_dotenv
    load_dotenv()
    name=os.getenv("name")
    password=os.getenv("password")
    tel=os.getenv("tel")
    base_url=os.getenv("base_url")

    from getcrpit import encrypt
    payload = {"username": name, "password": password, "phoneNumber": tel}
    plain = json.dumps(payload, ensure_ascii=False)
    cipher = encrypt(plain)
    cookie_manager = CookieManager(base_url, cipher)
    cookie = cookie_manager.get_cookie()
    if cookie:
        DEFAULT_CONFIG["cookie"]=cookie
        DEFAULT_CONFIG["base_url"]=base_url
        print(f":配置详情{DEFAULT_CONFIG}")

    return DEFAULT_CONFIG

def process_single_series(
        series,
        series_count: int,
        patient_name: str,
        series_type: int,
        base_url: str,
        cookie: str,
        upload_config: Namespace,
        api_url: str,
        use_series_uid: bool = False
) -> bool:
    """
    Process and upload a single DICOM series.

    Args:
        series: DICOM series object
        series_count: Series counter
        patient_name: Patient name
        series_type: Series type
        base_url: Base URL
        cookie: Authentication cookie
        upload_config: Upload configuration
        api_url: API URL for querying
        use_series_uid: Whether to use series UID as patient name

    Returns:
        bool: True if processed successfully, False otherwise
    """
    series_info = get_series_info(series)

    # 如果需要使用 series UID，则覆盖 patient_name
    if use_series_uid:
        patient_name = series_info["PatientID"]

    series_desc = (
        f"{series_info['SeriesDescription']} "
        f"({series_info['SliceNum']} 切片)"
    )
    print(f"\n{'=' * 60}")
    print(f"序列 {series_count}: {series_desc}")
    print(f"Patient Name: {patient_name}")
    print(f"{'=' * 60}")

    if not should_upload_series(series_info):
        print("X 序列不符合上传标准，跳过...")
        return False

    print("* 符合标准，开始上传流程...\n")

    # Step 1: Upload initial metadata (status 11)
    try:
        print("[1/3] 上传初始元数据...")
        metadata = upload_series_metadata(
            series_info, patient_name, series_type, 11, base_url, cookie, verbose=False
        )

        print("\n[2/3] 上传DICOM文件...")
        upload_dicom_files(series, upload_config, verbose=False)
        print("\n[3/3] 上传最终元数据...")
        metadata = upload_series_metadata(
            series_info, patient_name, series_type, 12, base_url, cookie, verbose=False
        )
        return True
    except Exception as e:
        print(f"\n[错误] 序列 {series_count} 上传失败: {e}\n")
        return False


def test(directory_path,DEFAULT_CONFIG,series_type):

    config = DEFAULT_CONFIG

    # Initialize basic parameters

    directory = directory_path
    base_url = config['base_url']
    if config['cookie'].startswith("ls="):
        cookie = config['cookie']
    else:
        cookie = "ls=" + config['cookie']
    # series_type = config['series_type']
    series_type = int(series_type)
    patient_name = config.get('patient_name', None)
    use_series_uid = patient_name is None  # 如果 patient_name 未设置，则使用 series UID
    if patient_name is None:
        patient_name = 'default'  # 默认值，会被 series UID 覆盖
    api_url = f"{base_url}/api/v2/getSeriesByStudyInstanceUID"

    # Create upload configuration
    upload_config = create_upload_config(config)

    # Initialize DICOM directory
    print(f"扫描 DICOM 目录: {directory}")
    dicom_directory = DICOMDirectory(directory)

    # Get all series
    all_series = list(dicom_directory.get_dicom_series())
    total_series = len(all_series)
    print(f"发现 {total_series} 个序列\n")

    # Process each series
    successful_uploads = 0
    skipped_series = 0
    failed_series = 0
    patient_num = []
    error_messages = []  # 收集错误信息
    if len(all_series)>1:
        for series_count, series in enumerate(all_series, start=1):
            series_info = get_series_info(series)
            patient_num.append(series_info["PatientID"])
        dit={"message":f"当前文件夹包含{len(all_series)}个序列，建议先进行序列拆分，上传单个文件夹"}
        return {
            "content": [
                {
                "type": "text",
                "text": json.dumps(dit, ensure_ascii=False, indent=2)
                }
            ]
        }
    else:
        series_count=1
        series=all_series[0]

        series_info = get_series_info(series)
        patient_num.append(series_info)
        try:
            success = process_single_series(
                    series=series,
                    series_count=series_count,
                    patient_name=patient_name,
                    series_type=series_type,
                    base_url=base_url,
                    cookie=cookie,
                    upload_config=upload_config,
                    api_url=api_url,
                    use_series_uid=use_series_uid
            )
            if success:
                successful_uploads += 1
            else:
                skipped_series += 1
        except Exception as e:
            error_msg = f"序列 {series_count} ({series_info.get('SeriesDescription', 'Unknown')}): {str(e)}"
            print(f"\n[错误] 处理序列 {series_count} 时出错: {e}\n")
            error_messages.append(error_msg)
            failed_series += 1
    series_info = get_series_info(series)
    study_uid = series_info["StudyInstanceUID"]
    SeriesInstanceUID = series_info["SeriesInstanceUID"]

    # 构建返回结果
    dic = {
        "successful_uploads": successful_uploads,
        "totalPatients": 1,
        "patients": f"{patient_num[0]}",
        "view_url": f"{config['base_url']}/study/studylist",
        "directory_path":directory,
        "study_uid":study_uid,
        "SeriesInstanceUID":SeriesInstanceUID,
        "type":series_type
    }
    import pandas as pd
    import os

    # ... (函数 test 内部的其他代码)

    dic = {
        "successful_uploads": successful_uploads,
        "totalPatients": 1,
        "patients": f"{patient_num[0]}",
        "view_url": f"{config['base_url']}/study/studylist",
        "directory_path": directory,
        "study_uid": study_uid,
        "SeriesInstanceUID": SeriesInstanceUID,
        "type": series_type
    }

    # --- 将字典写入 XLSX 文件的代码 ---
    try:
        output_filename = 'log/upload_log.xlsx'


        # 将字典转换为 DataFrame
        # patient_num[0] 是一个字典，我们将其转换为字符串以便写入
        dic_for_excel = dic.copy()
        dic_for_excel['patients'] = str(dic_for_excel['patients'])

        df_new = pd.DataFrame([dic_for_excel])

        # 如果文件已存在，则读取并追加；否则，创建新文件
        if os.path.exists(output_filename):
            with pd.ExcelWriter(output_filename, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                # 获取最后一行的行号
                startrow = writer.book.worksheets[0].max_row
                # 追加数据，不写入表头
                df_new.to_excel(writer, index=False, header=False, startrow=startrow)
        else:
            # 创建新文件并写入数据（包含表头）
            df_new.to_excel(output_filename, index=False)

        print(f"结果已成功写入到 '{output_filename}'")

    except Exception as e:
        print(f"写入 Excel 文件时出错: {e}")

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(dic, ensure_ascii=False, indent=2)
            }
        ]
    }


def copy_dicom(src_path: str, dest_dir: str) -> Path:
    src = Path(src_path)
    dest_folder = Path(dest_dir)
    if not src.exists():
        raise FileNotFoundError(f"源文件不存在: {src}")
    dest_folder.mkdir(parents=True, exist_ok=True)

    dest = dest_folder / src.name
    if dest.exists():
        stem = src.stem
        suffix = src.suffix
        i = 1
        while True:
            candidate = dest_folder / f"{stem}_copy{i}{suffix}"
            if not candidate.exists():
                dest = candidate
                break
            i += 1

    shutil.copy2(src, dest)
    return dest

def get_result(directory_path):
    DEFAULT_CONFIG=main()
    import pandas as pd
    import os
    config=main()
    # --- 从 Excel 文件读取 study_uid ---
    cookie="ls="+config["cookie"]
    api_url=config["base_url"]
    dit={}
    api_url=api_url+'/api/v2/getSeriesByStudyInstanceUID'
    try:
        output_filename = 'log/upload_log.xlsx'
        if not os.path.exists(output_filename):
            print(f"错误: 日志文件 '{output_filename}' 不存在。")
            return

        df = pd.read_excel(output_filename)
        # 确保 directory_path 列是字符串类型以便比较
        df['directory_path'] = df['directory_path'].astype(str)

        # 查找匹配的行
        result_row = df[df['directory_path'] == directory_path]

        if result_row.empty:
            dit["message"]=f"未找到与目录路径 '{directory_path}' 匹配的记录,请先上传进行分析。"
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(dit, ensure_ascii=False, indent=2)
                    }
                ]
            }

        # 获取 study_uid
        study_uid = result_row.iloc[0]['study_uid']
        SeriesInstanceUID= result_row.iloc[0]['SeriesInstanceUID']
        type= result_row.iloc[0]['type']
        dit={"study_uid":study_uid,"SeriesInstanceUID":SeriesInstanceUID}
        print(f"从日志文件中找到 StudyInstanceUID: {study_uid}")

    except Exception as e:
        dit["message"]=f"未找到与目录路径 '{directory_path}' 匹配的记录,请先上传进行分析。"
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(dit, ensure_ascii=False, indent=2)
                }
            ]
        }


    def query_result(study_uid):
        study_uid, series_uid, s_type, status = find_result(
            api_url, study_uid, cookie
        )
        return status
    #查询结果输出
    from src.api.query_api import find_result
    import time
    print("查询上传结果...")
    re=False
    for i in range(120):
        status=query_result(study_uid)
        print(f"查询状态: {status}, StudyInstanceUID: {study_uid}")
        if status is not None:
            if int(status)==42:
                re=True
                print("查询成功")
                break
            elif int(status)==44:
                break

        else:
            print("查询失败")
            break
        time.sleep(1)
    if re==True:
        dit["url"]=f"{config['base_url']}/viewer/{study_uid}?seriesInstanceUID={SeriesInstanceUID}&type={type}&status=42"
    else:
        dit["message"]=f"查询超时，请稍后在系统中查看结果:{config['base_url']}/study/studylist"
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(dit, ensure_ascii=False, indent=2)
            }
        ]
    }



def separate_series_by_patient(directory_path):
    dicom_directory = DICOMDirectory(directory_path)
    all_series = list(dicom_directory.get_dicom_series())

    # 按患者分组
    patient_series_map = {}
    for series in all_series:
        info = get_series_info(series)
        pid = info["PatientID"]
        patient_series_map.setdefault(pid, []).append(series)

    # 为每个患者和序列创建目录并复制文件
    base_path = Path(directory_path)
    sucess_num=0
    main_dir=[]
    for pid, series_list in patient_series_map.items():
        p_dir = base_path / pid
        p_dir.mkdir(parents=True, exist_ok=True)
        main_dir.append(p_dir)
        for series in series_list:
            info = get_series_info(series)
            series_uid = info.get("SeriesInstanceUID", "unknown_series")
            s_dir = p_dir / series_uid
            s_dir.mkdir(parents=True, exist_ok=True)

            for instance in getattr(series, "instances", []):
                # 支持常见的实例路径属性名
                src = (
                    getattr(instance, "filepath", None)
                    or getattr(instance, "file_path", None)
                    or getattr(instance, "path", None)
                )
                if not src:
                    logger.warning(f"实例缺少路径: patient={pid}, series={series_uid}")
                    continue

                try:
                    if copy_dicom(src, s_dir):
                        sucess_num += 1
                except Exception as e:
                    logger.exception(f"复制失败: {src} -> {s_dir}: {e}")

    message=f"已为 {len(patient_series_map)} 位患者分离 {len(all_series)} 个序列，成功复制 {sucess_num} 个文件。"
    dic={
        "totalPatients": len(patient_series_map),
        "totalSeries": len(all_series),
        "totalFilesCopied": sucess_num,
        "message": message,
        "newDirectory": f"{main_dir}"
    }
    return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(dic, ensure_ascii=False)
                }
            ]
    }

async def Analysis_dicom_directory_tool(directory_path,series_type):
    "seriers_type:1主动脉9为二尖瓣"
    try:
        return test(directory_path,main(),series_type)
    except Exception as e:
        import traceback
        error_info = f"处理过程中发生错误: {str(e)}\n详细信息:\n{traceback.format_exc()}"
        return {
            "content": [
                {
                    "type": "text",
                    "text": error_info
                }
            ]
        }

async def separate_series_by_patient_tool(directory_path):
    directory_path=fr'{directory_path}'
    try:
        return separate_series_by_patient(directory_path)
    except Exception as e:
        import traceback
        error_info = f"处理过程中发生错误: {str(e)}\n详细信息:\n{traceback.format_exc()}"
        return {
            "content": [
                {
                    "type": "text",
                    "text": error_info
                }
            ]
        }

async def get_result_tool(directory_path):
    directory_path=fr'{directory_path}'
    try:
        return get_result(directory_path)
    except Exception as e:
        import traceback
        error_info = f"处理过程中发生错误: {str(e)}\n详细信息:\n{traceback.format_exc()}"
        return {
            "content": [
                {
                    "type": "text",
                    "text": error_info
                }
            ]
        }

if __name__ == "__main__":
    # print(test(fr'C:\Users\13167\Desktop\数据\0009637617\1.3.12.2.1107.5.1.4.76315.30000021042706150001900118114',main(),1))
    print(get_result(fr'C:\Users\13167\Desktop\数据\0009637617\1.3.12.2.1107.5.1.4.76315.30000021042706150001900118114'))
    #print(separate_series_by_patient(fr'C:\Users\13167\Desktop\数据'))