def place_substrings(main_string: str, substrings: list[tuple[str, int]], already_sorted: bool = False) -> str:
    """
    Places substrings into the main string at specified positions.

    :param main_string: The original string where substrings will be placed.
    :param substrings: A list of tuples, each containing a substring and its position.
    :param already_sorted: If True, assumes substrings are already sorted by position in descending order.
    :return: The modified string with substrings placed at specified positions.
    """
    if not already_sorted:
        # Sort substrings by position in descending order to avoid index shifting
        substrings.sort(key=lambda x: x[1], reverse=True)

    for substring, position in substrings:
        if 0 <= position <= len(main_string):
            main_string = main_string[:position] + substring + main_string[position:]
        else:
            raise ValueError(f"Position {position} is out of bounds for the main string.")

    return main_string
