from person import Person

def main():
    grandpa = Person("Grandpa")
    parent = Person("Parent")
    alice = Person("Alice")
    bob = Person("Bob")
    stranger = Person("Stranger")

    # Build the family tree.
    grandpa.add_child(parent)
    parent.add_child(alice)

    # Add a friendship connection.
    alice.make_friend(bob)

    # Test 1: ancestor checks.
    print("Grandpa is Alice's ancestor:", grandpa.is_ancestor(alice))
    print("Alice is Grandpa's ancestor:", alice.is_ancestor(grandpa))

    # Test 2: reachability checks.
    print("Grandpa can reach Bob:", grandpa.can_reach(bob))
    print("Grandpa can reach Stranger:", grandpa.can_reach(stranger))


if __name__ == "__main__":
    main()