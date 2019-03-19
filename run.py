from proxy import get, check
from api import run_web

if __name__ == '__main__':
    from multiprocessing import Process
    p_list = []
    funcs = [get, check, run_web]
    for f in funcs:
        p = Process(target=f)
        p_list.append(p)
        p.start()

    for p in p_list:
        p.join()