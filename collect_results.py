import sys

if __name__ == "__main__":
    import importlib

    module = importlib.import_module(sys.argv[1][:-3])

    collect_results = module.collect_results
    output_root = "/home/k77wu/Desktop/" \
                  + "fast-wasserstein-adversarial/" \
                  + module.output_root.split("fast-wasserstein-adversarial")[1]
    print(output_root)

    collect_results(output_root)
