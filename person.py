from __future__ import annotations
from typing import Set
from collections import deque


class Person:
    def __init__(self, name: str):
        self.name: str = name
        self.parent: Person | None = None
        self.children: Set[Person] = set()
        self.friends: Set[Person] = set()
        self.all_relevant: Set[Person] = set()

    def add_child(self, child: Person) -> Person:
        if not isinstance(child, Person):
            raise ValueError("Child should be a Person")

        # Prevent a cycle in the family tree.
        ancestor = self
        while ancestor is not None:
            if ancestor is child:
                raise ValueError("Adding this child would create a cycle")
            ancestor = ancestor.parent

        if child.parent is not None:
            raise ValueError("Child already has a parent")

        child.parent = self
        self.children.add(child)

        # Store the family connection in both directions for reachability.
        self.all_relevant.add(child)
        child.all_relevant.add(self)

        return self

    def make_friend(self, friend: Person) -> Person:
        if not isinstance(friend, Person):
            raise ValueError("Friend should be a Person")

        if friend is self:
            raise ValueError("You cannot be friends with yourself")

        # Friendship is an undirected connection.
        self.friends.add(friend)
        friend.friends.add(self)

        self.all_relevant.add(friend)
        friend.all_relevant.add(self)

        return self

    def is_ancestor(self, target_person: Person) -> bool:
        if not isinstance(target_person, Person):
            raise ValueError("Target person must be a Person instance")

        # Walk up from the target through its parents.
        parent = target_person.parent
        while parent is not None:
            if parent is self:
                return True

            parent = parent.parent

        return False

    def can_reach(self, right_person: Person) -> bool:
        left_person = self
        if not isinstance(right_person, Person):
            raise ValueError("Target person must be a Person instance")

        if left_person == right_person:
            return True

        # Return early if they are directly connected.
        if right_person in self.all_relevant:
            return True

        # Search outward from both people.
        left_visited: Set[Person] = {left_person}
        right_visited: Set[Person] = {right_person}
        left_queue: deque[Person] = deque([left_person])
        right_queue: deque[Person] = deque([right_person])
        expand_left_on_tie = True

        while left_queue and right_queue:
            # Expand the smaller frontier; alternate when they are equal.
            if len(left_queue) < len(right_queue):
                expand_left = True
            elif len(right_queue) < len(left_queue):
                expand_left = False
            else:
                expand_left = expand_left_on_tie
                expand_left_on_tie = not expand_left_on_tie

            if not expand_left:
                current_queue = right_queue
                current_visited = right_visited
                other_side_visited = left_visited
            else:
                current_queue = left_queue
                current_visited = left_visited
                other_side_visited = right_visited

            # Expand one BFS layer.
            for _ in range(len(current_queue)):
                current_person = current_queue.popleft()

                for neighbor in current_person.all_relevant:
                    # The two searches have met.
                    if neighbor in other_side_visited:
                        return True

                    if neighbor not in current_visited:
                        current_visited.add(neighbor)
                        current_queue.append(neighbor)

        return False

    def can_reach_single(self, target_person: Person) -> bool:
        if not isinstance(target_person, Person):
            raise ValueError("Target person must be a Person instance")

        if self is target_person:
            return True

        if target_person in self.all_relevant:
            return True

        # Search outward from this person using one queue.
        queue: deque[Person] = deque([self])
        visited: Set[Person] = {self}

        while queue:
            current_person = queue.popleft()
            if current_person is target_person:
                return True

            for relevant in current_person.all_relevant:
                if relevant not in visited:
                    visited.add(relevant)
                    queue.append(relevant)

        return False
