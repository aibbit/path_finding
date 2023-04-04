import re
import matplotlib.pyplot as plt
from matplotlib import colors
import seaborn as sns


class ScenarioLoader:

    class Experiment:

        def __init__(self, bucket, mapname, map_width, map_height, s_x, s_y, g_x, g_y, optimal_len):
            self.bucket = bucket
            self.mapname = mapname
            self.map_width = map_width
            self.map_height = map_height
            self.s_x = s_x
            self.s_y = s_y
            self.g_x = g_x
            self.g_y = g_y
            self.optimal_len = optimal_len

        def get_mapname(self):
            return self.mapname

        def get_start_x(self):
            return self.s_x

        def get_start_y(self):
            return self.s_y

        def get_end_x(self):
            return self.g_x

        def get_end_y(self):
            return self.g_y

        def get_optimal_length(self):
            return self.optimal_len

    def __init__(self, filename):
        self.filename = filename
        self.experiments = []
        self.experimentsNum = 0

    def read_scen(self):

        file = open(self.filename)

        version = int(file.readline().split(' ')[1].rstrip(" ,\n"))
        # print(type(version))
        # print('version:', version)

        count = 0

        if(version == 1):
            while True:
                line = file.readline()

                if not line:
                    break

                count += 1

                # print(line.rstrip(" ,\n"))
                bucket, mapname, map_width, map_height, ss_x, s_y, g_x, g_y, ptimal_len = line.split('\t')
                exp = self.Experiment(bucket, mapname, map_width, map_height, ss_x, s_y, g_x, g_y, ptimal_len)
                self.experiments.append(exp)

            self.experimentsNum = count

        file.close()

    def get_nth_experiment(self, which):
        return (self.experiments[which])

    def print_scen(self):
        print(self.experiments[0].get_mapname())


def cal_dir(now, parent):
    dir = (a != b and (a - b) // abs(a - b) or 0 for a, b in zip(now, parent))
    return dir


class GridMap:
    def __init__(self):
        self.type = ''
        self.height = 0
        self.width = 0
        self.field = []

    def is_in_bounds(self, x, y):
        return (0 <= y < self.width) and (0 <= x < self.height)

    def is_obstacle(self, x, y):
        return self.field[x][y] == 2

    def is_valid(self, x, y):
        return self.is_in_bounds(x, y) and not self.is_obstacle(x, y)

    def get_neighbors(self, now_pos):

        (x, y) = now_pos
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if self.is_valid(x + dx, y + dy):
                    neighbors.append((x + dx, y + dy))

        neighbors.remove(now_pos)

        return neighbors

    def get_prune_neighbors(self, now_pos, parent_pos, indicateForcedNeighbors=False):

        neighbors = []

        (x, y) = now_pos
        # (dx, dy) = (now_pos[0] - parent_pos[0], now_pos[1] - parent_pos[1])
        (dx, dy) = cal_dir(now_pos, parent_pos)

        hasForcedNeighbors = False

        # Natural neighbour in the same direction
        if self.is_valid(x + dx, y + dy):
            neighbors.append((x + dx, y + dy))

        # Diagonal move
        if dx != 0 and dy != 0:
            # Natural neighbors
            if self.is_valid(x + dx, y):
                neighbors.append((x + dx, y))
            if self.is_valid(x, y + dy):
                neighbors.append((x, y + dy))

            # Forced neighbors
            if not self.is_valid(x - dx, y) and self.is_valid(x - dx, y + dy):
                neighbors.append((x - dx, y + dy))
                hasForcedNeighbors = True
            if not self.is_valid(x, y - dy) and self.is_valid(x + dx, y - dy):
                neighbors.append((x + dx, y - dy))
                hasForcedNeighbors = True

        # Straight move
        else:
            if dx != 0:
                for move in [-1, 1]:
                    if self.is_in_bounds(x, y + move) and self.is_obstacle(x, y + move) and self.is_valid(x + dx, y + move):
                        neighbors.append((x + dx, y + move))
                        hasForcedNeighbors = True
            else:
                for move in [-1, 1]:
                    if self.is_in_bounds(x + move, y) and self.is_obstacle(x + move, y) and self.is_valid(x + move, y + dy):
                        neighbors.append((x + move, y + dy))
                        hasForcedNeighbors = True

        if indicateForcedNeighbors:
            return neighbors, hasForcedNeighbors

        return neighbors

    def jump(self, pos, dir, end, limit=-1):

        if not self.is_valid(pos[0] + dir[0], pos[1] + dir[1]):
            return None

        next = (pos[0] + dir[0], pos[1] + dir[1])

        if next == end or limit == 0:
            return next

        if limit > -1:
            limit -= 1

        _, hasForced = self.get_prune_neighbors(next, pos, indicateForcedNeighbors=True)
        if hasForced:
            return next

        # Diagonal move
        if dir[0] != 0 and dir[1] != 0:
            if (self.jump(next, (0, dir[1]), end, limit) is not None or self.jump(next, (dir[0], 0), end, limit) is not None):
                return next

        return self.jump(next, dir, end, limit)

    def set_map_value(self, x, y, value):
        self.field[x][y] = value

    def read_map_from_file(self, filename):

        file = open(filename)

        map_type = file.readline()
        self.type = map_type.split(' ')[1].rstrip(" ,\n")

        map_height = file.readline()
        self.height = int(map_height.split(' ')[1])

        map_width = file.readline()
        self.width = int(map_width.split(' ')[1])

        file.readline()

        while True:
            line = file.readline()

            if not line:
                break

            # print(line.rstrip(" ,\n"))

            map_data = line.rstrip(" ,\n")
            map_data = re.sub(r'[.]', '0,', map_data)           # 可通行区域
            map_data = re.sub(r'[@|T]', '2,', map_data)         # 障碍物

            line_parse = lambda line: [int(i) for i in line.split(',')]
            map_data = line_parse(map_data.rstrip(" ,','"))

            self.field.append(map_data)

        file.close()

    def draw_map(self):

        # rows = len(field)
        # cols = len(field[0])

        cmap = colors.ListedColormap(['none', 'white', 'black', 'gray', 'red', 'yellow', 'green', 'cyan', 'blue'])

        # 绘图函数
        plt.figure()
        ax = plt.gca()
        ax.axis('equal')  # 保持栅格的横纵坐标刻度一致

        # 隐藏坐标轴和网格
        ax.axis('off')
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        # 绘制热力图
        # 其中vmin和vmax对应栅格地图数值的颜色与cmap一一对应
        # cbar设置false将色条设置为不可见
        ax = sns.heatmap(self.field,
                         cmap=cmap,
                         vmin=0,
                         vmax=8,
                         ax=ax,
                         cbar=False)

        # plt.savefig("1-1.jpg", dpi=500, bbox_inches='tight', pad_inches=0)
        plt.show()


# for test
if __name__ == '__main__':
    f = ScenarioLoader("./map/Aftershock.map.scen")
    f.read_scen()
    print(f.get_nth_experiment(1).get_start_x())
