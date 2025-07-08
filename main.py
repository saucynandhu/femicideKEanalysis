# Femicide in Kenya Data Analysis
# ==================================
# This script analyzes femicide case data from 2016 to 2022 from an Excel file
# and generates visual insights and statistics to help understand trends.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os
from datetime import datetime


# -------- CONFIG --------
import os

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "dataset.xlsx")  # Use full path to the file
OUTPUT_DIR = "femicide_analysis_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------- LOAD & CLEAN DATA --------
df = pd.read_excel(INPUT_FILE)

# Clean and standardize text data
def clean_text(column):
    if column.dtype == 'object':
        # Convert to string, handle NaN values, and strip whitespace
        column = column.astype(str).str.strip()
        # Convert to lowercase for consistency
        column = column.str.lower()
        # Common replacements for inconsistent spellings
        replacements = {
            'husband|ex-husband|former husband': 'husband',
            'boyfriend|ex-boyfriend|former boyfriend': 'boyfriend',
            'partner|domestic partner': 'partner',
            'acquaintance|known|known to victim': 'acquaintance',
            'stranger|unknown': 'stranger',
            'family member|relative': 'family member',
            'neighbor|neighbour': 'neighbor',
            'friend|friends': 'friend',
            'co-worker|colleague': 'coworker'
        }
        
        for pattern, replacement in replacements.items():
            column = column.str.replace(fr'\b({pattern})\b', replacement, case=False, regex=True)
            
    return column

# Apply cleaning to relevant columns
text_columns = ['suspect relationship', 'Mode of killing', 'Type of femicide', 'Verdict']
for col in text_columns:
    if col in df.columns:
        df[col] = clean_text(df[col])

# Fill missing values with 'unknown' for categorical columns
categorical_cols = ['suspect relationship', 'Mode of killing', 'Type of femicide', 'Verdict']
for col in categorical_cols:
    if col in df.columns:
        df[col] = df[col].replace(['nan', 'none', 'null', ''], 'unknown').fillna('unknown')

# Parse dates
df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce')
df['date of murder'] = pd.to_datetime(df['date of murder'], errors='coerce')
df['Court date (first appearance)'] = pd.to_datetime(df['Court date (first appearance)'], errors='coerce')
df['verdict date'] = pd.to_datetime(df['verdict date'], errors='coerce')

# Extract year/month
df['year'] = df['date of murder'].dt.year

# -------- 1. YEARLY TREND --------
yearly = df['year'].value_counts().sort_index()
yearly.plot(kind='line', marker='o', title='Femicide Cases Per Year', figsize=(10, 5))
plt.xlabel('Year')
plt.ylabel('Number of Cases')
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/cases_per_year.png")
plt.close()

# -------- 2. MODES OF KILLING --------
mode = df['Mode of killing'].value_counts().head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=mode.values, y=mode.index, palette='Reds_d')
plt.title('Top 10 Modes of Killing')
plt.xlabel('Number of Cases')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/top_modes_of_killing.png")
plt.close()

# -------- 3. RELATIONSHIPS --------
rels = df['suspect relationship'].value_counts().head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=rels.values, y=rels.index, palette='Purples_d')
plt.title('Relationship Between Victim and Suspect')
plt.xlabel('Number of Cases')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/relationship_distribution.png")
plt.close()

# -------- 4. VERDICT ANALYSIS --------
verdicts = df['Verdict'].value_counts()
plt.figure(figsize=(8, 5))
sns.barplot(x=verdicts.index, y=verdicts.values, palette="Greens")
plt.title('Verdict Distribution')
plt.ylabel('Number of Cases')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/verdicts.png")
plt.close()

# -------- 5. SENTENCE LENGTHS --------
df['Years of sentence'] = pd.to_numeric(df['Years of sentence'], errors='coerce')
df['Years of sentence'].dropna().plot.hist(bins=20, color='orange', edgecolor='black', figsize=(10, 5))
plt.title('Distribution of Sentencing Lengths')
plt.xlabel('Years')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/sentence_lengths.png")
plt.close()

# -------- 6. CIRCUMSTANCE WORD CLOUD --------
circum_text = " ".join(df['Circumstance'].dropna().astype(str))
wordcloud = WordCloud(width=1000, height=500, background_color='white').generate(circum_text)
plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Circumstance Word Cloud')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/circumstance_wordcloud.png")
plt.close()

# -------- 7. TIMELINE OF HIGH PROFILE CASES --------
high_profile = df[df['medium'].str.contains("Nation|Citizen|BBC", case=False, na=False)]
high_profile_cases = high_profile[['date of murder', 'name of victim', 'Location']].dropna()
high_profile_cases = high_profile_cases.sort_values('date of murder').drop_duplicates()

plt.figure(figsize=(12, 5))
plt.plot_date(high_profile_cases['date of murder'], range(len(high_profile_cases)), linestyle='solid', marker='o')
plt.title('Timeline of High-Profile Femicide Cases')
plt.xlabel('Date')
plt.ylabel('Case Index')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/high_profile_timeline.png")
plt.close()

# -------- 8. SAVE CLEANED CSV --------
df.to_csv(f"{OUTPUT_DIR}/cleaned_femicide_data.csv", index=False)

print("[✅] Analysis complete. All visualizations saved to:", OUTPUT_DIR)