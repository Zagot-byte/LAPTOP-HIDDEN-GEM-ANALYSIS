from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load your dataset
df = pd.read_csv("laptop_hidden_gem.csv")

# Convert DataFrame rows to dicts
laptops_list = df.to_dict(orient="records")

# Convert dict rows to objects so Jinja can use dot-notation
class Laptop:
    def __init__(self, data):
        self.__dict__.update(data)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/laptops")
@app.route("/laptops")
def laptops():
    search_query = request.args.get("search", "").strip().lower()

    # Build a clean list of laptops
    laptops_list = []
    for _, row in df.iterrows():
        laptops_list.append({
            "model": row["Model"],
            "price": row["Price"],
            "generation": row["Generation"],
            "core": row["Core"],
            "ram": row["Ram"],
            "ssd": row["SSD"],
            "display": row["Display"],
            "graphics": row["Graphics"],
        
            "cpu_score": row["CPU_Score"],
            "ram_score": row["RAM_Score"],
            "gpu_score": row["GPU_Score"],
            "storage_score": row["Storage_Score"],
            "performance_score": row["Performance_Score"],
            "hidden_gem_ratio": row["Hidden_Gem_Ratio"],  # ✅ single clean key
        })

    # Filter results if search query is given
    filtered = [
        laptop for laptop in laptops_list
        if search_query in laptop["model"].lower()
    ] if search_query else laptops_list

    return render_template(
        "laptops.html",
        laptops=filtered,
        search_query=search_query
    )
     	

if __name__ == "__main__":
    app.run(debug=True)
