import pygame
import random

# --- 1. 游戏化窗口设置 (不变) ---
BLUE, SAND, GREEN, RED, PURPLE, BLACK, WHITE, NET_COLOR, GREY = (135, 206, 250), (244, 164, 96), (34, 139, 34), (
220, 20, 60), (128, 0, 128), (0, 0, 0), (255, 255, 255), (112, 128, 144), (169, 169, 169)
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("小岛经济学模拟器 (V6 - 随机产出)")
pygame.font.init()
FONT = pygame.font.SysFont("SimHei", 24)
SMALL_FONT = pygame.font.SysFont("SimHei", 16)
STATUS_FONT = pygame.font.SysFont("SimHei", 18)


# --- 2. 带有新初始设定的 Agent 模型 ---
class Islander:
    def __init__(self, name, color, home_pos, risk_propensity):
        self.name = name
        self.color = color
        self.home_pos = home_pos
        self.risk_propensity = risk_propensity

        self.fish_in_hand = 0
        self.has_net = False
        self.hunger = 0
        self.is_active = True

        self.is_investing = False
        self.days_spent_investing = 0
        self.investment_duration = 2

        self.action = 'idle'
        self.pos = list(home_pos)
        self.target_pos = list(home_pos)
        self.speed = 2

    # (draw 和 update_position 方法不变)
    def update_position(self):
        if not self.is_active: return
        dx, dy = self.target_pos[0] - self.pos[0], self.target_pos[1] - self.pos[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < self.speed:
            self.pos = list(self.target_pos)
        else:
            self.pos[0] += (dx / dist) * self.speed
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

    # *** 核心逻辑变更 ***
    def decide_and_act(self):
        if not self.is_active:
            self.action = 'out'
            return

        # 1. 投资进程 (逻辑不变)
        if self.is_investing:
            self.action = 'investing'
            self.target_pos = self.home_pos
            self.days_spent_investing += 1
            if self.days_spent_investing >= self.investment_duration:
                self.is_investing = False
                self.days_spent_investing = 0
                if random.random() < 0.5:
                    self.has_net = True
                    print(f"🎉🎉🎉 {self.name} 成功造出了渔网！")
                else:
                    print(f"😭😭😭 {self.name} 的投资失败了...")
            return

        # 2. 决策：投资还是捕鱼 (逻辑不变)
        can_afford_investment = self.fish_in_hand >= self.investment_duration
        if not self.has_net and can_afford_investment:
            if random.random() < self.risk_propensity:
                self.is_investing = True
                self.days_spent_investing = 0
                self.decide_and_act()
                return

        # 3. 默认行动：捕鱼 (***产出逻辑变更***)
        self.action = 'fishing'
        self.target_pos = [random.randint(50, WIDTH - 50), 50]

        if self.has_net:
            fish_caught = 3  # 有网后，产出稳定且更高
        else:
            fish_caught = random.choice([1, 2])  # 徒手捕鱼，产出随机

        self.fish_in_hand += fish_caught

    def end_of_day_consumption(self):
        # (此方法完全不变)
        if not self.is_active: return
        if self.fish_in_hand > 0:
            self.fish_in_hand -= 1
            self.hunger = 0
        else:
            self.hunger += 1
        if self.hunger >= 3:
            self.is_active = False
            self.action = 'out'
            print(f"!!! {self.name} 因为连续饥饿3天而出局了 !!!")


class IslandEconomy:
    def __init__(self):
        self.islanders = [
            Islander("Able", GREEN, (WIDTH // 4, HEIGHT // 2), risk_propensity=0.1),
            Islander("Baker", RED, (WIDTH // 2, HEIGHT // 2), risk_propensity=0.0),
            Islander("Charlie", PURPLE, (WIDTH * 3 // 4, HEIGHT // 2), risk_propensity=0.0),
        ]
        self.day = 0

    # (其余 IslandEconomy 方法和 main 循环完全不变)
    def simulate_one_day(self):
        self.day += 1
        print(f"\n--- 第 {self.day} 天 ---")
        for agent in self.islanders:
            agent.decide_and_act()
        for agent in self.islanders:
            agent.end_of_day_consumption()

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

        day_text = FONT.render(f"第 {self.day} 天", True, BLACK)
        screen.blit(day_text, (10, HEIGHT - 40))
        y_offset = 10
        for agent in self.islanders:
            hunger_text = f"饥饿: {agent.hunger}/2"
            text_color = agent.color if agent.is_active else GREY
            if agent.hunger >= 2:
                hunger_text_color = RED
            else:
                hunger_text_color = BLACK

            status_text = f"{agent.name} | 储蓄: {agent.fish_in_hand} | 状态: {agent.action}"
            status_surface = STATUS_FONT.render(status_text, True, text_color)
            hunger_surface = STATUS_FONT.render(hunger_text, True, hunger_text_color)

            screen.blit(status_surface, (10, y_offset))
            screen.blit(hunger_surface, (350, y_offset))
            y_offset += 25


# --- 3. 游戏主循环 (不变) ---
def main():
    clock = pygame.time.Clock()
    economy = IslandEconomy()
    running = True
    DAY_LENGTH_MS = 500
    day_timer = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        current_time = pygame.time.get_ticks()
        if current_time - day_timer > DAY_LENGTH_MS:
            if any(agent.is_active for agent in economy.islanders):
                economy.simulate_one_day()
            day_timer = current_time

        economy.update_positions()
        economy.draw(SCREEN)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()