# Geopolitical-Shock Market Simulator

A high-fidelity market simulation environment that utilizes **Game Theory** and **Agent-Based Modeling** to study how geopolitical events impact financial market stability, liquidity, and price discovery.[cite: 1]

## 📊 Overview

This project simulates a complex financial ecosystem where diverse trading agents interact within a shared market state.[cite: 1] By introducing "Geopolitical Shocks," the simulator analyzes the resilience of different trading strategies and the emergence of market phenomena like margin calls, panic selling, and mean reversion.[cite: 1]

## 🤖 Agent Types

The simulator features several distinct agent profiles, each with unique decision-making logic:[cite: 1]

* **Momentum Agents**: Trade based on trend strength and price velocity.[cite: 1]
* **Value Investors**: Focus on fundamental value and mean reversion.[cite: 1]
* **Retail Agents**: Exhibit behavioral biases and are highly sensitive to market volatility.[cite: 1]
* **Institutional Agents**: Large-scale players that trigger significant liquidity shifts.[cite: 1]

## 🚀 Key Features

- **Dynamic Market State**: Real-time tracking of price, volume, and volatility.[cite: 1]
- **Geopolitical Shock Engine**: Randomized and scripted events that alter market parameters (e.g., interest rate hikes, regional conflicts).[cite: 1]
- **Margin Call Logic**: Simulation of leverage risks and forced liquidations.[cite: 1]
- **Game Theory Framework**: Agents optimize decisions based on the predicted actions of other market participants.[cite: 1]

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/varchasvaiesisyphus-hub/Geopolitical-Shock-Market-Simulator-using-Game-Theory.git](https://github.com/varchasvaiesisyphus-hub/Geopolitical-Shock-Market-Simulator-using-Game-Theory.git)
   cd Geopolitical-Shock-Market-Simulator-using-Game-Theory
   
```[cite: 1]

2. **Set up the environment:**
   ```bash
   python -m venv market_simulator_env
   # On Windows:
   .\market_simulator_env\Scripts\activate
   # On macOS/Linux:
   source market_simulator_env/bin/activate
   
```[cite: 1]

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   
```[cite: 1]

## 💻 Usage

Run the primary simulation script to generate a market run:

```bash
python main.py --duration 1000 --shock_intensity high
```[cite: 1]

The output will generate logs and visualization data reflecting price movements and agent PnL.[cite: 1]

## 📂 Project Structure

- `/agents`: Contains the logic for different trading entities.[cite: 1]
- `/simulation`: The core engine that manages time steps and agent interactions.[cite: 1]
- `market_state.py`: The global object tracking the current financial climate.[cite: 1]
- `test.py`: Suite for validating agent behavior and margin call triggers.[cite: 1]

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.[cite: 1]
