import pygame
import random
import matplotlib.pyplot as plt
import matplotlib
import numpy as np  # 需要numpy来简化基尼系数的计算

# 解决matplotlib中文显示问题 (This part is for displaying Chinese characters in Matplotlib, can be removed if not needed)
# matplotlib.rcParams['font.sans-serif'] = ['SimHei'] # Using default fonts is better for English
matplotlib.rcParams['axes.unicode_minus'] = False

# --- 1. 游戏化窗口设置 (Window and Color Setup) ---
BLUE, SAND, GREEN, RED, PURPLE, BLACK, WHITE, NET_COLOR, GREY = (135, 206, 250), (244, 164, 96), (34, 139, 34), (
    220, 20, 60), (128, 0, 128), (0, 0, 0), (255, 255, 255), (112, 128, 144), (169, 169, 169)
WIDTH, HEIGHT = 900, 700  # 稍微增大窗口以容纳更多信息
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Island Economy Simulator (V8 - Inequality Analysis)")  # 窗口标题改为英文
pygame.font.init()
# 字体改为通用英文字体
FONT = pygame.font.SysFont("Arial", 24)
SMALL_FONT = pygame.font.SysFont("Arial", 16)
STATUS_FONT = pygame.font.SysFont("Arial", 18)
HUD_FONT = pygame.font.SysFont("Arial", 20)  # HUD字体


