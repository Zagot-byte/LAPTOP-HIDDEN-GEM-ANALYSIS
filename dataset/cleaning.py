import pandas as pd
import re

# Load CSV
df = pd.read_csv("/content/laptop.csv")

# Standardize model names
df['Model'] = df['Model'].str.strip().str.upper()

# Sort alphabetically by Model
df = df.sort_values(by='Model').reset_index(drop=True)

# Check and fill missing values
for col in df.columns:
    if df[col].isnull().sum() > 0:
        if df[col].dtype == 'object':
            df[col].fillna('UNKNOWN', inplace=True)
        else:
            df[col].fillna(df[col].median(), inplace=True)

# Clean Price column
df['Price'] = df['Price'].replace({'₹':'', ',':''}, regex=True).astype(float)

# --- CPU Score (0.4 weight) ---
cpu_scores = []
for cpu in df['Generation']:
    cpu_name = str(cpu).upper()
    gen_score = 0
    core_score = 0
    
    # Extract generation number
    match = re.search(r'(\d{3,4})', cpu_name)
    if match:
        gen_number = int(str(match.group())[0])
        gen_score = gen_number * 2  # scale generation
    
    # Series/core scoring
    if 'H' in cpu_name or 'K' in cpu_name:
        core_score = 3
    elif 'U' in cpu_name:
        core_score = 1
    elif 'G' in cpu_name:
        core_score = 2
    else:
        core_score = 2
    
    cpu_scores.append((gen_score + core_score) * 0.4)
df['CPU_Score'] = cpu_scores

# --- RAM Score (0.2 per GB) ---
ram_scores = []
for ram in df['Ram']:
    match = re.search(r'(\d+)', str(ram))
    if match:
        ram_scores.append(int(match.group(1)) * 0.2)
    else:
        ram_scores.append(8 * 0.2)  # default 8GB
df['RAM_Score'] = ram_scores

# --- GPU Score (0.3 weight, depends on VRAM and model) ---
gpu_scores = []
for gpu in df['Graphics']:
    gpu_str = str(gpu).upper()
    # Base VRAM
    match = re.search(r'(\d+)\s*GB', gpu_str)
    vram = int(match.group(1)) if match else 4

    # Simple model multiplier: newer series get +0.5
    if '6500' in gpu_str or '6600' in gpu_str:
        model_multiplier = 1.1
    elif '3050' in gpu_str or '3060' in gpu_str:
        model_multiplier = 1.2
    elif '4070' in gpu_str or '4080' in gpu_str:
        model_multiplier = 1.3
    else:
        model_multiplier = 1.0

    gpu_scores.append(vram * model_multiplier * 0.3)
df['GPU_Score'] = gpu_scores

# --- Storage Score (0.1 for SSD) ---
storage_scores = []
for storage in df['SSD']:
    if 'SSD' in str(storage).upper():
        storage_scores.append(0.1)
    else:
        storage_scores.append(0)
df['Storage_Score'] = storage_scores

# --- Total Performance Score ---
df['Performance_Score'] = df['CPU_Score'] + df['GPU_Score'] + df['RAM_Score'] + df['Storage_Score']

# --- Hidden Gem Ratio ---
df['Hidden_Gem_Ratio'] = df['Performance_Score'] / df['Price']

# Round Hidden Gem Ratio to 4 decimal places
df['Hidden_Gem_Ratio'] = df['Hidden_Gem_Ratio'].round(4)

# Sort by Hidden Gem Ratio descending
df = df.sort_values(by='Hidden_Gem_Ratio', ascending=False).reset_index(drop=True)
# Gaming
gaming_laptops = df[df['Hidden_Gem_Ratio'] > 0.0005]

# Editing
editing_laptops = df[(df['Hidden_Gem_Ratio'] >= 0.0004) & (df['Hidden_Gem_Ratio'] <= 0.0005)]

# Normal usage
normal_laptops = df[df['Hidden_Gem_Ratio'] < 0.0004]

# Save CSV
df.to_csv("/content/laptop_hidden_gem.csv", index=False)

# Preview top laptops
print(df[['Model', 'CPU_Score', 'GPU_Score', 'RAM_Score', 'Storage_Score', 'Performance_Score', 'Price', 'Hidden_Gem_Ratio']].head(10))

