#from MOMP.io.input import 
from MOMP.lib.loader import dic, cfg

from itertools import product

#print(dic)
#print("\n", cfg)



def iter_list(dic, ext="_list"):
    layout_pool = []
    # for field in layout:
    for field in dic["layout"]:
        # lst = globals().get(field + ext, None)
        lst = dic.get(field + ext)  # .copy()
        layout_pool.append(lst)
    return layout_pool


def iter_list_ref(dic, ext="_list"):
    layout_pool = []
    for field in dic["layout"]:
        lst = dic.get(field + ext)  # .copy()
        if field == "model":
            #    model_ref = lst.pop(0)
            # layout_pool.append(lst)
            model_ref = lst[0]
            layout_pool.append(lst[1:])
        else:
            layout_pool.append(lst)
    return layout_pool, model_ref


dd = {'layout': ('model', 'ensemble', 'window'), 'model_list': ('AIFS', 'NGCM'), 'ensemble_list': (1, 2, 3, 4, 5), 'window_list': (1, 16)}

layout_pool = iter_list(dd)
print(layout_pool)
for combi in product(*layout_pool):
    print(combi)
