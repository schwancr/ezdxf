#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import math
import random
import time

import ezdxf.addons.binpacking as bp

SEED = 47856535


def make_sample(n: int, max_width: float, max_height: float, max_depth: float):
    for _ in range(n):
        yield (
            random.random() * max_width,
            random.random() * max_height,
            random.random() * max_depth,
        )


def make_flat_packer(items) -> bp.FlatPacker:
    packer = bp.FlatPacker()
    for index, (w, h) in enumerate(items):
        packer.add_item(str(index), w, h)
    return packer


def make_3d_packer(items) -> bp.Packer:
    packer = bp.Packer()
    for index, (w, h, d) in enumerate(items):
        packer.add_item(str(index), w, h, d)
    return packer


def setup_flat_packer(n: int) -> bp.FlatPacker:
    items = make_sample(n, 20, 20, 20)
    packer = make_flat_packer(
        ((round(w) + 1, round(h) + 1) for w, h, d in items)
    )
    area = packer.get_unfitted_volume()
    w = round(math.sqrt(area) / 2.0)
    h = w * 1.60
    packer.add_bin("bin", w, h)
    return packer


def setup_3d_packer(n: int) -> bp.Packer:
    items = make_sample(n, 20, 20, 20)
    packer = make_3d_packer(
        ((round(w) + 1, round(h) + 1, round(d) + 1) for w, h, d in items)
    )
    volume = packer.get_unfitted_volume()
    s = round(math.pow(volume, 1.0 / 3.1))
    packer.add_bin("bin", s, s, s)
    return packer


def print_result(p0: bp.AbstractPacker, t: float):
    box = p0.bins[0]
    print(
        f"Packed {len(box.items)} items in {t:.3f}s, "
        f"ratio: {p0.get_fill_ratio():.3f}"
    )


def run_bigger_first(packer: bp.AbstractPacker):
    print("\nBigger first strategy:")
    p0 = packer.copy()
    strategy = bp.PickStrategy.BIGGER_FIRST
    t0 = time.perf_counter()
    p0.pack(strategy)
    t1 = time.perf_counter()
    print_result(p0, t1 - t0)


def run_shuffle(packer: bp.AbstractPacker, shuffle_count: int):
    print("\nShuffle strategy:")
    n_shuffle = shuffle_count
    t0 = time.perf_counter()
    p0 = bp.shuffle_pack(packer, n_shuffle)
    t1 = time.perf_counter()
    print(f"Shuffle {n_shuffle}x, best result:")
    print_result(p0, t1 - t0)


def run_genetic_driver(packer: bp.AbstractPacker, generations: int, dns_count: int):
    def feedback(driver: bp.GeneticDriver):
        print(
            f"gen: {driver.generation:4}, "
            f"stag: {driver.stagnation:4}, "
            f"fitness: {driver.best_fitness:.3f}"
        )
        return False

    print(f"\nGenetic algorithm search: gens={generations}, DNS strands={dns_count}")
    n_generations = generations
    n_dns_strands = dns_count
    gd = bp.GeneticDriver(packer, n_generations)
    gd.mutation_type1 = bp.MutationType.FLIP
    gd.mutation_type2 = bp.MutationType.FLIP
    gd.add_random_dna(n_dns_strands)
    gd.execute(feedback, interval=10.0)
    print(
        f"GeneticDriver: {n_generations} generations x {n_dns_strands} "
        f"DNS strands, best result:"
    )
    print_result(gd.best_packer, gd.runtime)


if __name__ == "__main__":
    random.seed(SEED)
    packer = setup_3d_packer(50)
    # packer = setup_flat_packer(50)
    print(packer.bins[0])
    print(f"Total item count: {len(packer.items)}")
    print(f"Total item volume: {packer.get_unfitted_volume():.3f}")
    run_bigger_first(packer)
    run_shuffle(packer, shuffle_count=100)
    run_genetic_driver(packer, generations=500, dns_count=50)