# (Islander 类和其方法完全不变，我们只修改 IslandEconomy)
# Islander class and its methods remain unchanged as they contain no Chinese strings.
class Islander:
    def __init__(self, name, color, home_pos, risk_propensity):
        self.name, self.color, self.home_pos, self.risk_propensity = name, color, home_pos, risk_propensity
        self.fish_in_hand, self.has_net, self.hunger, self.is_active = 0, False, 0, True
        self.is_investing, self.days_spent_investing, self.investment_duration = False, 0, 2
        self.action, self.pos, self.target_pos, self.speed = 'idle', list(home_pos), list(home_pos), 2
        self.daily_production = 0

    def update_position(self):
        if not self.is_active: return
        dx, dy = self.target_pos[0] - self.pos[0], self.target_pos[1] - self.pos[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < self.speed:
            self.pos = list(self.target_pos)
        else:
            self.pos[0] += (dx / dist) * self.speed;
            self.pos[1] += (dy / dist) * self.speed

    def draw(self, screen):
        draw_color = self.color if self.is_active else GREY
        pygame.draw.circle(screen, draw_color, self.pos, 15)
        if self.has_net:
            net_rect = pygame.Rect(self.pos[0] - 20, self.pos[1] - 20, 10, 10)
            pygame.draw.rect(screen, NET_COLOR, net_rect, 2)
            pygame.draw.line(screen, NET_COLOR, (net_rect.left, net_rect.centery), (net_rect.right, net_rect.centery),
                             1)
            pygame.draw.line(screen, NET_COLOR, (net_rect.centerx, net_rect.top), (net_rect.centerx, net_rect.bottom),
                             1)

    def decide_and_act(self):
        self.daily_production = 0
        if not self.is_active: self.action = 'out'; return
        if self.is_investing:
            self.action = 'investing';
            self.target_pos = self.home_pos;
            self.days_spent_investing += 1
            if self.days_spent_investing >= self.investment_duration:
                self.is_investing = False;
                self.days_spent_investing = 0
                if random.random() < 0.5: self.has_net = True
            return
        can_afford = self.fish_in_hand >= self.investment_duration
        if not self.has_net and can_afford and random.random() < self.risk_propensity:
            self.is_investing = True;
            self.days_spent_investing = 0;
            self.decide_and_act();
            return
        self.action = 'fishing';
        self.target_pos = [random.randint(50, WIDTH - 50), 50]
        fish_caught = 3 if self.has_net else random.choice([1, 2]);
        self.fish_in_hand += fish_caught;
        self.daily_production = fish_caught

    def end_of_day_consumption(self):
        if not self.is_active: return
        if self.fish_in_hand > 0:
            self.fish_in_hand -= 1;
            self.hunger = 0
        else:
            self.hunger += 1
        if self.hunger >= 3: self.is_active = False; self.action = 'out'


# --- 3. 经济体 (增加基尼系数的计算与展示) ---
class IslandEconomy:
    def __init__(self):
        self.islanders = [
            Islander("Able", GREEN, (WIDTH // 4, HEIGHT // 2), risk_propensity=0.1),
            Islander("Baker", RED, (WIDTH // 2, HEIGHT // 2), risk_propensity=0.0),
            Islander("Charlie", PURPLE, (WIDTH * 3 // 4, HEIGHT // 2), risk_propensity=0.0),
        ]
        self.day = 0
        self.history = {
            'day': [], 'gdp': [], 'total_wealth': [], 'capital_stock': [], 'population': [],
            'gini_coefficient': [],  # *** 新增：基尼系数历史记录 ***
            'individual_wealth': {agent.name: [] for agent in self.islanders}
        }

    # *** 新增：计算基尼系数的函数 ***
    def _calculate_gini(self, wealths):
        """计算基尼系数。输入为财富列表。"""
        if not wealths or sum(wealths) == 0:
            return 0.0  # 如果没有财富或列表为空，则完全平等

        # 排序并计算
        sorted_wealths = np.sort(wealths)
        n = len(wealths)
        cum_wealth = np.cumsum(sorted_wealths, dtype=float)
        # 洛伦兹曲线面积的计算公式
        return (n + 1 - 2 * np.sum(cum_wealth) / cum_wealth[-1]) / n

    def _log_daily_stats(self):
        self.history['day'].append(self.day)
        gdp = sum(a.daily_production for a in self.islanders)
        total_wealth = sum(a.fish_in_hand for a in self.islanders)
        capital_stock = sum(1 for a in self.islanders if a.has_net)
        population = sum(1 for a in self.islanders if a.is_active)

        # 计算并记录基尼系数
        active_wealths = [a.fish_in_hand for a in self.islanders if a.is_active]
        gini = self._calculate_gini(active_wealths)
        self.history['gini_coefficient'].append(gini)

        self.history['gdp'].append(gdp)
        self.history['total_wealth'].append(total_wealth)
        self.history['capital_stock'].append(capital_stock)
        self.history['population'].append(population)
        for agent in self.islanders:
            self.history['individual_wealth'][agent.name].append(agent.fish_in_hand)

    def simulate_one_day(self):
        self.day += 1
        for agent in self.islanders: agent.decide_and_act()
        for agent in self.islanders: agent.end_of_day_consumption()
        self._log_daily_stats()

    def update_positions(self):
        for agent in self.islanders: agent.update_position()

    def draw(self, screen):
        screen.fill(BLUE)
        pygame.draw.rect(screen, SAND, (0, HEIGHT // 3, WIDTH, HEIGHT * 2 // 3))
        for agent in self.islanders:
            pygame.draw.rect(screen, agent.color, (agent.home_pos[0] - 20, agent.home_pos[1] - 20, 40, 40), 0,
                             border_radius=5)
            name_text = SMALL_FONT.render(agent.name, True, BLACK)
            screen.blit(name_text, (agent.home_pos[0] - 15, agent.home_pos[1] + 20))
        for agent in self.islanders: agent.draw(screen)
        self.draw_hud(screen)
        self.draw_agent_status(screen)

    def draw_hud(self, screen):
        hud_surface = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        hud_surface.fill((0, 0, 0, 120))

        gdp = self.history['gdp'][-1] if self.history['gdp'] else 0
        wealth = self.history['total_wealth'][-1] if self.history['total_wealth'] else 0
        capital = self.history['capital_stock'][-1] if self.history['capital_stock'] else 0
        pop = self.history['population'][-1] if self.history['population'] else len(self.islanders)
        gini = self.history['gini_coefficient'][-1] if self.history['gini_coefficient'] else 0

        # *** 在HUD中增加基尼系数 ***
        texts = [
            f"📅 Day: {self.day}", f"🧑 Pop: {pop}", f"🐟 Wealth: {wealth}",
            f"📈 GDP: {gdp}", f"🕸️ Capital: {capital}", f"⚖️ Gini: {gini:.2f}"
        ]
        x_offset = 15
        for text in texts:
            text_surf = HUD_FONT.render(text, True, WHITE)
            hud_surface.blit(text_surf, (x_offset, 8))
            x_offset += text_surf.get_width() + 30
        screen.blit(hud_surface, (0, 0))

    def draw_agent_status(self, screen):
        y_offset = HEIGHT - 90
        for agent in self.islanders:
            # 个人状态UI改为英文
            status_text = f"{agent.name} | Savings: {agent.fish_in_hand} | Hunger: {agent.hunger}/2 | Status: {agent.action}"
            status_surface = STATUS_FONT.render(status_text, True, agent.color if agent.is_active else GREY)
            screen.blit(status_surface, (10, y_offset))
            y_offset += 25

    def plot_final_report(self):
        """模拟结束后，生成并显示综合报告图表"""
        if not self.history['day']:
            print("Not enough data to generate a report.")
            return

        fig, axs = plt.subplots(3, 2, figsize=(16, 15))
        # 图表标题改为英文
        fig.suptitle('Island Economy Comprehensive Report', fontsize=20)
        days = self.history['day']

        # *** 辅助函数：将 Pygame 的 0-255 颜色转换为 Matplotlib 的 0-1 颜色 ***
        def to_mpl_color(pygame_color):
            return tuple(c / 255.0 for c in pygame_color)

        # 图表 1: 宏观经济
        axs[0, 0].plot(days, self.history['gdp'], label='Daily GDP', color='blue', marker='.')
        axs[0, 0].plot(days, self.history['total_wealth'], label='Total Savings', color='green')
        axs[0, 0].set_title('Macroeconomic Indicators')
        axs[0, 0].set_xlabel('Day')
        axs[0, 0].set_ylabel('Number of Fish')
        axs[0, 0].legend(loc='upper left')
        axs[0, 0].grid(True)
        ax00_twin = axs[0, 0].twinx()
        ax00_twin.plot(days, self.history['capital_stock'], label='Capital Stock (Nets)', color='orange',
                       linestyle='--')
        ax00_twin.set_ylabel('Number of Nets')
        ax00_twin.legend(loc='upper right')

        # 图表 2: 个人财富轨迹 (*** 应用颜色转换 ***)
        for name, wealth_history in self.history['individual_wealth'].items():
            agent = next(a for a in self.islanders if a.name == name)
            # 在这里进行颜色转换！
            mpl_color = to_mpl_color(agent.color)
            axs[0, 1].plot(days, wealth_history, label=name, color=mpl_color)
        axs[0, 1].set_title('Individual Wealth Growth and Divergence')
        axs[0, 1].set_xlabel('Day')
        axs[0, 1].set_ylabel('Individual Savings')
        axs[0, 1].legend()
        axs[0, 1].grid(True)

        # 图表 3: 贫富差距演变
        axs[1, 0].plot(days, self.history['gini_coefficient'], label='Gini Coefficient', color='purple')
        axs[1, 0].axhline(y=0.4, color='red', linestyle='--', label='International Alert Line (0.4)')
        axs[1, 0].set_title('Evolution of Inequality')
        axs[1, 0].set_xlabel('Day')
        axs[1, 0].set_ylabel('Gini Coefficient (0=Equality, 1=Inequality)')
        axs[1, 0].set_ylim(0, 1)
        axs[1, 0].legend()
        axs[1, 0].grid(True)

        # 图表 4: 人口变化
        axs[1, 1].plot(days, self.history['population'], label='Surviving Population', color='red')
        axs[1, 1].set_title('Population Change')
        axs[1, 1].set_xlabel('Day')
        axs[1, 1].set_ylabel('Number of People')
        axs[1, 1].set_ylim(0, len(self.islanders) + 1)
        axs[1, 1].grid(True)

        # 图表 5: 空白
        axs[2, 0].set_visible(False)

        # 图表 6: 最终财富分配 (*** 应用颜色转换 ***)
        final_wealth = [data[-1] if data else 0 for data in self.history['individual_wealth'].values()]
        names = list(self.history['individual_wealth'].keys())
        # 在这里进行颜色转换！
        mpl_colors = [to_mpl_color(agent.color) for agent in self.islanders]
        axs[2, 1].bar(names, final_wealth, color=mpl_colors)
        axs[2, 1].set_title('Final Wealth Distribution')
        axs[2, 1].set_xlabel('Islander')
        axs[2, 1].set_ylabel('Final Savings')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()


# --- 4. 游戏主循环 (不变) ---
def main():
    clock = pygame.time.Clock()
    economy = IslandEconomy()
    running = True;
    DAY_LENGTH_MS = 300;
    day_timer = pygame.time.get_ticks()

    # 引入结束条件
    MAX_SIMULATION_DAYS = 200

    while running:
        # 处理用户输入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 检查自动结束条件
        if economy.day >= MAX_SIMULATION_DAYS:
            print(f"Reached max simulation days ({MAX_SIMULATION_DAYS}). Simulation ending.")
            running = False
        if not any(a.is_active for a in economy.islanders) and economy.day > 0:
            print("All islanders are out. Economic collapse. Simulation ending.")
            pygame.time.wait(2000)
            running = False

        # 更新游戏状态
        if running:
            current_time = pygame.time.get_ticks()
            if current_time - day_timer > DAY_LENGTH_MS:
                economy.simulate_one_day()
                day_timer = current_time
            # 更新窗口标题
            pygame.display.set_caption(f"Island Economy Simulator - Day: {economy.day}/{MAX_SIMULATION_DAYS}")

        # 绘制屏幕
        economy.update_positions();
        economy.draw(SCREEN);
        pygame.display.flip();
        clock.tick(60)

    # *** 关键改动：先显示图表，再退出Pygame ***
    print("Simulation ended. Generating final report...")  # 终端提示改为英文
    economy.plot_final_report()  # 步骤1：让 Matplotlib 创建并显示图表窗口

    pygame.quit()  # 步骤2：在图表显示后，再安全地关闭 Pygame


if __name__ == "__main__":
    main()