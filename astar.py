import heapq
import math

from func_timer import cost_time
from grid_map import GridMap

class Node:

    def __init__(self, parent, pos, g, h):
        self.parent = parent
        self.pos = pos
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f

    def get_direction(self):
        return self.parent and (self.pos[0] - self.parent.pos[0], self.pos[1] - self.parent.pos[1]) or (0, 0)


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
def astar(map, start_x, start_y, end_x, end_y):

    # 起点和终点节点
    start = (start_x, start_y)
    end = (end_x, end_y)

    start_node = Node(None, start, 0, heuristic(start, end))
    # end_node = Node(None, end, 0, 0)

    # 检测起点和终点是否合法
    if(map.is_valid(start_x, start_y) is False):
        print('start point error')
        return [], []
    if(map.is_valid(end_x, end_y) is False):
        print('end point error')
        return [], []

    # 初始化：起点加入 open 列表
    open_list = []
    heapq.heappush(open_list, start_node)

    # closed_list = set()
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
            break

        # 将当前节点添加到closedlist中
        # closed_list.add(current_node.pos)

        # 搜索邻域节点
        # if current_node.parent is not None:
        #     neighbors = map.get_prune_neighbors(current_node.pos, current_node.parent.pos)
        # else:
        #     neighbors = map.get_neighbors(current_node.pos)

        neighbors = map.get_neighbors(current_node.pos)

        for neighbor in neighbors:
            # neighbor_node = current_node[0] + neighbor[0], current_node[1] + neighbor[1]

            # 判断邻域节点是否合法
            if map.is_valid(neighbor[0], neighbor[1]):

                # 如果邻居节点已经在closedlist中则忽略
                # if neighbor_pos in closed_list:
                #     continue

                # 计算到相邻节点的移动代价 （g值） 直行代价为1 斜行代价为sqrt(2)
                if neighbor[0] == current_node.pos[0] or neighbor[1] == current_node.pos[1]:
                    g = current_node.g + 1
                else:
                    g = current_node.g + 1.4142

                h = heuristic(neighbor, end)
                neighbor_node = Node(current_node, neighbor, g, h)

                # 如果邻居节点不在openlist中，则添加
                # 否则，如果新的路径比旧的路径更短，则更新节点的父节点和g值

                # if neighbor_node not in open_list:
                #     heapq.heappush(open_list, neighbor_node)
                # else:
                #     for node in open_list:
                #         if node == neighbor_node and node.g > neighbor_node.g:
                #             node.parent = current_node
                #             node.g = neighbor_node.g

                if neighbor_node.pos not in visited or g < visited[neighbor_node.pos].g:
                    visited[neighbor_node.pos] = neighbor_node
                    heapq.heappush(open_list, neighbor_node)

    # 回溯路径
    path = []

    # 统计总路径长度
    print('Total Length:', round(current_node.g, 4))
    # 统计经过的节点数
    print('Total Visited Nodes:', num_visited_nodes)

    while current_node is not None:
        path.append(current_node.pos)
        current_node = current_node.parent

    path.reverse()

    return path, visited.keys()


# 统计总转向角的度数
def calculate_turning_angles(path):

    # TODO测试
    dir = [a != b and (a - b) // abs(a - b) or 0 for a, b in zip(path[-1], path[0])]
    # print(dir)

    # 初始方向为终点方向
    # 角度顺时针计算

    prev_direction = dir
    total_turning_angle = 0

    # 遍历相邻节点，计算夹角
    for i in range(len(path) - 1):
        # 计算当前线段的方向向量
        direction = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        # 计算夹角
        turning_angle = math.acos(
            (prev_direction[0] * direction[0] + prev_direction[1] * direction[1]) /
            (math.sqrt(prev_direction[0]**2 + prev_direction[1]**2) * math.sqrt(direction[0]**2 + direction[1]**2))
        )
        # 更新总转向角度
        total_turning_angle += turning_angle
        # 更新当前方向向量
        prev_direction = direction

    # 将弧度转换为角度并返回
    return math.degrees(total_turning_angle)


def main():

    map = GridMap()
    # Workaround 此处坐标轴xy相反

    # map.read_map_from_file("./map/test.map")
    # path, visited = astar(map, 18, 1, 3, 16)

    map.read_map_from_file("./map/Aftershock.map")
    path, visited = astar(map, 53, 502, 475, 495)   # 727.891

    angle = calculate_turning_angles(path)
    print('Total Angle:', round(angle, 4))

    # print(path)
    # print(visited)

    # 扩展节点 -> 灰色
    # print('visited:', len(visited))
    for key in visited:
        map.set_map_value(key[0], key[1], 3)

    # 输出路径 -> 红色
    # print('path:', len(path))
    for (x, y) in path:
        map.set_map_value(x, y, 4)

    map.draw_map()


# for test
if __name__ == '__main__':

    main()
