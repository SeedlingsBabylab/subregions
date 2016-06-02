import csv
import sys
import re

rank_regx = re.compile("(\d+)( of )(\d+)")

class Subregion(object):
    def __init__(self, filename, rank, onset):
        self.filename = filename
        self.rank = rank
        self.onset = onset
        self.offset = None

        self.word_count = 0

        self.words = []

    def __repr__(self):
        return "\n\n{} [ \n\trank: {} \n\tonset: {} \n\toffset: {}\n]".format(self.filename,
                                                                 self.rank,
                                                                 self.onset,
                                                                 self.offset)


def get_subregions(all_comments):
    subregions = []
    curr_subregion = None
    content = ""
    for index, comment in enumerate(all_comments):
        content = comment[3]
        if "subregion" in content:
            if "starts" in content:
                rank_reg_result = rank_regx.search(content)
                rank = None
                onset_split = comment[2].split("_")
                print onset_split
                onset = onset_split[1]
                print index
                if rank_reg_result:
                    rank = rank_reg_result.group(1)

                curr_subregion = Subregion(comment[0], rank, onset)
                print curr_subregion
            if "ends" in content:
                offset = comment[2].split("_")[1]
                curr_subregion.offset = offset
                subregions.append(curr_subregion)

    return subregions


if __name__ == "__main__":

    comments_file = sys.argv[1]
    #basic_level_file = sys.argv[2]

    all_comments = []
    with open(comments_file, "rU") as comments:
        reader = csv.reader(comments)
        reader.next()
        for comment in reader:
            all_comments.append(comment)

    # all_basic_levels = []
    # with open(basic_level_file, "rU") as basic_level:
    #     reader = csv.reader(basic_level)
    #     reader.next()
    #     for entry in reader:
    #         all_basic_levels.append(entry)

    subregions = get_subregions(all_comments)

    print subregions
