import os
import logging
from datetime import datetime
import csv
import numpy as np
import time
from stimbposd import BPOSD
from hamld.benchmark.utility import parse_b8, b8_to_array
import stim
# 设置 logging 配置，放在模块级别
from hamld.logging_config import setup_logger

logger = setup_logger("qLDPC/qldpc_decode_bposd_acc", log_level=logging.INFO)

def main():
    # 设置输入数据的相关路径
    stim_dir = "/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_circuit"
    dem_dir = "/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_dem"
    dat_dir = "/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_dat"

    # 设置输出目录
    output_dir = "/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_result"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"overall_performance_qldpc_code_acc_no_decode_results_{timestamp}.csv")

    # 设置待测试的解码方法：
    decoder_methods = ["BP+OSD"]
    have_stabilizer = False  # 根据需要调整

    # BP+OSD 初始化参数
    max_bp_iters = 100
    osd_method = "osd_cs"
    osd_order = 10

    # 创建存储结果的CSV文件并写入表头
    fieldnames = ['task_name', 'decoder_method', 'logical_error_rate', 'have_stabilizer', 'total_running_time']
    # 如果文件不存在，写入表头
    if not os.path.exists(output_file):
        with open(output_file, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    # 使用 with 来避免每次打开文件
    with open(output_file, mode='a', newline='') as f:  # 使用 'a' 追加模式，避免覆盖
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        # 如果文件为空，写入表头（但由于'a'模式，可能需要检查）
        if os.path.getsize(output_file) == 0:
            writer.writeheader()
        
        # 添加打印信息
        logger.info("Starting the benchmark process...")

        for filename in os.listdir(stim_dir):
            if filename.endswith('.stim') and 'without_measure' not in filename and "Z" in filename and "bb" in filename:
                logger.info(f"Processing file: {filename}")
                task_name = filename.replace('.stim', '')
                dem_filename = filename.replace('.stim', '.dem')
                dem_file = os.path.join(dem_dir, dem_filename)

                if not os.path.exists(dem_file):
                    logger.warning(f"DEM file not found: {dem_file}. Skipping.")
                    continue

                # 加载DEM
                try:
                    dem = stim.DetectorErrorModel.from_file(dem_file)
                    logger.info(f"Loaded DEM with {dem.num_detectors} detectors and {dem.num_observables} observables")
                except Exception as e:
                    logger.error(f"Error loading DEM {dem_file}: {e}. Skipping.")
                    continue

                if dem.num_observables >= 30:
                    logger.info(f"Skipping {filename} due to too many observables: {dem.num_observables}")
                    continue

                dat_filename = filename.replace('.stim', '.dat')
                dat_file = os.path.join(dat_dir, dat_filename)
                if not os.path.exists(dat_file):
                    logger.warning(f"DAT file not found: {dat_file}. Skipping.")
                    continue
                
                # 加载data文件
                with open(dat_file, 'rb') as f:
                    data = f.read()

                # 计算每shot的比特数
                bits_per_shot = dem.num_detectors + dem.num_observables
                # 解析 b8 格式数据
                shots = parse_b8(data, bits_per_shot)

                # 将解析结果转换为 numpy 数组
                syndrome, actual_observables = b8_to_array(shots, logical_num=dem.num_observables)
            
                num_shots = syndrome.shape[0]
                logger.info(f"Loaded {num_shots} shots from {dat_file}")

                # decoder = BPOSD(dem, max_bp_iters=max_bp_iters, osd_method=osd_method, osd_order=osd_order)
                
                # start_time = time.time()
                # predicted_observables = decoder.decode_batch(syndrome)
                # end_time = time.time()
                # total_running_time = end_time - start_time
            
                mistakes_mask = np.any(actual_observables != 0, axis=1)
                num_mistakes = np.sum(mistakes_mask)
                
                logical_error_rate = num_mistakes / num_shots
                
                logger.info(f"Decoded {num_shots} shots, mistakes: {num_mistakes}")
                logger.info(f"Logical Error Rate for {task_name}: {logical_error_rate}, total_running_time: {0}")
                
                # 将结果写入CSV文件
                writer.writerow({
                    'task_name': task_name,
                    'decoder_method': "No Decode",  # 假设只有一个
                    'logical_error_rate': logical_error_rate,
                    'have_stabilizer': have_stabilizer,
                    'total_running_time': 0
                })
    
    logger.info("Finish the benchmark process.")

if __name__ == "__main__":
    main()

# 后台运行命令
# nohup python /home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_decode_bposd.py >/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_result/log/qldpc_decode_bposd.log 2>&1 &
# 2541800