import os
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def run_lammps_in_folder(folder_path, cmd):
    start_time = time.time()
    current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"开始时间：{current_time_str}")

    absolute_folder_path = Path(folder_path).resolve()
    print(f"工作目录: {absolute_folder_path}")

    if "oriCd" in folder_path.name:
        cmd = "mpiexec -n 8 D:/lammps_test/exe/lmp_msmpi.exe -in input.lmp"
        print(f"包含关键字'oriCd'，执行命令：{cmd}")
    else:
        cmd = "mpiexec -n 8 C:/LAMMPS/LAMMPS_PRIVATE/lammps-private/build/Release/lmp_msmpi.exe -in input.lmp"
        print(f"执行命令：{cmd}")

    command_to_execute_in_new_window = f'cd /d "{absolute_folder_path}" && {cmd}'
    full_start_command = f'start "LAMMPS: {Path(folder_path).name}" /wait cmd /c "{command_to_execute_in_new_window}"'
    return_code = os.system(full_start_command)

    elapsed = time.time() - start_time
    print(f"\n执行完毕，用时 {elapsed:.1f} 秒。")
    if return_code == 0:
        print(f"🟢 正常退出 (退出码: {return_code})。")
    else:
        print(f"🔴 异常退出 (退出码: {return_code})。")
    
    output_file_path = Path(folder_path) / "target_output.txt"
    pic_file_path = Path(folder_path) / "target_output.png"
    if output_file_path.exists():
        print(f"正在从输出文件生成图像...")
        # 1. 读取数据
        df = pd.read_csv(output_file_path, sep=r'\s+')
        # 2. 原始时间列（非均匀）
        time_raw = df["dtfix"].values
        # 3. 构造统一时间轴
        time_uniform = np.linspace(time_raw.min(), time_raw.max(), 1000)
        # 4. 要插值的字段
        fields = ["damage", "vm_stress", "mean_stress", "vm_strain", "mean_strain", "plas_strain"]
        # 5. 对每个字段做插值
        interpolated_data = {}
        for field in fields:
            interp_func = interp1d(time_raw, df[field].values, kind='linear', fill_value="extrapolate")
            interpolated_data[field] = interp_func(time_uniform)
        # 6. 绘图
        plt.figure(figsize=(10, 6))
        for field in fields:
            plt.plot(time_uniform, interpolated_data[field], label=field)

        plt.xlabel("dtfix")
        plt.ylabel("value")
        plt.title("curve")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(pic_file_path)
        print(f"生成完成，图像已保存到：{pic_file_path}")
    
    return return_code

def main():
    if len(sys.argv) < 2:
        print("请提供要运行的目录路径。")
        return
    
    base_path = Path(sys.argv[1])
    if not base_path.exists() or not base_path.is_dir():
        print(f"错误：路径不存在或不是文件夹：{base_path}")
        return
    
    subfolders = sorted([f for f in base_path.iterdir() if f.is_dir()])
    total = len(subfolders)
    print(f"目标路径：{base_path}")
    print(f"发现子文件夹：{total} 个")

    total_start_time = time.time()
    success_count  = 0

    for idx, folder in enumerate(subfolders, start=1):
        print(f"\n======== 开始第 {idx}/{total} 个任务：{folder.name} ========")
        code = run_lammps_in_folder(folder)
        if code == 0:
            success_count += 1
    
    total_elapsed = time.time() - total_start_time
    print(f"\n全部任务完成，总耗时：{total_elapsed:.1f} 秒")
    print(f"🟢 运行成功：{success_count}/{total} 个任务")
    if success_count < total:
        print(f"🔴 运行失败：{total - success_count}/{total} 个任务")

if __name__ == "__main__":
    main()