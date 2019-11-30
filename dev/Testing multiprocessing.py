# =============================================================================
# import os                                                                       
# from multiprocessing import Pool, Process
# import time                                              
#                                                                                 
# # All scripts are:  "ReferenceVsLiterature_CC_calc.py",\
# #                  "ReferenceVsSimplified_calc.py", \
# #                  "ReferenceVsSimplified_test_cases_calc.py", \
# #                  "ReferenceVsSimplified_UDDGP_and_HSD_calc.py")  
# 
#                                                                             
# processes = ("ReferenceVsSimplified_calc.py", \
#              "ReferenceVsSimplified_test_cases_calc.py", \
#              "ReferenceVsSimplified_UDDGP_and_HSD_calc.py")                                    
#                                                                                                                               
# def run_process(process):                                                             
#     os.system('python {}'.format(process))                                       
# 
# # For reasons yet unknown, need to run one by one. When running the whole script
# # paraellel processing takes longer.
#     
# # Also, it is better to run from anaconda prompt
# 
# # Test was done with one iteration
# 
# #%% Processees in sequence
# times=[time.time()]
# for i in range(3):
#     run_process(processes[i])
#     times.append(time.time())
#     print(processes[i], " - Time for iteration: ", round(times[i+1] - times[i],2))
#     
# print("Total time for runnin processes in sequence: ", round(times[3]-times[0],2))
# 
# #ReferenceVsSimplified_calc.py  - Time for iteration:  ~26
# #ReferenceVsSimplified_test_cases_calc.py  - Time for iteration:  ~88
# #ReferenceVsSimplified_UDDGP_and_HSD_calc.py  - Time for iteration:  ~28
# #Total time :  ~14295
# 
# #%% Multiprocessing with process
# if __name__ == '__main__':                                                                                
#     start_time = time.time()  
#     
#     p0 = Process(target=run_process,args=(processes[0],))
#     p1 = Process(target=run_process,args=(processes[1],))
#     p2 = Process(target=run_process,args=(processes[2],))     
# 
#     p0.start()
#     p1.start()
#     p2.start()
#     
#     p0.join()
#     p1.join()
#     p2.join()
#                                                                          
#     total_time = round(time.time() - start_time,2)
#     print("Total time for running processes in parallel with process: ", total_time)
# 
# ##Total time for running processes in parallel with process:  ~95
# 
# #%% Multiprocessing with pool
#     
# if __name__ == '__main__':                                                                                
#     start_time = time.time()                                                                            
#     pool = Pool(processes=3)                                                  
#     pool.map(run_process, processes)   
#     pool.close()
#     pool.join()
#     total_time = round(time.time() - start_time,2)
#     print("Total time for running processes in parallel with pool: ", total_time)
# 
# #Total time for running processes in parallel:  ~93
# =============================================================================
