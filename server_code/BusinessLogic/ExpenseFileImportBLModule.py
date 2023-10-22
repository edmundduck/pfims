import anvil.server
from fuzzywuzzy import fuzz
from ..SysProcess import LoggingModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = LoggingModule.ServerLogger()

@anvil.server.callable('predict_relevant_labels')
@logger.log_function
def predict_relevant_labels(srclbl, curlbl):
    """
    Return a label which has the highest proximity (a.k.a. the most matched) from the DB from the source label.

    Parameters:
        srclbl (list): The labels extracted from Excel to be compared.
        curlbl (list): The label dropdown from the DB labels table.

    Returns:
        score (list): Proximity score of each label, its order follows the order of the srclbl.
    """
    # Max 100, min 0
    min_proximity = 40
    score = []
    for s in srclbl:
        highscore = [0, None]
        for lbl in curlbl:
            similarity = fuzz.ratio(s, lbl[1][1])
            # logger.trace(f"lbl={lbl[1][1]}, similarity={similarity}, highscore[0]={highscore[0]}")
            if similarity > highscore[0]:
                highscore = (similarity, tuple([lbl[1][0], lbl[1][1]]))
        score.append(highscore[1] if highscore[0] > min_proximity else None)
    return score
