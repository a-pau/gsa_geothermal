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

#%% First order
 
def find_least_number(df,threshold):
    params=[]
    counter=0
    for col in df.columns[1:]:
        ser=df[["parameters",col]].sort_values(ascending=False, by=col)
        sum_=0
        i=0
        while sum_<=threshold:
            sum_+=ser[col].iloc[i]
            if not ser["parameters"].iloc[i] in params:
                params.append(ser["parameters"].iloc[i])
                counter+=1
            i+=1
    return counter

threshold = [0.5,0.6,0.7,0.8]

cge_F_n_dict={}
ege_F_n_dict={}

for t in threshold:
    cge_F_n_dict[t] = [find_least_number(cge_F, t)]
    ege_F_n_dict[t] = [find_least_number(ege_F, t)]
       
cge_F_n = pd.DataFrame.from_dict(cge_F_n_dict,orient="index")
ege_F_n = pd.DataFrame.from_dict(ege_F_n_dict,orient="index")
first_n = pd.concat([cge_F_n,ege_F_n], axis=1)
first_n.columns=["Conventional", "Enhanced"]

#%%Total order

def find_least_number_for_total(df,threshold):
    df_2 = df[df.columns[1:]]
    df_2=df_2[df_2<threshold].dropna()
    return len(df_2)
  

threshold_t = [0.01, 0.05,0.1,0.2,0.3]

cge_T_n_dict={}
ege_T_n_dict={}

for t in threshold_t:
    cge_T_n_dict[t] = [find_least_number_for_total(cge_T, t)]
    ege_T_n_dict[t] = [find_least_number_for_total(ege_T, t)]
       
cge_T_n = pd.DataFrame.from_dict(cge_T_n_dict,orient="index")
ege_T_n = pd.DataFrame.from_dict(ege_T_n_dict,orient="index")
total_n = pd.concat([cge_T_n,ege_T_n], axis=1)
total_n.columns=["Conventional", "Enhanced"]

#%% Subplots

# f1, (ax_first, ax_total) = plt.subplots(nrows=1,ncols=2)
# sb.set_style("darkgrid")

#%% Individual plots

f2, ax_first = plt.subplots()
f3, ax_total = plt.subplots()

#%% First order - Manual lollipop categorical chart with matplotlib

col_pal = sb.color_palette()

# set width of bars
barWidth = 0.02
 
# Set position of bars on X axis
r1 = np.arange(len(first_n["Conventional"]))
r2 = [x + 10*barWidth for x in r1]

# Make the plot
ax_first.scatter(r1, first_n["Conventional"],s=100,label='Conventional') 
ax_first.scatter(r2, first_n["Enhanced"],s=100,label='Enhanced') 
ax_first.bar(r1, first_n["Conventional"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)
ax_first.bar(r2, first_n["Enhanced"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)

# Add xticks on the middle of the group bars
ax_first.set_xlabel("Sum of first order indices", fontsize=12)
ax_first.set_xticks([r + 10*barWidth/2 for r in range(len(first_n["Conventional"]))])
ax_first.set_xticklabels(["0.50", "0.60", "0.70", "0.80"])
ax_first.set_ylabel("Least number of parameters below threshold", fontsize=12)
ax_first.set_yticks (np.arange(1,18))
min_, max_ = ax_first.get_xlim()
ax_first.set_xlim(left=min_, right=max_)
ax_first.hlines(17, xmin=min_, xmax=max_, linestyles='dashed', linewidth=1, colors=col_pal[0])
ax_first.hlines(16, xmin=min_, xmax=max_, linestyles='dashed', linewidth=1, colors=col_pal[1])

#legend
ax_first.legend(frameon=False, loc="upper left", fontsize="medium", markerscale=0.8, bbox_to_anchor= (0.0, 1.08), ncol=2, borderaxespad=0)

#grid
ax_first.grid(b=None, which='major', axis='x') 


#%% Total order - Manual lollipop categorical chart with matplotlib

# set width of bars
barWidth = 0.02
 
# Set position of bars on X axis
r1 = np.arange(len(total_n["Conventional"]))
r2 = [x + 10*barWidth for x in r1]

# Make the plot
ax_total.scatter(r1, total_n["Conventional"],s=100,label='Conventional') 
ax_total.scatter(r2, total_n["Enhanced"],s=100,label='Enhanced') 
ax_total.bar(r1, total_n["Conventional"]-0.35, color='black', width=barWidth, edgecolor='white', alpha=0.3)
ax_total.bar(r2, total_n["Enhanced"]-0.35, color='black', width=barWidth, edgecolor='white', alpha=0.3)

# Add xticks on the middle of the group bars
ax_total.set_xlabel("Total order index", fontsize=12)
ax_total.set_xticks([r + 10*barWidth/2 for r in range(len(total_n["Conventional"]))])
ax_total.set_xticklabels(["0.01", "0.05", "0.10","0.20", "0.30"])
ax_total.set_ylabel("Number of parameters below threshold", fontsize=12)
ax_total.set_yticks (np.arange(1,18))
min_, max_ = ax_total.get_xlim()
ax_total.set_xlim(left=min_, right=max_)
ax_total.hlines(17, xmin=min_, xmax=max_, linestyles='dashed', linewidth=1, colors=col_pal[0])
ax_total.hlines(16, xmin=min_, xmax=max_, linestyles='dashed', linewidth=1, colors=col_pal[1])

#legend
ax_total.legend(frameon=False, loc="upper left", fontsize="medium", markerscale=0.8,bbox_to_anchor= (0.0, 1.08), ncol=2, borderaxespad=0)

#grid
ax_total.grid(b=None, which='major', axis='x') 


#%% Save Combined
# f1.tight_layout()
# folder_OUT = os.path.join(absolute_path, "generated_plots","ecoinvent_3.6")
# f1.savefig(os.path.join(folder_OUT, "lollipop chart - combined.png"))


#%% Save individual

f2.tight_layout()
f3.tight_layout()
folder_OUT = os.path.join(absolute_path, "generated_plots","ecoinvent_3.6")
f2.savefig(os.path.join(folder_OUT, "lollipop chart - First.png"), dpi=600)
f3.savefig(os.path.join(folder_OUT, "lollipop chart - Total.png"), dpi=600)