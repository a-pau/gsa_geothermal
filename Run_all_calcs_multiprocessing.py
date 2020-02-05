import os                                                                       
from multiprocessing import Pool
import time                                              
                                                                                
# All scripts are: "ReferenceVsLiterature_CC_calc.py",\
#                  "ReferenceVsSimplified_calc.py", \
#                  "ReferenceVsSimplified_test_cases_calc.py", \
#                  "ReferenceVsSimplified_UDDGP_and_HSD_calc.py")  

                                                                            
processes = ("ReferenceVsSimplified_calc.py", \
             "ReferenceVsSimplified_test_cases_calc.py", \
             "ReferenceVsSimplified_UDDGP_and_HSD_calc.py")
                                    
                                                                                                                              
def run_process(process):                                                             
    os.system('python {}'.format(process))                                       

n_proc = len(processes)

if __name__ == '__main__':                                                                                
    start_time = time.time()                                                                            
    pool = Pool(processes=n_proc)                                                  
    pool.map(run_process, processes)   
    pool.close()
    pool.join()
    total_time = time.time() - start_time
    print("Total time for running processes in parallel: ", total_time)

