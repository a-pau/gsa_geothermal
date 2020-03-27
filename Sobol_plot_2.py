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

#This excludes the first column, which includex the indices
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

threshold = [0.5,0.756,0.9,0.95,0.99]

cge_F_n_dict={}
cge_T_n_dict={}
ege_F_n_dict={}
ege_T_n_dict={}

for t in threshold:
    cge_F_n_dict[t] = [find_least_number(cge_F_pc, t)]
    cge_T_n_dict[t] = [find_least_number(cge_T_pc, t)]
    ege_F_n_dict[t] = [find_least_number(ege_F_pc, t)]
    ege_T_n_dict[t] = [find_least_number(ege_T_pc, t)]
    
cge_F_n = pd.DataFrame.from_dict(cge_F_n_dict,orient="index")
cge_T_n = pd.DataFrame.from_dict(cge_T_n_dict,orient="index")
cge_n = pd.concat([cge_F_n,cge_T_n], axis=1)
cge_n.columns=["First", "Total"]
ege_F_n = pd.DataFrame.from_dict(ege_F_n_dict,orient="index")
ege_T_n = pd.DataFrame.from_dict(ege_T_n_dict,orient="index")
ege_n = pd.concat([ege_F_n,ege_T_n], axis=1)
ege_n.columns=["First", "Total"]

#%% Manual lollipop categorical chart with matplotlib

# set width of bars
barWidth = 0.02
 
# Set position of bars on X axis
r1 = np.arange(len(cge_n["First"]))
r2 = [x + 10*barWidth for x in r1]
 
sb.set_style("darkgrid")

#%% First order
# Make the plot
f1=plt.figure()
plt.scatter(r1, cge_n["First"],s=100,label='Conventional') 
plt.scatter(r2, ege_n["First"],s=100,label='Enhanced') 
plt.bar(r1, cge_n["First"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)
plt.bar(r2, ege_n["First"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)

# Add xticks on the middle of the group bars
plt.xlabel("Explained variance")
plt.xticks([r + 10*barWidth/2 for r in range(len(cge_n["First"]))], ["50%", "75%", "90%", "95%", "99%"], fontsize=10)
plt.ylabel("Least number of parameters")
plt.yticks (np.arange(1,15), fontsize=10)

#grid
plt.grid(b=None, which='major', axis='x') 

#adjust layout
plt.tight_layout()

#legend
plt.legend(frameon=True, loc="upper left", fontsize="small", markerscale=0.8)

#%%Enhanced

# Make the plot
f2=plt.figure()
plt.scatter(r1, cge_n["Total"],s=100,label='Conventional') 
plt.scatter(r2, ege_n["Total"],s=100,label='Enhanced') 
plt.bar(r1, cge_n["Total"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)
plt.bar(r2, ege_n["Total"]-0.3, color='black', width=barWidth, edgecolor='white', alpha=0.3)

# Add xticks on the middle of the group bars
plt.xlabel("Explained variance")
plt.xticks([r + 10*barWidth/2 for r in range(len(cge_n["First"]))], ["50%", "75%", "90%","95%", "99%"], fontsize=10)
plt.ylabel("Least number of parameters")
plt.yticks (np.arange(1,15), fontsize=10)

#grid
plt.grid(b=None, which='major', axis='x') 

#adjust layout
plt.tight_layout()

#legend
plt.legend(frameon=True, loc="upper left", fontsize="small", markerscale=0.8)




#%% Save
folder_OUT = os.path.join(absolute_path, "generated_plots","ecoinvent_3.6")
f1.savefig(os.path.join(folder_OUT, "lollipop chart - First.png"))
f2.savefig(os.path.join(folder_OUT, "lollipop chart - Total.png"))


