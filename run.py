from proxy_pool import get, check, run_web
from multiprocessing import Process



if __name__ == '__main__':
    p_list = list()
    funcs = [get, check, run_web]

    for f in funcs:
        p = Process(target=f)
        p_list.append(p)
        p.start()

    for p in p_list:
        p.join()