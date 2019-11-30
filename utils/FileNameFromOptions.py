def get_file_name(base_name, exploration, success_rate):
    
    # Get name of file from base_name and options exploration and success_rate
   
    if ".xlsx" in base_name:
        base_name_wo_ext, _ = base_name.split(".")
        ext= ".xlsx"
    else:
        base_name_wo_ext = base_name
        ext = ""
            
    if success_rate and exploration:
        file_name = base_name
    elif success_rate and not exploration:
        file_name = base_name_wo_ext + " - NO expl" + ext
    elif exploration and not success_rate:
        file_name = base_name_wo_ext + " - NO sr" + ext
    elif not exploration and not success_rate:
        file_name = base_name_wo_ext + " - NO sr NO expl" + ext
        
    return file_name