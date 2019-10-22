from operator import itemgetter
from te_settings import Direction, MAXCOL, MAXROW
 

class AutoPlayer():
    def __init__(self, controller):
        self.controller = controller
        self.best_move = None
        self.first_move = True
        self.next_block_type = None
        self.weights = {"holes": -0.35663, "completed_lines": 0.760666,
                        "aggregate_height": -0.510066, "roughness": -0.184483}
        self.set_ones = [bin(i).count('1') for i in range(1024)]
        self.tetronimos = {"I": (([15], [30], [60], [120], [240], [480], [960]),
                    ([1, 1, 1, 1], [2, 2, 2, 2], [4, 4, 4, 4], [8, 8, 8, 8], [16, 16, 16, 16], [32, 32, 32, 32],
                     [64, 64, 64, 64], [128, 128, 128, 128], [256, 256, 256, 256],
                     [512, 512, 512, 512])),
                      "L": (([1, 7], [2, 14], [4, 28], [8, 56], [16, 112], [32, 224], [64, 448], [128, 896]),
                            ([2, 2, 3], [4, 4, 6], [8, 8, 12], [16, 16, 24], [32, 32, 48], [64, 64, 96],
                             [128, 128, 192], [256, 256, 384], [512, 512, 768]),
                            ([7, 4], [14, 8], [28, 16], [56, 32], [112, 64], [224, 128], [448, 256], [896, 512]),
                            ([3, 1, 1], [6, 2, 2], [12, 4, 4], [24, 8, 8], [48, 16, 16], [96, 32, 32],
                             [192, 64, 64], [384, 128, 128], [768, 256, 256])),
                      "J": (([4, 7], [8, 14], [16, 28], [32, 56], [64, 112], [128, 224], [256, 448], [512, 896]),
                            ([3, 2, 2], [6, 4, 4], [12, 8, 8], [24, 16, 16], [48, 32, 32], [96, 64, 64],
                             [192, 128, 128], [384, 256, 256], [768, 512, 512]),
                            ([7, 1], [14, 2], [28, 4], [56, 8], [112, 16], [224, 32], [448, 64], [896, 128]),
                            ([1, 1, 3], [2, 2, 6], [4, 4, 12], [8, 8, 24], [16, 16, 48], [32, 32, 96],
                             [64, 64, 192], [128, 128, 384], [256, 256, 768])),
                      "O": (([3, 3], [6, 6], [12, 12], [24, 24], [48, 48], [96, 96], [192, 192], [384, 384],
                             [768, 768]),),
                      "Z": (([6, 3], [12, 6], [24, 12], [48, 24], [96, 48], [192, 96], [384, 192], [768, 384]),
                            ([1, 3, 2], [2, 6, 4], [4, 12, 8], [8, 24, 16], [16, 48, 32], [32, 96, 64],
                             [64, 192, 128], [128, 384, 256], [256, 768, 512])),
                      "S": (([3, 6], [6, 12], [12, 24], [24, 48], [48, 96], [96, 192], [192, 384], [384, 768]),
                            ([2, 3, 1], [4, 6, 2], [8, 12, 4], [16, 24, 8], [32, 48, 16], [64, 96, 32],
                             [128, 192, 64], [256, 384, 128], [512, 768, 256])),
                      "T": (([2, 7], [4, 14], [8, 28], [16, 56], [32, 112], [64, 224], [128, 448], [256, 896]),
                            ([2, 3, 2], [4, 6, 4], [8, 12, 8], [16, 24, 16], [32, 48, 32], [64, 96, 64],
                             [128, 192, 128], [256, 384, 256], [512, 768, 512]),
                            ([7, 2], [14, 4], [28, 8], [56, 16], [112, 32], [224, 64], [448, 128], [896, 256]),
                            ([1, 3, 1], [2, 6, 2], [4, 12, 4], [8, 24, 8], [16, 48, 16], [32, 96, 32],
                             [64, 192, 64], [128, 384, 128], [256, 768, 256]))}

        self.directions = {"[15]": (0, 3), "[30]": (0, 2), "[60]": (0, 1), "[120]": (0, 0), "[240]": (0, -1),
                      "[480]": (0, -2), "[960]": (0, -3), "[1, 1, 1, 1]": (1, 4), "[2, 2, 2, 2]": (1, 3),
                      "[4, 4, 4, 4]": (1, 2), "[8, 8, 8, 8]": (1, 1), "[16, 16, 16, 16]": (1, 0),
                      "[32, 32, 32, 32]": (1, -1), "[64, 64, 64, 64]": (1, -2), "[128, 128, 128, 128]": (1, -3),
                      "[256, 256, 256, 256]": (1, -4), "[512, 512, 512, 512]": (1, -5),
                      "[1, 7]": (0, 4), "[2, 14]": (0, 3), "[4, 28]": (0, 2), "[8, 56]": (0, 1), "[16, 112]": (0, 0),
                      "[32, 224]": (0, -1), "[64, 448]": (0, -2), "[128, 896]": (0, -3), "[2, 2, 3]": (1, 4),
                      "[4, 4, 6]": (1, 3), "[8, 8, 12]": (1, 2), "[16, 16, 24]": (1, 1), "[32, 32, 48]": (1, 0),
                      "[64, 64, 96]": (1, -1), "[128, 128, 192]": (1, -2), "[256, 256, 384]": (1, -3),
                      "[512, 512, 768]": (1, -4), "[7, 4]": (2, 4), "[14, 8]": (2, 3), "[28, 16]": (2, 2),
                      "[56, 32]": (2, 1), "[112, 64]": (2, 0), "[224, 128]": (2, -1), "[448, 256]": (2, -2),
                      "[896, 512]": (2, -3), "[3, 1, 1]": (-1, 5), "[6, 2, 2]": (-1, 4), "[12, 4, 4]": (-1, 3),
                      "[24, 8, 8]": (-1, 2), "[48, 16, 16]": (-1, 1), "[96, 32, 32]": (-1, 0),
                      "[192, 64, 64]": (-1, -1),
                      "[384, 128, 128]": (-1, -2), "[768, 256, 256]": (-1, -3), "[4, 7]": (0, 4), "[8, 14]": (0, 3),
                      "[16, 28]": (0, 2), "[32, 56]": (0, 1), "[64, 112]": (0, 0), "[128, 224]": (0, -1),
                      "[256, 448]": (0, -2), "[512, 896]": (0, -3), "[3, 2, 2]": (1, 4), "[6, 4, 4]": (1, 3),
                      "[12, 8, 8]": (1, 2), "[24, 16, 16]": (1, 1), "[48, 32, 32]": (1, 0), "[96, 64, 64]": (1, -1),
                      "[192, 128, 128]": (1, -2), "[384, 256, 256]": (1, -3), "[768, 512, 512]": (1, -4),
                      "[7, 1]": (2, 4), "[14, 2]": (2, 3), "[28, 4]": (2, 2), "[56, 8]": (2, 1),
                      "[112, 16]": (2, 0), "[224, 32]": (2, -1), "[448, 64]": (2, -2), "[896, 128]": (2, -3),
                      "[1, 1, 3]": (-1, 5), "[2, 2, 6]": (-1, 4), "[4, 4, 12]": (-1, 3), "[8, 8, 24]": (-1, 2),
                      "[16, 16, 48]": (-1, 1), "[32, 32, 96]": (-1, 0), "[64, 64, 192]": (-1, -1),
                      "[128, 128, 384]": (-1, -2), "[256, 256, 768]": (-1, -3),
                      "[3, 3]": (0, 4), "[6, 6]": (0, 3), "[12, 12]": (0, 2), "[24, 24]": (0, 1), "[48, 48]": (0, 0),
                      "[96, 96]": (0, -1), "[192, 192]": (0, -2), "[384, 384]": (0, -3), "[768, 768]": (0, -4),
                      "[6, 3]": (0, 4), "[12, 6]": (0, 3), "[24, 12]": (0, 2), "[48, 24]": (0, 1), "[96, 48]": (0, 0),
                      "[192, 96]": (0, -1), "[384, 192]": (0, -2), "[768, 384]": (0, -3), "[1, 3, 2]": (1, 4),
                      "[2, 6, 4]": (1, 3), "[4, 12, 8]": (1, 2), "[8, 24, 16]": (1, 1), "[16, 48, 32]": (1, 0),
                      "[32, 96, 64]": (1, -1), "[64, 192, 128]": (1, -2), "[128, 384, 256]": (1, -3),
                      "[256, 768, 512]": (1, -4), "[3, 6]": (0, 4), "[6, 12]": (0, 3), "[12, 24]": (0, 2),
                      "[24, 48]": (0, 1), "[48, 96]": (0, 0), "[96, 192]": (0, -1), "[192, 384]": (0, -2),
                      "[384, 768]": (0, -3), "[2, 3, 1]": (1, 4), "[4, 6, 2]": (1, 3), "[8, 12, 4]": (1, 2),
                      "[16, 24, 8]": (1, 1), "[32, 48, 16]": (1, 0), "[64, 96, 32]": (1, -1),
                      "[128, 192, 64]": (1, -2), "[256, 384, 128]": (1, -3), "[512, 768, 256]": (1, -4),
                      "[2, 7]": (0, 4), "[4, 14]": (0, 3), "[8, 28]": (0, 2), "[16, 56]": (0, 1), "[32, 112]": (0, 0),
                      "[64, 224]": (0, -1), "[128, 448]": (0, -2), "[256, 896]": (0, -3), "[2, 3, 2]": (1, 4),
                      "[4, 6, 4]": (1, 3), "[8, 12, 8]": (1, 2), "[16, 24, 16]": (1, 1), "[32, 48, 32]": (1, 0),
                      "[64, 96, 64]": (1, -1), "[128, 192, 128]": (1, -2), "[256, 384, 256]": (1, -3),
                      "[512, 768, 512]": (1, -4), "[7, 2]": (2, 4), "[14, 4]": (2, 3), "[28, 8]": (2, 2),
                      "[56, 16]": (2, 1), "[112, 32]": (2, 0), "[224, 64]": (2, -1), "[448, 128]": (2, -2),
                      "[896, 256]": (2, -3), "[1, 3, 1]": (-1, 5), "[2, 6, 2]": (-1, 4), "[4, 12, 4]": (-1, 3),
                      "[8, 24, 8]": (-1, 2), "[16, 48, 16]": (-1, 1), "[32, 96, 32]": (-1, 0),
                      "[64, 192, 64]": (-1, -1), "[128, 384, 128]": (-1, -2), "[256, 768, 256]": (-1, -3)}

    def next_move(self, gamestate):
        if gamestate.get_falling_block_position()[1] == 1 or self.first_move:
            grid = self.convert_to_bin_arr(gamestate.get_tiles())
            block_type = gamestate.get_falling_block_type()
            self.next_block_type = gamestate.get_next_block_type()
            self.best_move = self.get_best_move(self.get_all_possible_moves(grid, block_type, 1))
            self.first_move = False
        if self.best_move["rotation"] > 0:
            gamestate.rotate(Direction.RIGHT)
            self.best_move["rotation"] -= 1
        elif self.best_move["rotation"] < 0:
            gamestate.rotate(Direction.LEFT)
            self.best_move["rotation"] += 1
        if self.best_move["translation"] > 0:
            gamestate.move(Direction.RIGHT)
            self.best_move["translation"] -= 1
        elif self.best_move["translation"] < 0:
            gamestate.move(Direction.LEFT)
            self.best_move["translation"] += 1

    def get_all_possible_moves(self, grid, block_type, iterations):
        return list(map(self.get_move, [(grid.copy(), t, iterations) for r in self.tetronimos[block_type] for t in r]))

    def get_move(self, args):
        grid, block, iterations, min_y = args[0], args[1], args[2], 0
        while min_y < MAXROW and not grid[min_y]:
            min_y += 1
        y, length = min_y, len(block)
        while y < MAXROW:
            if any(block[length - 1 - i] & grid[y - i] for i in range(length)):
                break
            y += 1
        for i in range(length):
            grid[y - 1 - i] |= block[length - 1 - i]
        rating = self.get_rating(grid)
        if iterations == 1:
            next_possible_moves = self.get_all_possible_moves(grid, self.next_block_type, 2)
            rating += self.get_best_move(next_possible_moves)["rating"]
        return {"block": block, "rating": rating}

    def get_best_move(self, possible_moves):
        best_move = max(possible_moves, key=itemgetter("rating"))
        directions = self.directions[str(best_move["block"])]
        return {"rotation": directions[0], "translation": directions[1], "rating": best_move["rating"]}

    def convert_to_bin_arr(self, tiles):
        grid = []
        for y in range(MAXROW):
            row = 0
            for x in range(0, MAXCOL):
                if tiles[y][x]:
                    row += 2 ** (9 - x)
            grid.append(row)
        return grid

    def get_rating(self, grid):
        rating = 0
        rating += self.get_holes(grid) * self.weights["holes"]
        rating += self.get_completed_lines(grid) * self.weights["completed_lines"]
        rating += self.get_aggregate_height(grid) * self.weights["aggregate_height"]
        rating += self.get_roughness(grid) * self.weights["roughness"]
        return rating

    def get_holes(self, grid):
        under_mask = holes = min_y = 0
        while min_y < MAXROW and not grid[min_y]:
            min_y += 1
        for y in range(min_y, MAXROW):
            row = grid[y]
            holes += self.set_ones[under_mask & (row ^ 1023)]
            under_mask |= row
        return holes

    def get_completed_lines(self, grid):
        return grid.count(1023)

    def get_aggregate_height(self, grid):
        return sum(self.get_peaks(grid))

    def get_roughness(self, grid):
        peaks = self.get_peaks(grid)
        roughness = 0
        for i in range(0, len(peaks) - 1):
            roughness += abs(peaks[i] - peaks[i + 1])
        return roughness

    def get_peaks(self, grid):
        peaks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for x in range(MAXCOL):
            min_y, mask = 0, 512 >> x
            while min_y < MAXROW and not grid[min_y]:
                min_y += 1
            for y in range(min_y, MAXROW):
                if grid[y] & mask:
                    peaks[x] = MAXROW - y
                    break
        return peaks
