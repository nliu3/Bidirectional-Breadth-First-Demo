from person import Person
from random import Random
from statistics import mean
from time import perf_counter

REPEATS = 5
LOOPS = 10


def make_people(prefix: str, count: int) -> list[Person]:
    return [Person(f"{prefix} {i}") for i in range(count)]


def connect_chain(people: list[Person]) -> None:
    for first, second in zip(people, people[1:]):
        first.make_friend(second)


def add_query(
    queries: list[tuple[str, Person, Person, bool]],
    label: str,
    start: Person,
    target: Person,
    expected: bool,
) -> None:
    queries.append((label, start, target, expected))


def build_test_cases() -> list[tuple[str, Person, Person, bool]]:
    queries: list[tuple[str, Person, Person, bool]] = []

    # 1. Long chain: distant, nearby, and unreachable pairs.
    chain = make_people("Chain", 1_200)
    connect_chain(chain)
    isolated_chain_person = Person("Isolated from chain")

    add_query(queries, "Long chain: far apart", chain[0], chain[-1], True)
    add_query(queries, "Long chain: nearby", chain[500], chain[501], True)
    add_query(
        queries,
        "Long chain: unreachable",
        chain[0],
        isolated_chain_person,
        False,
    )

    # 2. Family tree: ancestor, different branches, and separate families.
    root = Person("Family Root")
    levels = [[root]]

    for depth in range(6):
        next_level = []

        for parent_index, parent in enumerate(levels[-1]):
            for child_index in range(3):
                child = Person(f"Family {depth}-{parent_index}-{child_index}")
                parent.add_child(child)
                next_level.append(child)

        levels.append(next_level)

    other_family = Person("Other Family")

    add_query(queries, "Family tree: ancestor to descendant", root, levels[-1][-1], True)
    add_query(
        queries,
        "Family tree: across branches",
        levels[-1][0],
        levels[-1][-1],
        True,
    )
    add_query(
        queries,
        "Family tree: separate families",
        root,
        other_family,
        False,
    )

    # 3. Grid: opposite corners, neighboring nodes, and an isolated node.
    rows, columns = 30, 30
    grid = [
        [Person(f"Grid {row}-{column}") for column in range(columns)]
        for row in range(rows)
    ]

    for row in range(rows):
        for column in range(columns):
            if column + 1 < columns:
                grid[row][column].make_friend(grid[row][column + 1])
            if row + 1 < rows:
                grid[row][column].make_friend(grid[row + 1][column])

    isolated_grid_person = Person("Isolated from grid")

    add_query(queries, "Grid: opposite corners", grid[0][0], grid[-1][-1], True)
    add_query(queries, "Grid: neighboring nodes", grid[10][10], grid[10][11], True)
    add_query(
        queries,
        "Grid: unreachable",
        grid[0][0],
        isolated_grid_person,
        False,
    )

    # 4. Shared hub: the start and target connect through many intermediate nodes.
    hub_start = Person("Hub Start")
    hub_target = Person("Hub Target")

    for index in range(200):
        hub = Person(f"Hub {index}")
        hub_start.make_friend(hub)
        hub_target.make_friend(hub)

    isolated_hub_person = Person("Isolated from hub")

    add_query(queries, "Shared hub: reachable", hub_start, hub_target, True)
    add_query(
        queries,
        "Shared hub: unreachable",
        hub_start,
        isolated_hub_person,
        False,
    )

    # 5. Clustered network: each group has several internal links,
    # and the groups are connected by bridge links.
    groups = [make_people(f"Group {group}", 60) for group in range(5)]

    for group in groups:
        # Connect each group in a ring, then add some local cross-links.
        for index, person in enumerate(group):
            person.make_friend(group[(index + 1) % len(group)])
            person.make_friend(group[(index + 3) % len(group)])

    for left_group, right_group in zip(groups, groups[1:]):
        left_group[-1].make_friend(right_group[0])

    separate_group = make_people("Separate Group", 60)
    connect_chain(separate_group)

    add_query(
        queries,
        "Clustered network: across groups",
        groups[0][0],
        groups[-1][-1],
        True,
    )
    add_query(
        queries,
        "Clustered network: separate components",
        groups[0][0],
        separate_group[-1],
        False,
    )

    # 6. Random sparse network: use a fixed seed for a consistent graph.
    random_people = make_people("Random", 500)
    connect_chain(random_people)  # Ensure the main network is connected.
    rng = Random(4530)

    for _ in range(1_500):
        first = rng.choice(random_people)
        second = rng.choice(random_people)

        if first is not second:
            first.make_friend(second)

    isolated_random_person = Person("Isolated from random network")

    add_query(
        queries,
        "Random sparse network: reachable",
        random_people[0],
        random_people[-1],
        True,
    )
    add_query(
        queries,
        "Random sparse network: unreachable",
        random_people[0],
        isolated_random_person,
        False,
    )

    return queries


def average_runtime_ms(function) -> float:
    # Run once to warm up; do not include this run in the measurements.
    function()

    samples = []

    for _ in range(REPEATS):
        start_time = perf_counter()

        for _ in range(LOOPS):
            function()

        elapsed = perf_counter() - start_time
        samples.append(elapsed * 1_000 / LOOPS)

    return mean(samples)


def main() -> None:
    queries = build_test_cases()
    single_times = []
    bidirectional_times = []

    print(
        f"Each query was measured over {REPEATS} rounds, "
        f"with {LOOPS} runs per round. Times are in milliseconds.\n"
    )
    print(
        f"{'Test case':<38} {'Result':<8} "
        f"{'Single-source BFS':>18} {'Bidirectional BFS':>20} {'Ratio':>9}"
    )

    for label, start, target, expected in queries:
        single_result = start.can_reach_single(target)
        bidirectional_result = start.can_reach(target)

        assert single_result == expected, (
            f"{label}: single-source BFS returned the wrong result; "
            f"expected {expected}, got {single_result}"
        )
        assert bidirectional_result == expected, (
            f"{label}: bidirectional BFS returned the wrong result; "
            f"expected {expected}, got {bidirectional_result}"
        )

        single_ms = average_runtime_ms(lambda: start.can_reach_single(target))
        bidirectional_ms = average_runtime_ms(lambda: start.can_reach(target))

        single_times.append(single_ms)
        bidirectional_times.append(bidirectional_ms)

        ratio = single_ms / bidirectional_ms if bidirectional_ms > 0 else float("inf")

        print(
            f"{label:<38} {str(expected):<8} "
            f"{single_ms:>10.4f} ms "
            f"{bidirectional_ms:>12.4f} ms "
            f"{ratio:>8.2f}x"
        )

    average_single = mean(single_times)
    average_bidirectional = mean(bidirectional_times)
    overall_ratio = average_single / average_bidirectional

    print("\nAverage time across all queries:")
    print(f"Single-source BFS: {average_single:.4f} ms")
    print(f"Bidirectional BFS: {average_bidirectional:.4f} ms")
    print(f"Average time ratio (single / bidirectional): {overall_ratio:.2f}x")

    if average_single < average_bidirectional:
        print("In this test set, single-source BFS had a shorter average runtime.")
    elif average_bidirectional < average_single:
        print("In this test set, bidirectional BFS had a shorter average runtime.")
    else:
        print("In this test set, both methods had the same average runtime.")


if __name__ == "__main__":
    main()