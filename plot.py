import importlib


def _get_output_root(output_root):
    return "/home/k77wu/Desktop/" \
           + "fast-wasserstein-adversarial/" \
           + "output/" \
           + output_root


def print_func(acc, avg_iter, avg_time, overflow=False, converge=True):
    if overflow:
        print(" & $-$ & $-$ & $-$", end="")

    elif converge is not True:
        print(" & ${:4.1f}$ & ${:5d}*$ & ${:6.1f}$".format(acc, int(avg_iter), avg_time), end="")

    else:
        print(" & ${:4.1f}$ & ${:5d}$ & ${:6.1f}$".format(acc, int(avg_iter), avg_time), end="")


if __name__ == "__main__":
    sinkhorn = importlib.import_module("run_sinkhorn")
    projected_gradient = importlib.import_module("run_projected_gradient")
    frank_wolfe = importlib.import_module("run_frank_wolfe")

    from script_utils import lst_eps

    # print("\\begin{table}")
    # print("\\centering")
    # print("\\begin{tabular}{c c c c c c}")
    # print("\\toprule")
    print("& \\multirow{2}{*}{method}                 & " + " & ".join(["\\multicolumn{{3}}{{c|}}{{$\\epsilon = {:5.3f}$}}".format(eps) for eps in lst_eps]) + " \\\\")
    print("& & " + " & ".join([" acc & iter & time ".format(eps) for eps in lst_eps]) + " \\\\")
    print("\\hline")

    from script_utils import enum2str
    from script_utils import TYPE
    print("\\multirow{{1}}{{*}}{{\\rotatebox[origin=c]{{90}}{{{}}}}}".format(enum2str[TYPE]))

    sinkhorn.collect_results(_get_output_root("sinkhorn"), print_func)
    projected_gradient.collect_results(_get_output_root("projected_gradient"), print_func)
    frank_wolfe.collect_results(_get_output_root("frank_wolfe"), print_func)

    # print("\\bottomrule")
    # print("\\end{tabular}")
    # print("\\end{table}")
