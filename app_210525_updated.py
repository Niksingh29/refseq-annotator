import streamlit as st
import pandas as pd
from Bio import Entrez
import time

# Set your email address (required by NCBI)
Entrez.email = "your_email@example.com"  # <-- Replace with your real email

# Page configuration
st.set_page_config(page_title="RefSeq & LOC ID Annotator", layout="centered")
st.title("🔍 RefSeq & LOC ID Annotator")
st.markdown("**Designed by [Nikhil Singh](https://singhdecodeomics.com/my-work/)**")
st.markdown("📧 Contact or report errors: [niksingh29@gmail.com](mailto:niksingh29@gmail.com)")
st.markdown("Upload a CSV file with a column named **GeneID** containing RefSeq IDs (e.g., XM_, NM_) or LOC IDs (e.g., LOC123456...).")

st.markdown("""
---

### 📘 About this Tool
This web-based utility allows researchers to quickly annotate RefSeq transcript and protein accessions (e.g., `NM_`, `XM_`, `XP_`) as well as NCBI Gene LOC identifiers (`LOC...`). It leverages real-time queries to the NCBI Gene database to retrieve gene names and functional descriptions.

### 💡 Supported Input IDs
- RefSeq mRNA: `NM_`, `XM_`
- RefSeq ncRNA: `NR_`, `XR_`
- RefSeq protein: `NP_`, `XP_`
- Gene symbols: `LOC...`

### 🧪 Example File Format
You can upload a CSV like this:
```csv
GeneID
NM_001301717.1
XP_004485536.1
LOC101488245
```

### 🔐 License and Citation
- **License:** MIT, free for academic use

---
""")

# File upload
uploaded_file = st.file_uploader("Upload RefSeq or LOC CSV File", type=["csv"])

# Define annotation function
def annotate_ids(gene_id_list):
    results = []
    for idx, gid in enumerate(gene_id_list, 1):
        st.info(f"Processing {idx}/{len(gene_id_list)}: {gid}")
        try:
            if gid.startswith("NM_") or gid.startswith("XM_") or gid.startswith("NR_") or gid.startswith("XR_") or gid.startswith("NP_") or gid.startswith("XP_"):
                # Link RefSeq to Gene ID
                link = Entrez.elink(dbfrom="nuccore", db="gene", id=gid)
                link_result = Entrez.read(link)
                if link_result[0]["LinkSetDb"]:
                    gene_id = link_result[0]["LinkSetDb"][0]["Link"][0]["Id"]
                    summary = Entrez.esummary(db="gene", id=gene_id)
                    summary_result = Entrez.read(summary)
                    info = summary_result["DocumentSummarySet"]["DocumentSummary"][0]
                    results.append({
    "InputID": gid,
    "GeneID": gene_id,
    "GeneName": info["Name"],
    "GeneSymbol": info.get("NomenclatureSymbol", "-"),
    "Description": info["Description"],
    "GeneType": info.get("GeneType", "-"),
    "Organism": info.get("Organism", "-"),
    "Chromosome": info.get("Chromosome", "-"),
    "MapLocation": info.get("MapLocation", "-")
})
                else:
                    results.append({"InputID": gid, "GeneID": "Not found", "GeneName": "Not found", "Description": "Not found"})

            elif gid.startswith("LOC"):
                # Use esearch with LOC ID in gene db
                search = Entrez.esearch(db="gene", term=f"{gid}[Gene Name]")
                search_result = Entrez.read(search)
                if search_result["IdList"]:
                    gene_id = search_result["IdList"][0]
                    summary = Entrez.esummary(db="gene", id=gene_id)
                    summary_result = Entrez.read(summary)
                    info = summary_result["DocumentSummarySet"]["DocumentSummary"][0]
                    results.append({
    "InputID": gid,
    "GeneID": gene_id,
    "GeneName": info["Name"],
    "GeneSymbol": info.get("NomenclatureSymbol", "-"),
    "Description": info["Description"],
    "GeneType": info.get("GeneType", "-"),
    "Organism": info.get("Organism", "-"),
    "Chromosome": info.get("Chromosome", "-"),
    "MapLocation": info.get("MapLocation", "-")
})
                else:
                    results.append({"InputID": gid, "GeneID": "Not found", "GeneName": "Not found", "Description": "Not found"})

            else:
                results.append({"InputID": gid, "GeneID": "Invalid format", "GeneName": "Invalid", "Description": "Invalid input ID"})

        except Exception as e:
            results.append({"InputID": gid, "GeneID": "Error", "GeneName": "Error", "Description": str(e)})
        time.sleep(0.34)
    return pd.DataFrame(results)

# Process file
if uploaded_file:
    try:
        df_input = pd.read_csv(uploaded_file)
        if "GeneID" not in df_input.columns:
            st.error("❌ CSV must contain a column named 'GeneID'.")
        else:
            id_list = df_input["GeneID"].dropna().unique().tolist()
            df_output = annotate_ids(id_list)
            st.success("✅ Annotation complete!")
            st.dataframe(df_output)

            # Download button
            csv = df_output.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Annotated Results", csv, "Annotated_Genes.csv", "text/csv")
    except Exception as e:
        st.error(f"Error processing file: {e}")
