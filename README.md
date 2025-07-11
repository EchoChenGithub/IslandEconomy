# Island Economy Simulator 🏝️

A simple Agent-Based Model (ABM) inspired by the book *"How an Economy Grows and Why It Crashes"*. This simulation, built with Pygame, visualizes the economic development of a small island, from subsistence survival to capital formation, productivity growth, and the emergence of inequality.

  ![game](https://github.com/user-attachments/assets/3c6115c9-62db-4cae-994a-f7ae6465f8cd)<img width="1600" height="1500" alt="img" src="https://github.com/user-attachments/assets/42c42e29-686d-4d03-ba18-0a1803a48b80" />




## Features

- **Agent-Based Simulation**: Each islander is an independent agent with their own "personality" (risk propensity).
- **Dynamic Behavior**: Watch islanders decide between fishing and making high-risk, high-reward investments in capital (fishing nets).
- **Economic Concepts Visualized**:
  - **Capital Formation**: See the sacrifice required to build the first fishing net.
  - **Productivity Growth**: Observe how capital goods dramatically increase output.
  - **Inequality**: Track the Gini coefficient as the wealth gap widens between innovators and followers.
  - **Risk & Failure**: Investment isn't guaranteed! There's a 50% chance of failure, representing the harsh realities of innovation.
- **Real-time Data HUD**: Key economic indicators (GDP, Wealth, Capital, Gini) are displayed live.
- **Final Comprehensive Report**: After the simulation ends, a detailed report with multiple charts is generated using Matplotlib.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/IslandEconomy.git
    cd IslandEconomy
    ```

2.  **Install dependencies:**
    Make sure you have Python 3 installed. Then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the simulation:**
    ```bash
    python island_simulator.py
    ```

## Simulation Rules
- **Initial State**: 3 islanders. Each can catch 1 or 2 fish per day by hand.
- **Consumption**: Each islander must eat 1 fish per day. Failing to eat for 3 consecutive days results in being eliminated.
- **Investment (The Net)**:
  - An islander can choose to spend 2 days building a fishing net.
  - This requires a starting savings of at least 2 fish to survive the construction period.
  - The investment has a **50% chance of failure**.
- **Productivity**: A successful net allows an islander to catch a stable 3 fish per day.
- **Personalities**:
  - **Able (The Innovator)**: Has a 10% chance to attempt investment each day if conditions are met.
  - **Baker & Charlie (The Followers)**: Will never attempt to innovate on their own (risk propensity is 0).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
