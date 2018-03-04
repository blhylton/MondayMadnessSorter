import csv
from sys import argv
from sys import exit
import random


class PlayerList:
    def __init__(self):
        self.players = {}
        self.players['napc'] = []
        self.players['naps'] = []
        self.players['naxb'] = []
        self.players['eupc'] = []
        self.players['eups'] = []
        self.players['euxb'] = []

    def append(self,  player):
        self.players[player.region + player.platform].append(player)

    def generate_teams(self):
        teams = {}
        teams['napc'] = []
        teams['naps'] = []
        teams['naxb'] = []
        teams['eupc'] = []
        teams['eups'] = []
        teams['euxb'] = []

        for key in self.players:
            extras = len(self.players[key]) % 6
            team_count = int((len(self.players[key]) - extras) / 6)
            if team_count < 2:
                print(
                    'Not enough people to make teams for {} - {} :('.format(key[:2].upper(), key[2:].upper()))
                continue
            self.players[key].sort()

            for i in range(0, team_count):
                del i
                teams[key].append(Team())

            idx = 0
            while self.players[key]:
                if idx >= team_count:
                    idx = 0
                    teams[key].sort()

                teams[key][idx].players.append(self.players[key].pop())
                idx += 1

        return teams


class Team:
    def __init__(self):
        self.team_name = ''
        self.region = ''
        self.platform = ''
        self.captain_discord = ''
        self.players = []

    def sr_avg(self):
        if len(self.players) == 0:
            return 0

        avg = 0
        sum = 0
        for player in self.players:
            sum += player.sr

        avg = sum/len(self.players)

        return avg

    def __lt__(self, other):
        return self.sr_avg() < other.sr_avg()

    def __str__(self):
        val_str = 'SR: {}\n'.format(round(self.sr_avg()))
        for player in self.players:
            val_str += str(player)

        return val_str + '----------\n'


class Player:
    def __init__(self, discord='', battle_tag='', sr=0):
        self.discord = discord
        self.battle_tag = battle_tag
        self.sr = int(sr)
        self.region = ''
        self.platform = ''

    def __str__(self):
        return '{: <20} {: <40}\n'.format(self.battle_tag, self.discord)

    def parse_csv_row(self, row):
        self.discord = row[2]
        self.battle_tag = row[3]
        self.sr = int(row[5])
        self.region = self._handle_region(row[6])
        self.platform = self._handle_platform(row[7])

    def _handle_region(self, region_entry):
        if 'Americas' in region_entry:
            return 'na'
        return 'eu'

    def _handle_platform(self, platform_entry):
        if platform_entry == 'PC (Battle.net)':
            return 'pc'
        elif platform_entry == 'Playstation 4':
            return 'ps'
        return 'xb'

    def __lt__(self, other):
        return self.sr < other.sr


class DuplicateBattleTagException(Exception):
    def __init__(self, message):
        self.message = message


def dedupe(input_file_location):
    with open(input_file_location, 'r', encoding="latin-1", newline='') as input_file:
        battle_tags = {}
        reader = csv.reader(input_file)
        # Ignore header row
        next(reader, None)
        for idx, row in enumerate(reader, start=2):
            if row[2]:
                if row[2] not in battle_tags.values():
                    battle_tags['C' + str(idx)] = row[2]
                else:
                    for cell, tag in battle_tags.items():
                        if tag == row[2]:
                            raise DuplicateBattleTagException(
                                'Duplicate battle tag in {} and {}{}'.format(cell, 'C', str(idx)))


if 'help' in argv[1]:
    print(
        '\nUsage: mondaymadness <input_file.csv> [pretty_output_file.txt] [importable_output_file.txt]')
    print('\n\tIf no output files are specified, the default files are \'pretty-output.txt\' and \'importable-output.txt\' and will be placed relative to the executable.')
    exit()

input_file = argv[1]
pretty_output_file = argv[2] if len(argv) > 2 else 'pretty-output.txt'
importer_output_file = argv[3] if len(argv) > 3 else 'importable-output.txt'

try:
    dedupe(input_file)
except DuplicateBattleTagException as e:
    print(e.message)
    exit()

p_list = PlayerList()

f = open(input_file, 'r', encoding="latin-1", newline='')

reader = csv.reader(f)
# Ignore header row
next(reader, None)
for row in reader:
    player = Player()
    player.parse_csv_row(row)
    p_list.append(player)

f.close()

teams = p_list.generate_teams()
with open(pretty_output_file, 'w', encoding='latin-1') as out:
    for key in teams:
        if len(teams[key]) > 0:
            out.write(
                '\n========== {} - {} =========\n'.format(key[:2].upper(), key[2:].upper()))
            for team in teams[key]:
                out.write(str(team))


# with open(importer_output_file, 'w', encoding='latin-1') as out:
#     for idx, team in enumerate(Teams.teams, start=1):
#         out.write('{}\t{}\t{}\t{}\n'.format(team.team_name, team.captain_discord,
#                                             round(team.sr_avg()), '{} - {}'.format(team.region.upper(), team.platform.upper())))

#         for player in team.players:
#             out.write('{}\t{}\t{}\n'.format(
#                 player.battle_tag, player.discord, player.sr))
#         out.write('\n')
