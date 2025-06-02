import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# 1. 读取数据
df = pd.read_csv("target_output.txt", sep=r'\s+')

# 2. 原始时间列（非均匀）
time_raw = df["dtfix"].values

# 3. 构造统一时间轴（例如：1000个点，均匀从 min 到 max）
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
plt.savefig("stress_strain_vs_time.png")
