from proxy_pool import get, check, run_web
from multiprocessing import Process



if __name__ == '__main__':
    pros = list()
    funcs = [get, check, run_web]

    for f in funcs:
        p = Process(target=f)
        pros.append(p)
        p.start()

    for p in pros:
        p.join()