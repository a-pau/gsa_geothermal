import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np
import os 

# Set working directory
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

col=range(1,17)

cge_F=pd.read_excel(os.path.join(absolute_path,"generated_files/gsa_results/cge_N500/sobol_first.xlsx"), usecols=col)
cge_T=pd.read_excel(os.path.join(absolute_path,"generated_files/gsa_results/cge_N500/sobol_total.xlsx"), usecols=col)
ege_F=pd.read_excel(os.path.join(absolute_path,"generated_files/gsa_results/ege_N500/sobol_first.xlsx"), usecols=col)
ege_T=pd.read_excel(os.path.join(absolute_path,"generated_files/gsa_results/ege_N500/sobol_total.xlsx"), usecols=col)

#This excludes the first column
def norm_pd(df_in):
    df_out=df_in
    for col in df_in.columns[1:]:
        df_out[col] = df_in[col]/df_in[col].sum()
    return df_out

cge_F_pc = norm_pd(cge_F)  
cge_T_pc = norm_pd(cge_T)
ege_F_pc = norm_pd(ege_F)
ege_T_pc = norm_pd(ege_T)      


def find_least_number(df,threshold):
    counter={}
    for col in df.columns[1:]:
        ser=df[col].sort_values(ascending=False)
        sum_=0
        i=0
        while sum_<=threshold:
            sum_+=ser.iloc[i]
            i+=1
            
        counter[col]=i
    return counter

threshold = [0.5,0.6,0.7,0.8,0.9,0.95,0.99]

cge_F_n_dict={}
cge_T_n_dict={}
ege_F_n_dict={}
ege_T_n_dict={}

for t in threshold:
    cge_F_n_dict[t] = find_least_number(cge_F_pc, t)
    cge_T_n_dict[t] = find_least_number(cge_T_pc, t)
    ege_F_n_dict[t] = find_least_number(ege_F_pc, t)
    ege_T_n_dict[t] = find_least_number(ege_T_pc, t)
    
cge_F_n = pd.DataFrame.from_dict(cge_F_n_dict,orient="columns").T
cge_T_n = pd.DataFrame.from_dict(cge_T_n_dict,orient="columns").T
ege_F_n = pd.DataFrame.from_dict(ege_F_n_dict,orient="columns").T
ege_T_n = pd.DataFrame.from_dict(ege_T_n_dict,orient="columns").T

cge_F_n["max"]=cge_F_n.max(axis=1)
cge_F_n["min"]=cge_F_n.min(axis=1)

cge_T_n["max"]=cge_T_n.max(axis=1)
cge_T_n["min"]=cge_T_n.min(axis=1)
    
ege_F_n["max"]=ege_F_n.max(axis=1)
ege_F_n["min"]=ege_F_n.min(axis=1)

ege_T_n["max"]=ege_T_n.max(axis=1)
ege_T_n["min"]=ege_T_n.min(axis=1)  
      
#%% Plot

plt.vlines(x=cge_F_n.index, ymin=cge_F_n["min"], ymax=cge_F_n["max"], color='grey', alpha=0.4)
plt.scatter(x=cge_F_n.index, y=cge_F_n["min"], color='skyblue', alpha=1)
plt.scatter(x=cge_F_n.index, y=cge_F_n["max"], color='green', alpha=0.4)
plt.legend()


# thresh = ["50%", "60%", "70%", "80%", "90%", "95%","99%"]
# cge_max = pd.DataFrame(data=thresh, columns=["threshold"])
# cge_max["first"]=cge_F_n["max"].array
# cge_max["total"]=cge_T_n["max"].array
# cge_max=cge_max.melt(id_vars="threshold",value_vars=["first", "total"] ,var_name="order", value_name="max")

# sb.barplot(data=cge_max, x="threshold", y="max", hue="order")

# ege_max = pd.DataFrame(data=thresh, columns=["threshold"])
# ege_max["first"]=ege_F_n["max"].array
# ege_max["total"]=ege_T_n["max"].array
# ege_max=ege_max.melt(id_vars="threshold",value_vars=["first", "total"] ,var_name="order", value_name="max")

#%% Manual lollipop categorical chart with matplotlib

# set width of bars
barWidth = 0.02
 
# Set position of bars on X axis
r1 = np.arange(len(cge_F_n["max"]))
r2 = [x + 10*barWidth for x in r1]
 
sb.set_style("darkgrid")

#%%Conventional
# Make the plot
f1=plt.figure()
plt.scatter(r1, cge_F_n["max"],s=100,label='First order') 
plt.scatter(r2, cge_T_n["max"],s=100,label='Total order') 
plt.bar(r1, cge_F_n["max"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)
plt.bar(r2, cge_T_n["max"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)

# Add xticks on the middle of the group bars
plt.xlabel("Explained variance")
plt.xticks([r + 10*barWidth/2 for r in range(len(cge_F_n["max"]))], ["50%", "60%", "70%", "80%", "90%", "95%","99%"], fontsize=10)
plt.ylabel("Least number of parameters")
plt.yticks (np.arange(1,18), fontsize=10)

#grid
plt.grid(b=None, which='major', axis='x') 

#adjust layout
plt.tight_layout()

#legend
plt.legend(frameon=True, loc="upper left", fontsize="small", markerscale=0.8)

#%%Enhanced

# Make the plot
f2=plt.figure()
plt.scatter(r1, ege_F_n["max"],s=100,label='First order') 
plt.scatter(r2, ege_T_n["max"],s=100,label='Total order') 
plt.bar(r1, ege_F_n["max"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)
plt.bar(r2, ege_T_n["max"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)

# Add xticks on the middle of the group bars
plt.xlabel("Explained variance")
plt.xticks([r + 10*barWidth/2 for r in range(len(cge_F_n["max"]))], ["50%", "60%", "70%", "80%", "90%", "95%","99%"], fontsize=10)
plt.ylabel("Least number of parameters")
plt.yticks (np.arange(1,17), fontsize=10)

#grid
plt.grid(b=None, which='major', axis='x') 

#adjust layout
plt.tight_layout()

#legend
plt.legend(frameon=True, loc="upper left", fontsize="small", markerscale=0.8)




#%% Save
folder_OUT = os.path.join(absolute_path, "generated_plots","ecoinvent_3.6")
f1.savefig(os.path.join(folder_OUT, "lollipop chart - conventional.png"))
f2.savefig(os.path.join(folder_OUT, "lollipop chart - enhanced.png"))


