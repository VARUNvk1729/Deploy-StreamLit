import os
import pandas as pd
import streamlit as st

import chardet

def process_paths(file_path, filter_files=False):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        detected_encoding = chardet.detect(raw_data)['encoding']
        encoding = detected_encoding if detected_encoding else 'utf-8'

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            paths = [line.strip() for line in f.readlines()]
    except UnicodeDecodeError:
        st.error(f"Failed to decode file with detected encoding: {encoding}.")
        return pd.DataFrame() 

    data = []
    max_depth = 0
    for path in paths:
        drive, path_tail = os.path.splitdrive(path)
        if not drive:
            drive = 'No Drive'
        
        components = [comp for comp in path_tail.split(os.sep) if comp]
        
        if filter_files and (not components or '.' not in components[-1]):
            continue
        
        max_depth = max(max_depth, len(components))
        data.append((drive, components[:-1], components[-1] if components and '.' in components[-1] else None))
    
    columns = ["Drive"] + [f"Folder Level {i+1}" for i in range(max_depth - 1)] + ["File Name"]
    processed_data = []
    for drive, folders, file_name in data:
        row = [drive] + folders + [None] * (max_depth - 1 - len(folders)) + [file_name]
        processed_data.append(row)
    
    return pd.DataFrame(processed_data, columns=columns)


st.title("File Path Extraction and Categorization Tool")
uploaded_file = st.file_uploader("Upload a text file containing paths", type=["txt"])

if uploaded_file:
    temp_file = "uploaded_paths.txt"
    with open(temp_file, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    filter_files = st.checkbox("Show only paths containing file names")
    df = process_paths(temp_file, filter_files=filter_files)
    st.dataframe(df)
    
    export_button = st.button("Export to CSV")
    if export_button:
        output_file = "processed_paths.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        with open(output_file, "rb") as f:
            st.download_button(
                label="Download CSV File",
                data=f,
                file_name=output_file,
                mime="text/csv"
            )
