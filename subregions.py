import csv
import sys
import re

rank_regx = re.compile("(\d+)( of )(\d+)")

class Subregions(object):
    def __init__(self):
        self.subregions = []

    def for_file(self, filename):
        """
        Returns a list of subregion objests for the specified file
        :return: subregions
        """
        regions = []
        for subregion in self.subregions:
            if subregion.filename == filename:
                regions.append(subregion)

        return regions

    def add(self, subregion):
        """
        Adds a given subregion to the collection of all subregions
        :param subregion: a Subregion object
        """
        self.subregions.append(subregion)


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
    subregions = Subregions()
    curr_subregion = None
    content = ""
    for index, comment in enumerate(all_comments):
        content = comment[3]
        if "subregion" in content:
            if "starts" in content:
                rank_reg_result = rank_regx.search(content)
                rank = None
                onset = comment[2].split("_")[1]
                if rank_reg_result:
                    rank = rank_reg_result.group(1)

                curr_subregion = Subregion(comment[0], rank, onset)
                print curr_subregion
            if "ends" in content:
                offset = comment[2].split("_")[1]
                curr_subregion.offset = offset
                subregions.add(curr_subregion)

    return subregions

def basic_level_file_partition(all_basic_level, filename):
    bl_for_file = []

    for entry in all_basic_level:
        if entry[0][0:5] == filename[0:5]:
            bl_for_file.append(entry)

    return bl_for_file


if __name__ == "__main__":

    filename = sys.argv[1]
    comments_file = sys.argv[2]
    basic_level_file = sys.argv[3]

    all_comments = []
    with open(comments_file, "rU") as comments:
        reader = csv.reader(comments)
        reader.next()
        for comment in reader:
            all_comments.append(comment)

    all_basic_levels = []
    with open(basic_level_file, "rU") as basic_level:
        reader = csv.reader(basic_level)
        reader.next()
        for entry in reader:
            all_basic_levels.append(entry)

    all_subregions = get_subregions(all_comments)
    bl_for_file = basic_level_file_partition(all_basic_levels, filename)

    print all_subregions
    print bl_for_file

    subr_for_file = all_subregions.for_file(filename)
    print subr_for_file
