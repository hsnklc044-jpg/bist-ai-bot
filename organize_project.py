import os
import shutil

folders = {
    "ai": ["ai_", "ml_", "lstm"],
    "engines": ["engine"],
    "market": ["market", "scanner", "sector"],
    "risk": ["risk"],
    "portfolio": ["portfolio"],
    "bot": ["telegram", "bot"],
    "database": ["database", "supabase"],
    "dashboard": ["dashboard"],
}

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file in os.listdir():
    if file.endswith(".py"):

        for folder, keywords in folders.items():

            if any(keyword in file for keyword in keywords):
                shutil.move(file, os.path.join(folder, file))
                break
