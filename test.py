import pandas as pd
import random

def generate_test_excel(filename='test_data.xlsx', num_points=10):
    data = []
    for i in range(num_points):
        name = f"Point_{i+1}"
        x = round(random.uniform(1000, 5000), 3)
        y = round(random.uniform(1000, 5000), 3)
        z = round(random.uniform(1000, 5000), 3)
        data.append([name, x, y, z])

    df = pd.DataFrame(data, columns=['Name', 'X', 'Y', 'Z'])
    df.to_excel(filename, index=False)
    print(f"✅ Test file saved to {filename}")

if __name__ == "__main__":
    generate_test_excel()