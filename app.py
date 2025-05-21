import streamlit as st
import pandas as pd
from Bio import Entrez
import time

# Set your email address (required by NCBI)
Entrez.email = "your_email@example.com"  # <-- Replace with your real email

# Page configuration
st.set_page_config(page_title="RefSeq Annotator", layout="centered")
st.title("🔍 RefSeq ID Annotator")
st.markdown("Upload a CSV file with a column named **GeneID** containing RefSeq IDs (e.g., XM_, NM_, XR_, XP_...).")

# File upload
uploaded_file = st.file_uploader("Upload RefSeq CSV File", type=["csv"])

# Define annotation function
def annotate_refseq_ids(refseq_list):
    results = []
    for idx, acc in enumerate(refseq_list, 1):
        st.info(f"Processing {idx}/{len(refseq_list)}: {acc}")
        try:
            # Link RefSeq to Gene ID
            link = Entrez.elink(dbfrom="nuccore", db="gene", id=acc)
            link_result = Entrez.read(link)
            if link_result[0]["LinkSetDb"]:
                gene_id = link_result[0]["LinkSetDb"][0]["Link"][0]["Id"]
                
                # Get Gene info
                summary = Entrez.esummary(db="gene", id=gene_id)
                summary_result = Entrez.read(summary)
                info = summary_result["DocumentSummarySet"]["DocumentSummary"][0]
                
                results.append({
                    "RefSeqID": acc,
                    "GeneID": gene_id,
                    "GeneName": info["Name"],
                    "Description": info["Description"]
                })
            else:
                results.append({"RefSeqID": acc, "GeneID": "Not found", "GeneName": "Not found", "Description": "Not found"})
        except Exception as e:
            results.append({"RefSeqID": acc, "GeneID": "Error", "GeneName": "Error", "Description": str(e)})
        time.sleep(0.34)
    return pd.DataFrame(results)

# Process file
if uploaded_file:
    try:
        df_input = pd.read_csv(uploaded_file)
        if "GeneID" not in df_input.columns:
            st.error("❌ CSV must contain a column named 'GeneID'.")
        else:
            refseq_ids = df_input["GeneID"].dropna().unique().tolist()
            df_output = annotate_refseq_ids(refseq_ids)
            st.success("✅ Annotation complete!")
            st.dataframe(df_output)

            # Download button
            csv = df_output.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Annotated Results", csv, "Annotated_RefSeq_Results.csv", "text/csv")
    except Exception as e:
        st.error(f"Error processing file: {e}")
