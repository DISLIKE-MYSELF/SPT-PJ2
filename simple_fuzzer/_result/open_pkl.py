
import pickle

from main import  Result

# 假设文件叫 data.pkl
with open('Sample-4.pkl', 'rb') as f:
    data = pickle.load(f)

print(type(data))     # 查看数据类型
print(data)           # 打印内容（如果内容很大，建议用 pprint）
