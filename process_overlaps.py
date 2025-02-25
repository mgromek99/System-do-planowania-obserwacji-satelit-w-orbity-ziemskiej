
def process_overlaps(input_tuple, tuple_list, overlap_list):
    input_start, input_end = input_tuple
    new_tuples = []
    for idx, (start, end) in enumerate(tuple_list):
        if start < input_end and end > input_start:
            # Calculate the overlap
            overlap_start = max(start, input_start)
            overlap_end = min(end, input_end)
            overlap = (overlap_start, overlap_end)

            # Add overlap to overlap_list if not already present
            if overlap not in overlap_list:
                overlap_list.append(overlap)

                # Modify the original tuple_list
                start_check = start == overlap_start
                end_check = end == overlap_end
                if not (start_check and end_check):
                    if start_check:  # overlap at start, append 2nd part as free
                        new_tuples.append((overlap_end, end))
                    elif end_check:  # overlap at end, append 1st part as free
                        new_tuples.append((start, overlap_start))
                    else:  # overlap in middle, append 1st and 3rd part as free
                        new_tuples.append((start, overlap_start))
                        new_tuples.append((overlap_end, end))

        else:  # If no changes will be made, append old data to new list
            new_tuples.append((start, end))

    tuple_list.clear()
    tuple_list.extend(new_tuples)


