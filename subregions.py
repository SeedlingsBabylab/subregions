import csv
import sys
import re
import os

rank_regx = re.compile("(\d+)( of )(\d+)")

class AllFiles(object):
    def __init__(self):
        self.files = {}


    def add_file(self, subregion_group):
        self.files[subregion_group.file] = subregion_group

    def get_file(self, file):
        if file not in self.files:
            return None
        else:
            return self.files[file]


class SubregionGroup(object):
    def __init__(self):
        """
        self.subregions is a dictionary mapping subregion ranks
        to subregion objects. Each SubregionGroup represents a single
        CLAN file
        """
        self.file = ""

        self.subregions = {}
        self.unbounded_words = []


    def get_subregion(self, region_rank):
        """
        Returns a subregion objects for the specified rank
        :return: subregion
        """
        if region_rank not in self.subregions:
            return None
        else:
            return self.subregions[region_rank]


    def add(self, subregion):
        """
        Adds a given subregion to the collection of all subregions
        :param subregion: a Subregion object
        """
        self.subregions[subregion.rank] = subregion

        self.file = subregion.filename[0:5]

    def fill_with_basic_levels(self, basic_levels):
        for bl in basic_levels:
            time_split = bl[6].split("_")
            onset = time_split[0]
            offset = time_split[1]
            word_added_to_subregion = False

            for rank, region in self.subregions.iteritems():
                if (region.onset <= onset) and (region.offset >= offset):
                    region.add_word(bl)
                    word_added_to_subregion = True

            if not word_added_to_subregion:
                self.unbounded_words.append(bl)

    def output(self):
        """
        Outputs each subregion into it's own csv containing all the words.
        The words that were not bounded within a subregion will be in their
        own seperate subregion.
        """
        # make directory for the file
        file_dir = self.file
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        header = ["id", "tier", "object", "utterance_type",
                  "object_present", "speaker", "timestamp",
                  "basic_level"]

        # make directory for the subregions
        for rank, region in self.subregions.iteritems():
            region_file = os.path.join(file_dir, "subregion_{}.csv".format(rank))
            with open(region_file, "wb") as output:
                writer = csv.writer(output)
                writer.writerow(header)
                for word in region.words:
                    writer.writerow(word)

        unbounded_words_path = os.path.join(file_dir, "ubnounded_words.csv")
        with open(unbounded_words_path, "wb") as unbounded:
            writer = csv.writer(unbounded)
            writer.writerow(header)
            for word in self.unbounded_words:
                writer.writerow(word)

class Subregion(object):
    def __init__(self, filename, rank, onset, line):
        self.filename = filename
        self.rank = rank
        self.onset = onset
        self.offset = None
        self.line = line

        self.word_count = 0

        self.words = []

    def __repr__(self):
        return "\n\n{} [ \n\trank: {} \n\tonset: {} \n\toffset: {}\n]"\
            .format(self.filename,
                    self.rank,
                    self.onset,
                    self.offset)

    def add_word(self, word):
        """

        :param word: basic_level entry
        """
        self.words.append(word)


def get_subregions(all_comments):
    subregions = SubregionGroup()
    all_files = AllFiles()
    curr_subregion = None
    curr_file = ""
    content = ""
    first_subr = True
    for index, comment in enumerate(all_comments):
        content = comment[3]
        if "subregion" in content:
            if "starts" in content:
                if (curr_file != comment[0]) and not first_subr:
                    all_files.add_file(subregions)
                    subregions = SubregionGroup()

                curr_file = comment[0]
                rank_reg_result = rank_regx.search(content)
                rank = None
                onset = comment[2].split("_")[1]
                line = comment[1]
                if rank_reg_result:
                    rank = rank_reg_result.group(1)

                curr_subregion = Subregion(comment[0], rank, onset, line)
                print curr_subregion
            if "ends" in content:
                offset = comment[2].split("_")[1]
                curr_subregion.offset = offset
                subregions.add(curr_subregion)
                first_subr = False

    return all_files



def basic_level_file_partition(all_basic_level, filename):
    bl_for_file = []

    for entry in all_basic_level:
        if entry[0][0:5] == filename[0:5]:
            bl_for_file.append(entry)

    return bl_for_file


if __name__ == "__main__":

    filename = sys.argv[1][0:5]
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

    subr_for_file = all_subregions.get_file(filename)

    subr_for_file.fill_with_basic_levels(bl_for_file)

    print subr_for_file

    subr_for_file.output()

    #subr_for_file = all_subregions.for_file(filename)
    #print subr_for_file
