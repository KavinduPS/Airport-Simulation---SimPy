import simpy
import random
from metrics import AirportMetrics
import matplotlib.pyplot as plt

RANDOM_SEED = 42
SIM_TIME = 720
ARRIVAL_MEAN = 10

# Time distributions (minutes)
def landing_time(): return random.randint(3, 6)
def takeoff_time(): return random.randint(3, 6)
def taxi_time(): return random.randint(3, 6)

def aircraft(env, name, runway, gate, gate_min, gate_max, is_priority, metrics):
    # Record arrival time
    arrival_time = env.now
    metrics.record_arrival()

    # Arrival phase
    runway_wait_start = env.now
    # Request runway with priority (1 = lower priority for arrivals)
    if is_priority:
        request = runway.request(priority=1)
    else:
        request = runway.request()
    with request:
        if len(runway.queue) > 0:
            print(f"{env.now:.1f}: {name} waiting - runway busy with {len(runway.users)} plane(s).")
        yield request

        # Record runway wait time
        runway_wait_time = env.now - runway_wait_start
        metrics.record_runway_wait_landing(runway_wait_time)
        yield env.timeout(landing_time())

    # Taxi to gate
    yield env.timeout(taxi_time())

    # Gate phase
    # Track gate wait time
    gate_wait_start = env.now
    with gate.request() as gate_req:
        if len(gate.users) == gate.capacity:
            print(f"{env.now:.1f}: {name} waiting... - all gates full!")
        yield gate_req

        # Record gate wait time
        gate_wait_time = env.now - gate_wait_start
        metrics.record_gate_wait(gate_wait_time)

        # Turnaround service: unload passengers, refuel, load new passengers
        service_time = random.randint(gate_min, gate_max)
        yield env.timeout(service_time)

    # Departure phase
    # Taxi to runway
    yield env.timeout(taxi_time())

    # Request runway for takeoff
    # Track runway wait time for takeoff
    runway_wait_start = env.now
    # Request runway with priority (0 = higher priority for departures)
    if is_priority:
        request = runway.request(priority=0)
    else:
        request = runway.request()
    with request:
        if len(runway.queue) > 0:
            print(f"{env.now:.1f}: {name} waiting for runway.")
        yield request

        # Record runway wait time for takeoff
        runway_wait_time = env.now - runway_wait_start
        metrics.record_runway_wait_takeoff(runway_wait_time)
        yield env.timeout(takeoff_time())

    # Record departure and total system time
    departure_time = env.now
    total_time = departure_time - arrival_time
    metrics.record_total_time(total_time)
    metrics.record_departure()

def aircraft_generator(env, runway, gate, gate_min, gate_max, is_priority, metrics):
    flight_num = 1

    while True:
        # Wait for next aircraft arrival
        yield env.timeout(random.expovariate(1.0 / ARRIVAL_MEAN))
        name = f"Flight-{flight_num:03d}"
        env.process(aircraft(env, name, runway, gate, gate_min, gate_max, is_priority, metrics))
        flight_num += 1

def monitor(env, runway, gate, metrics, interval=1):
    while True:
        metrics.snapshot_queues(env.now, len(runway.queue), len(gate.queue))
        metrics.snapshot_utilization(env.now, len(runway.users), len(gate.users))
        yield env.timeout(interval)

def simulate(runways, gates, gate_min, gate_max, is_priority):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    runway = simpy.PriorityResource(env, capacity=runways) if is_priority else simpy.Resource(env, capacity=runways)
    gate = simpy.Resource(env, capacity=gates)
    metrics = AirportMetrics()

    env.process(aircraft_generator(env, runway, gate, gate_min, gate_max, is_priority, metrics))
    env.process(monitor(env, runway, gate, metrics))
    env.run(until=SIM_TIME)

    summary = metrics.get_summary(SIM_TIME)
    utilization = metrics.calculate_utilization(SIM_TIME, runways, gates)
    return {
        "label": f"{runways} Runway / {gates} Gates",
        "avg_runway_wait_landing": summary["avg_runway_wait_landing"],
        "avg_runway_wait_takeoff": summary["avg_runway_wait_takeoff"],
        "avg_gate_wait": summary["avg_gate_wait"],
        "runway_util": utilization["runway_util"],
        "gate_util": utilization["gate_util"],
        "throughput": summary["throughput_per_hour"],
    }

if __name__ == "__main__":
    scenarios = [
        (1, 8, 45, 90, False, "1 Runway / 8 Gates"),
        (2, 10, 45, 90, False, "2 Runways / 10 Gates"),
        (1, 8, 45, 90, False, "Gate time 45-90 mins (slower)"),
        (1, 8, 30, 60, False, "Gate time 30-60 mins (faster)"),
        (1, 8, 45, 90, False, "FCFS"),
        (1, 8, 45, 90, True, "Priority for Departures")
    ]

    results = [simulate(r, g, g_min, g_max, priority) for r, g, g_min, g_max, priority, _ in scenarios]

    scenario_titles = [scenarios[i * 2][5] + " vs " + scenarios[i * 2 + 1][5] for i in range(len(scenarios) // 2)]

    # Print comparison
    print("\n=== Scenario Comparison ===")
    for r in results:
        print(f"{r['label']}: RunwayWait(L)={r['avg_runway_wait_landing']:.2f}, "
              f"RunwayWait(T)={r['avg_runway_wait_takeoff']:.2f}, "
              f"RunwayUtil={r['runway_util']:.1f}%, "
              f"GateUtil={r['gate_util']:.1f}%, "
              f"GateWait={r['avg_gate_wait']:.2f}, Throughput={r['throughput']:.1f}")

    # Visualization
    for i in range(0, len(results), 2):
        labels = ['Runway Wait (Landing)', 'Runway Wait (Takeoff)', 'Gate Wait']
        basecase = [results[i]['avg_runway_wait_landing'],
                    results[i]['avg_runway_wait_takeoff'],
                    results[i]['avg_gate_wait']]
        testcase = [results[i + 1]['avg_runway_wait_landing'],
                    results[i + 1]['avg_runway_wait_takeoff'],
                    results[i + 1]['avg_gate_wait']]

        x = range(len(labels))
        width = 0.35
        plt.figure(figsize=(8, 5))
        plt.bar([j - width / 2 for j in x], basecase, width, label=scenarios[i][5], color='#1f77b4')
        plt.bar([j + width / 2 for j in x], testcase, width, label=scenarios[i + 1][5], color='#ff7f0e')
        plt.xticks(x, labels)
        plt.ylabel('Average Wait Time (min)')
        plt.title(f'Scenario {i // 2 + 1}: {scenario_titles[i // 2]}')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
