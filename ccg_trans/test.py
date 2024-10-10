# Standard Library
import sys
from itertools import product

# Third Party Library
import torch
from loguru import logger
from solver import solve, solve_ccg
from tqdm import tqdm

# First Party Library
from loss import syntactic_loss_function, wmc
from psg import LanguageGenerator, RegularGrammar
from utils.utils import raw_tags_to_tuple, tuple_to_raw_tags

MAX_SENTENCE_LENGTH = 3


def test_psg():
    nt = frozenset(["S", "NP", "NTVP", "TVP", "Det", "CN", "IV", "TV"])
    t = frozenset(["the", "cat", "dog", "walk", "likes"])
    p = {
        "S": [("NP", "IV"), ("Det", "NTVP")],
        "NP": [("Det", "CN")],
        "NTVP": [("CN", "TVP")],
        "TVP": [("TV", "NP")],
        "Det": ["the"],
        "CN": ["cat", "dog"],
        "IV": ["walk"],
        "TV": ["likes"],
    }
    s = "S"

    rg = RegularGrammar(non_term=nt, term=t, prod_rule=p, start=s)
    rg.print_grammar()
    print()
    # print(rg.model_dump_json())

    lg = LanguageGenerator(rg)
    sentences = lg.random_generate(max_length=5, num=5)
    for s in sentences:
        print(" ".join(s))


def test_solver():
    raw_test_supetags = [
        "np",
        R"s\np",
        R"s/np",
        R"(s\np)/np",
        R"(s\np)\np",
        R"(s/np)/np",
        R"(s/np)\np",
        R"np/(s\np)",
        R"np/(s/np)",
        R"np\(s\np)",
        R"np\(s/np)",
        R"np\((s/np)/np)",
    ]  # supertags
    logger.info(f"test supertags: {raw_test_supetags}")
    test_categories = list(map(raw_tags_to_tuple, raw_test_supetags))

    cat_seqs = []
    for seq_len in range(1, MAX_SENTENCE_LENGTH + 1):
        logger.info(f"===== seq_length: {seq_len} =====")
        # for seq in tqdm(
        #     product(test_categories, repeat=seq_len),
        #     leave=False,
        #     total=len(test_categories) ** seq_len,
        # ):
        for seq in product(test_categories, repeat=seq_len):
            # logger.debug(f"seq: {seq}")
            # if solve(antec, conseq):
            if solve(seq):
                raw_seq = list(map(tuple_to_raw_tags, seq))
                cat_seqs.append(raw_seq)

        for seq in cat_seqs:
            if len(seq) == seq_len:
                logger.info(seq)

    return cat_seqs


def test_wmc():
    test_supetags = [
        "np",
        R"s\np",
        R"s/np",
        R"(s\np)/np",
        R"(s\np)\np",
    ]  # supertags
    logger.info(f"test supertags: {test_supetags}")

    lexicon = {
        "John": "np",
        "Mary": "np",
        "walks": R"s\np",
        "loves": R"(s\np)/np",
    }
    logger.info(f"lexicon: {lexicon}")

    sentences = [
        "John walks",
        "John loves Mary",
    ]
    logger.info(f"sentences: {sentences}\n")

    # model = MyModel(test_categories)
    valid_cat_seqs = solve_ccg(test_supetags, MAX_SENTENCE_LENGTH)

    alpha = 0.5
    for batch in range(1):  # here, meanless loop
        # pred = model(batch)
        test_pred = [
            [
                torch.Tensor([0.8, 0.1, 0.1, 0.0, 0.0]),
                torch.Tensor([0.1, 0.7, 0.1, 0.1, 0.0]),
            ],  # for "John walks"
            [
                torch.Tensor([0.1, 0.1, 0.1, 0.7, 0.0]),
                torch.Tensor([0.1, 0.1, 0.1, 0.1, 0.6]),
                torch.Tensor([0.1, 0.1, 0.1, 0.1, 0.6]),
            ],  # for "John loves Mary"
        ]

        wmc_loss = wmc(test_supetags, valid_cat_seqs, test_pred, sentences)
        logger.info(f"wmc_loss: {wmc_loss}")

        loss = syntactic_loss_function(
            test_supetags,
            valid_cat_seqs,
            test_pred,
            sentences,
            lexicon,  # or directly, gold
            alpha,
        )
        logger.debug(f"overall loss: {loss}")


@logger.catch
def main(args):
    if args[0] == "-psg":
        test_psg()
    elif args[0] == "-solver":
        test_solver()
    elif args[0] == "-wmc":
        test_wmc()


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[0] == "-d":
        lev = "DEBUG"
    elif args[0] == "-i":
        lev = "INFO"

    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<level>{message}</level>",
        level=lev,
    )
    main(args[1:])
