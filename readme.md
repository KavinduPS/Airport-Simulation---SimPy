# Airport Simulation with SimPy

This project simulates an airport operation using **SimPy**, focusing on runway and gate utilization, wait times, and throughput under different scenarios.

## Features

- Models aircraft arrival, landing, taxiing, gate service, and takeoff.
- Supports priority scheduling for departures.
- Collects metrics:
  - Average runway and gate wait times
  - Runway and gate utilization
  - Throughput (aircraft per hour)
- Visualizes wait times using bar charts for scenario comparisons.

## Requirements

- Python 3.8+
- Libraries:
  ```bash
  pip install simpy matplotlib
  ```

## Usage

1. **Run the simulation**:

   ```bash
   python airport_sim.py
   ```

   This will:

   - Simulate multiple scenarios (resource changes, service time changes, priority strategies)
   - Print a summary of average waits, utilization, throughput.
   - Show bar charts comparing different scenarios

2. **Modify scenarios**:

   In airport\_sim.py, edit the `scenarios` list:

   ```python
   scenarios = [
       (1, 8, 45, 90, False, "1 Runway / 8 Gates"),
       (2, 10, 45, 90, False, "2 Runways / 10 Gates"),
       (1, 8, 45, 90, False, "Gate time 45-90 mins (slower)"),
       (1, 8, 30, 60, False, "Gate time 30-60 mins (faster)"),
       (1, 8, 45, 90, False, "FCFS"),
       (1, 8, 45, 90, True, "Priority for Departures")
   ]
   ```

   - Format: `(num_runways, num_gates, gate_min, gate_max, is_priority)`

3. **Understand outputs**:

   - **Console Summary**: Average wait times, resource utilization and throughput for each scenario.
   - **Bar Charts**: Comparison of landing wait, takeoff wait, and gate wait for each pair of scenarios.

4. **Metrics Module**:

   - `metrics.py` contains the `AirportMetrics` class that tracks queues, waits, and utilization.

## Example Output

```
=== Scenario Comparison ===
1 Runway / 8 Gates: RunwayWait(L)=15.56, RunwayWait(T)=15.97, RunwayUtil=88.5%, GateUtil=85.9%, GateWait=7.42, Throughput=5
...
```

**Visualization**: Bar charts showing scenario comparisons for wait times.

[](Scenario%201.png)![Scenario 1.png](Scenario%201.png)
