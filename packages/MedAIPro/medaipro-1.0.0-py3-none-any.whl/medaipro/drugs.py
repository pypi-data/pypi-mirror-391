DRUG_INTERACTIONS = {
    ("Aspirin", "Warfarin"): "嚴重：出血風險增加",
    ("Ibuprofen", "Lisinopril"): "中等：可能降低降壓效果",
    ("Paracetamol", "Alcohol"): "中等：肝毒性風險增加"
}

def check_interaction(drug1, drug2):
    """檢查兩種藥物的交互作用"""
    pair = tuple(sorted([drug1, drug2]))
    return DRUG_INTERACTIONS.get(pair, "無已知交互作用")
