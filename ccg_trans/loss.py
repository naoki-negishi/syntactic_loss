# Third Party Library
import torch
from loguru import logger


def scoring(supertags, valid_cat_seq, pred):
    # valid_cat_seq = ['np', 's\\np']
    score = torch.tensor(1.0)
    for i, cat in enumerate(valid_cat_seq):
        score *= pred[i][supertags.index(cat)]
    logger.debug(f"categ seq: {valid_cat_seq} -> score: {score}")
    return score


def wmc(
    supertags: list[str],
    valid_category_sequence: list[tuple[str]],
    pred: list[list[torch.Tensor]],
    sentences: list[str],
    # lexicon: dict[str, str],
) -> torch.Tensor:
    wmc_score = 0.0

    for sent_idx, sent in enumerate(sentences):
        n = len(sent.split())
        logger.info(f"target sentence: {sent}")
        logger.info(f"\tsupertags: {supertags}")
        logger.info(f"\t-> pred: {pred[sent_idx]}")
        for v_cat_seq in valid_category_sequence:
            if len(v_cat_seq) == n:
                wmc_score += scoring(supertags, v_cat_seq, pred[sent_idx])
        logger.info(f"wmc_score: {wmc_score}\n")

    loss = -torch.log(wmc_score)
    return loss


def cross_entropy_loss(
    pred: list[list[torch.Tensor]],
    sentences: list[str],
    lexicon: dict[str, str],
) -> torch.Tensor:
    score = torch.tensor(0.0)

    gold_tags = []
    for sent in sentences:
        words = sent.split()
        gold_tags.append([lexicon[word] for word in words])

    for sent_idx, sent in enumerate(sentences):
        n = len(sent.split())
        logger.info(f"target sentence: {sent}")
        for i in range(n):
            for j in range(len(pred[sent_idx][i])):
                score += gold_tags[sent_idx][i] == j
        logger.info(f"score: {score}\n")

    ce_loss = -torch.log(score)
    return ce_loss


def syntactic_loss_function(
    supertags: list[str],
    valid_cat_seqs: list[str],
    preds: list[list[torch.Tensor]],
    sentences: list[str],
    lexicon: dict[str, str],
    alpha: float = 0.5,
) -> torch.Tensor:
    wmc_loss = wmc(supertags, valid_cat_seqs, preds, sentences)
    ce_loss = cross_entropy_loss(preds, sentences, lexicon)

    return alpha * wmc_loss + (1 - alpha) * ce_loss
