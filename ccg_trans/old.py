def old():
    # Rule 1: only one categ in one place
    orders: list[z3.Function] = []
    for idx in range(len(categories)):
        orders.append(z3.Function(f"{idx}-th", z3.BoolSort(), z3.BoolSort()))
        only_one_in_order = z3_only_one(orders[idx], categories)
        cons.append(only_one_in_order)
        print(f"{idx}-th: {only_one_in_order}")

    # Rule 2: if categ is in some order, it must be in the categories
    conds = []
    for categ in [np, s, s_l_np, s_r_np]:
        conds.append(
            z3.And(
                categ,
                # [z3_only_one(order_f, ) for order_f in orders]
            )
        )
    cons.append(Or(conds))
    # composition
    # compose = z3.Function(
    #     "compose", z3.BoolSort(), z3.BoolSort(), z3.BoolSort()
    # )
    # for x, y in product([np, s, s_l_np, s_r_np], repeat=2):
    #     if x == np and y == s_l_np:
    #         for idx in range(seq_length - 1):
    #             c_compose1 = z3.And(
    #                 orders[idx](x), orders[idx + 1](y), compose(x, y)
    #             )
    #             solver.add(c_compose1)
    #     elif x == s_r_np and y == np:
    #         for idx in range(seq_length - 1):
    #             c_compose2 = z3.And(
    #                 orders[idx](x), orders[idx + 1](y), compose(x, y)
    #             )
    #             solver.add(c_compose2)
    #     else:
    #         pass

    # coordination
    # coord = z3.Function(R"coord", z3.BoolSort(), z3.BoolSort(), z3.BoolSort())

    # combinators
    # bll = z3.Function(R"B\\ ", z3.BoolSort(), z3.BoolSort(), z3.BoolSort())
    # blr = z3.Function(R"B\/ ", z3.BoolSort(), z3.BoolSort(), z3.BoolSort())
    # brr = z3.Function(R"B// ", z3.BoolSort(), z3.BoolSort(), z3.BoolSort())
    # brl = z3.Function(R"B/\ ", z3.BoolSort(), z3.BoolSort(), z3.BoolSort())

    # sll = z3.Function(R"S\\ ", z3.BoolSort(), z3.BoolSort(), z3.BoolSort())
    # slr = z3.Function(R"S\/ ", z3.BoolSort(), z3.BoolSort(), z3.BoolSort())
    # srr = z3.Function(R"S// ", z3.BoolSort(), z3.BoolSort(), z3.BoolSort())
    # srl = z3.Function(R"S/\ ", z3.BoolSort(), z3.BoolSort(), z3.BoolSort())

    # tll = z3.Function(R"T\\ ", z3.BoolSort(), z3.BoolSort())
    # tlr = z3.Function(R"T\/ ", z3.BoolSort(), z3.BoolSort())
    # trr = z3.Function(R"T// ", z3.BoolSort(), z3.BoolSort())
    # trl = z3.Function(R"T/\ ", z3.BoolSort(), z3.BoolSort())

    combinators = [
        ForAll(B, kll(x, B) == x/B),  # TODO
    ]
    for c in combinators:
        solver.add(c)


def sliding_window(iterable, n=2):
    it = iter(iterable)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def z3_only_one(func: Callable, args: list[z3.BoolRef]) -> z3.BoolRef:
    conditions = []

    for i in range(len(args)):
        cond = And(
            [func(c) if i == j else Not(func(c)) for j, c in enumerate(args)]
        )
        conditions.append(cond)

    return Or(conditions)


def old_fun():
    sats = [sat for sat in solve(cats=cats, seq_length=eval_lenth)]

    # TODO: the case eval_lenth != 2
    for (idx1, c1), (idx2, c2) in product(enumerate(cats), repeat=eval_lenth):
        # print(f"c1: {c1}, c2: {c2}")
        if {c1, c2} in sats:
            print("solved")
            for p1, p2 in sliding_window(pred, n=2):
                score += p1[idx1] * p2[idx2]
        else:
            pass

    if score == 0:
        return 0.0
    loss = -log(score / len(pred))
    loss = torch.Tensor([0.0]).to(device)

    return loss
