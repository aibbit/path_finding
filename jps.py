import heapq
import math

from func_timer import cost_time
from grid_map import GridMap
import distances


class Node:

    def __init__(self, parent, pos, g, h, weight=1):
        self.parent = parent
        self.pos = pos
        self.g = g
        self.h = h
        self.f = g + h * weight

    def __lt__(self, other):
        return self.f < other.f or ((self.f == other.f) and (self.h < other.h))

    def __str__(self):
        return 'Node:{}, g={} h={}'.format(self.pos, self.g, self.h)

    def get_direction(self):

        if self.parent is None:
            return [0, 0]
        else:
            return [a != b and (a - b) // abs(a - b) or 0 for a, b in zip(self.pos, self.parent.pos)]


# 启发函数 传入两个点坐标
def heuristic(a, b, n=2):

    dx = abs(b[0] - a[0])
    dy = abs(b[1] - a[1])

    # Manhattan Heuristic
    if n == 1:
        return dx + dy

    # Euclidean Heuristic
    elif n == 2:
        return (dx**2 + dy**2)**0.5

    # Chebychev Heuristic
    elif n == 3:
        return max(dx, dy)

    # Octile Heuristic
    else:
        return dx + dy + (2**0.5 - 2) * min(dx, dy)


@cost_time
def jps(map, start_x, start_y, end_x, end_y):

    # 起点和终点节点
    start = (start_x, start_y)
    end = (end_x, end_y)

    start_node = Node(None, start, 0, heuristic(start, end))
    # end_node = Node(None, end, 0, 0)

    # 检测起点和终点是否合法
    if(map.is_valid(start_x, start_y) is False):
        print('start point error')
        return []
    if(map.is_valid(end_x, end_y) is False):
        print('end point error')
        return []

    # 初始化：起点加入 open 列表
    open_list = []
    heapq.heappush(open_list, start_node)

    visited = dict()

    # 统计经过的节点数
    num_visited_nodes = 0

    # 开始搜索
    while len(open_list) > 0:

        # 取出openlist中f值最小的节点
        current_node = heapq.heappop(open_list)

        # 统计经过的节点数
        num_visited_nodes += 1

        # 如果找到了终点，结束搜索
        if current_node.pos == end:
            print("Find Path")
            break

        # identify successors
        neighbors = []
        successors = []

        if current_node.parent is not None:
            neighbors = map.get_prune_neighbors(current_node.pos, current_node.parent.pos)
        else:
            neighbors = map.get_neighbors(current_node.pos)

        for n in neighbors:
            next = map.jump(current_node.pos, (n[0] - current_node.pos[0], n[1] - current_node.pos[1]), end, -1)
            if next is not None:
                successors.append(next)

        for neighbor in successors:

            # 计算到相邻节点的移动代价 （g值） 直行代价为1 斜行代价为sqrt(2)
            # if neighbor[0] == current_node.pos[0] or neighbor[1] == current_node.pos[1]:
            #     g = current_node.g + 1
            # else:
            #     g = current_node.g + 1.4142

            g = current_node.g + distances.ComputeCost(current_node.pos, neighbor)

            h = heuristic(neighbor, end)
            neighbor_node = Node(current_node, neighbor, g, h)

            if neighbor_node.pos not in visited or g < visited[neighbor_node.pos].g:
                visited[neighbor_node.pos] = neighbor_node
                heapq.heappush(open_list, neighbor_node)

    # 统计总路径长度
    print('Total Length:', round(current_node.g, 4))
    # 统计经过的节点数
    print('Total Visited Nodes:', num_visited_nodes)

    # 回溯路径
    path = []

    # while current_node:
    #     path.append(current_node.pos)
    #     current_node = current_node.parent
    # path.reverse()

    while current_node:
        if current_node.parent:
            dir = current_node.get_direction()
            n = current_node.pos

            while n != current_node.parent.pos:
                path.append(n)
                n = (n[0] - dir[0], n[1] - dir[1])
        else:
            path.append(current_node.pos)
        current_node = current_node.parent
    path.reverse()

    return path


def main():

    map = GridMap()
    # Workaround 此处坐标轴xy相反

    # map.read_map_from_file("./map/test.map")
    # path = jps(map, 18, 1, 3, 16)

    map.read_map_from_file("./map/Aftershock.map")
    path = jps(map, 53, 502, 475, 495)   # 727.891

    # angle = calculate_turning_angles(path)
    # print('Total Angle:', round(angle, 4))

    # print(path)
    # print(visited)

    # 扩展节点 -> 灰色
    # print('visited:', len(visited))
    # for key in visited:
    #     map.set_map_value(key[0], key[1], 3)

    # 输出路径 -> 红色
    # print('path:', len(path))
    for (x, y) in path:
        map.set_map_value(x, y, 4)

    map.draw_map()


# for test
if __name__ == '__main__':

    main()
