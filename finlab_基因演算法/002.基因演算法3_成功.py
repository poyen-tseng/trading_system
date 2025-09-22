import numpy as np

# from scipy.stats import percentileofscore


# 初始化種群
# pop_size: 種群大小 較大的種群可以包含更多的基因組合，從而增加種群的多樣性，這有助於避免演算法陷入局部最優解
# gene_length: 基因長度（這裡是4，對應A, B, C, D）
def initialize_population(pop_size, gene_length):
    # 隨機生成範圍在[-10, 10]之間的實數種群
    return np.random.uniform(-10, 10, size=(pop_size, gene_length))


# 適應度函數 要被優化的東西 或者代表自然環境
# individual: 個體（包含A, B, C, D的值）
def fitness(individual):
    A, B, C, D = individual
    # 計算適應度，這裡我們希望最小化函數值，因此取負數
    return -(A**2 + B**2 + C**2 + D**2)


# 計算每個元素的百分位數
def calculate_percentile(array, value):
    # 排序陣列
    sorted_array = np.sort(array)
    rank = np.searchsorted(sorted_array, value, side="right")
    percentile = (rank / len(array)) * 100
    return percentile


# 選擇函數
# population: 種群
# fitnesses: 每個個體的適應度
# 適應度高的個體更有可能被選中，但適應度低的個體也有一定的機會被選中
def selection(population, fitnesses):
    total_fitness = max(fitnesses)
    # 計算每個個體被選中的概率
    # probabilities = [f / total_fitness for f in fitnesses]
    probabilities = [calculate_percentile(fitnesses, f) / 100 for f in fitnesses]
    # print("fitnesses=", fitnesses)
    # print("probabilities=", probabilities)
    # print()
    # 計算累積概率
    cumulative_probabilities = np.cumsum(probabilities)
    # 生成一個隨機數
    r = np.random.rand()
    # 根據累積概率選擇個體
    for i, cumulative_probability in enumerate(cumulative_probabilities):
        if r < cumulative_probability:
            return population[i]


# 交叉函數
# parent1, parent2: 父母個體
def crossover(parent1, parent2):
    # 隨機選擇交叉點
    point = np.random.randint(1, len(parent1))
    # 生成子代個體
    child1 = np.concatenate((parent1[:point], parent2[point:]))
    child2 = np.concatenate((parent2[:point], parent1[point:]))
    return child1, child2


# 變異函數
# individual: 個體
# mutation_rate: 變異率
def mutate(individual, mutation_rate):
    for i in range(len(individual)):
        # 以變異率的概率對基因進行變異
        if np.random.rand() < mutation_rate:
            individual[i] += np.random.uniform(-1, 1)
            # 生成一個範圍在-1到1之間的隨機數，並將這個隨機數加到當前基因的值上。這樣，基因的值會在一定範圍內隨機變化。
    return individual


# 基因演算法主函數
# pop_size: 種群大小
# gene_length: 基因長度
# generations: 迭代次數
# mutation_rate: 變異率
def genetic_algorithm(pop_size, gene_length, generations, mutation_rate=0.1):
    # 初始化種群
    population = initialize_population(pop_size, gene_length)
    for generation in range(generations):
        # 計算每個個體的適應度 準備下一輪的淘汰
        fitnesses = [fitness(ind) for ind in population]
        new_population = []
        for _ in range(pop_size // 2):
            # 選擇父母個體
            parent1 = selection(population, fitnesses)
            parent2 = selection(population, fitnesses)
            # 交叉生成子代
            child1, child2 = crossover(parent1, parent2)
            # 變異子代
            new_population.append(mutate(child1, mutation_rate))
            new_population.append(mutate(child2, mutation_rate))
        # 更新種群
        population = np.array(new_population)
        # 找到當前代的最佳適應度和個體

        best_fitness = max(fitnesses)
        best_individual = population[np.argmax(fitnesses)]
        # print(np.round(np.argmax(fitnesses), 1))
        # print(np.round(best_individual), 1)
        # print()
        # argmax回傳fitness陣列中，最大值的所在位置
        # 然後用population叫他們出列
        print(
            f"Generation {generation}: Best Fitness = {best_fitness}, Best Individual = {best_individual}",
            end="\r      ",
        )

    return population


# 例子
final_population = genetic_algorithm(pop_size=50, gene_length=4, generations=10000)
