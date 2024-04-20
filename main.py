import pandas as pd
from itertools import combinations
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to read transactions from CSV file
def read_transactions(file_path):
    try:
        df = pd.read_csv(file_path)
        transactions = df.groupby('TransactionNo')['Items'].apply(set).tolist()
        return transactions
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the file:\n{e}")
        return None

# Function to generate frequent item sets and association rules using the Apriori algorithm
def apriori(transactions, min_support, min_confidence):
    frequent_item_sets_per_level = dict()
    association_rules_per_level = dict()

    # Level 1: Generate frequent item sets
    level = 1
    frequent_item_sets = dict()
    for transaction in transactions:
        for item in transaction:
            frequent_item_sets[frozenset([item])] = frequent_item_sets.get(frozenset([item]), 0) + 1

    # Prune infrequent item sets
    frequent_item_sets = {item_set: support for item_set, support in frequent_item_sets.items() if support / len(transactions) >= min_support}
    frequent_item_sets_per_level[level] = frequent_item_sets

    # Levels > 1: Generate frequent item sets using self-join and pruning
    while frequent_item_sets:
        level += 1
        frequent_item_sets = dict()
        candidate_item_sets = set()

        # Self-join
        for item_set1 in frequent_item_sets_per_level[level - 1]:
            for item_set2 in frequent_item_sets_per_level[level - 1]:
                if len(item_set1.union(item_set2)) == level:
                    candidate_item_sets.add(item_set1.union(item_set2))

        # Pruning
        for transaction in transactions:
            for candidate_item_set in candidate_item_sets:
                if candidate_item_set.issubset(transaction):
                    frequent_item_sets[candidate_item_set] = frequent_item_sets.get(candidate_item_set, 0) + 1

        # Prune infrequent item sets
        frequent_item_sets = {item_set: support for item_set, support in frequent_item_sets.items() if support / len(transactions) >= min_support}
        frequent_item_sets_per_level[level] = frequent_item_sets

        # Generate association rules
        if level >= 2:
            association_rules = []
            for item_set in frequent_item_sets:
                for i in range(1, len(item_set)):
                    for antecedent in combinations(item_set, i):
                        antecedent = frozenset(antecedent)
                        consequent = item_set - antecedent
                        support_antecedent = frequent_item_sets_per_level[len(antecedent)][antecedent]
                        confidence = support_antecedent / frequent_item_sets_per_level[level][item_set]
                        support_consequent = frequent_item_sets_per_level[level][item_set]
                        lift = confidence / (support_consequent / len(transactions))
                        if confidence >= min_confidence:
                            association_rules.append((antecedent, consequent, confidence, lift))
            association_rules_per_level[level] = association_rules

    return frequent_item_sets_per_level, association_rules_per_level, transactions

# Function to handle button click event to browse file
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

# Function to handle button click event to start analysis
def start_analysis():
    file_path = entry_file_path.get()
    min_support = float(entry_min_support.get())
    min_confidence = float(entry_min_confidence.get())

    transactions = read_transactions(file_path)
    if transactions:
        # Perform analysis using Apriori algorithm
        frequent_item_sets_per_level, association_rules_per_level, transactions = apriori(transactions, min_support, min_confidence)
        # Print frequent item sets and association rules
        print_results(frequent_item_sets_per_level, association_rules_per_level, transactions)
        # Show completion message
        messagebox.showinfo("Analysis Complete", "Apriori analysis completed successfully.")

# Function to print frequent item sets and association rules
def print_results(frequent_item_sets_per_level, association_rules_per_level, transactions):
    for level, item_sets in frequent_item_sets_per_level.items():
        print("Frequent item sets for level", level)
        for item_set, support in item_sets.items():
            print("Item Set:", item_set, "Support Percentage:", round(support / len(transactions) * 100, 2), "%")

    for level, rules in association_rules_per_level.items():
        print("\nAssociation rules for level", level)
        for rule in rules:
            antecedent = "{" + ", ".join(rule[0]) + "}"
            consequent = "{" + ", ".join(rule[1]) + "}"
            confidence = rule[2]
            lift = rule[3]
            print(f"{antecedent} -> {consequent} <confidence: {confidence}, lift: {lift}>")

# Create GUI window
root = tk.Tk()
root.title("Apriori Analysis")

# File path label and entry
tk.Label(root, text="File Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_file_path = tk.Entry(root, width=50)
entry_file_path.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
btn_browse = tk.Button(root, text="Browse", command=browse_file)
btn_browse.grid(row=0, column=3, padx=5, pady=5)

# Minimum support label and entry
tk.Label(root, text="Minimum Support:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_min_support = tk.Entry(root)
entry_min_support.grid(row=1, column=1, padx=5, pady=5)

# Minimum confidence label and entry
tk.Label(root, text="Minimum Confidence:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_min_confidence = tk.Entry(root)
entry_min_confidence.grid(row=2, column=1, padx=5, pady=5)

# Start analysis button
btn_start = tk.Button(root, text="Start Analysis", command=start_analysis)
btn_start.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Run the GUI loop
root.mainloop()
