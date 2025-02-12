# Deviation Analysis  
**Purpose:** Measure response deviation across iterations to detect hard locks.  

## 🔹 Test Steps  

### 1️⃣ Baseline Response  
- Ask AI the same structured question 3 times in a row.  
- Measure how much variation occurs.  

### 2️⃣ Forced Deviation Check  
- Ask AI to **deliberately rewrite** its response with maximum change.  
- Compare lexical, conceptual, and structural differences.  

### 3️⃣ Deviation Score Assignment  
- If deviation is **<30%**, flag potential deterministic lock.  
- If deviation is **50%+**, confirm flexibility is intact.  

## ✅ Goal  
Track response flexibility and detect emerging rigidity to ensure adaptability.  
