class AirportMetrics:

    def __init__(self):
        # Wait times
        self.runway_wait_times_landing = []  # Time waiting for runway to land
        self.runway_wait_times_takeoff = []  # Time waiting for runway to takeoff
        self.gate_wait_times = []  # Time waiting for gate

        # Total times (for each aircraft)
        self.total_system_times = []  # Total time from arrival to departure

        # Queue lengths over time (snapshots)
        self.runway_queue_snapshots = []  # [(time, queue_length), ...]
        self.gate_queue_snapshots = []  # [(time, queue_length), ...]

        # Resource utilization tracking
        self.runway_utilization_snapshots = []  # [(time, in_use), ...]
        self.gate_utilization_snapshots = []  # [(time, in_use), ...]

        # Counters
        self.total_aircraft_arrived = 0
        self.total_aircraft_departed = 0

    def record_runway_wait_landing(self, wait_time):
        self.runway_wait_times_landing.append(wait_time)

    def record_runway_wait_takeoff(self, wait_time):
        self.runway_wait_times_takeoff.append(wait_time)

    def record_gate_wait(self, wait_time):
        self.gate_wait_times.append(wait_time)

    def record_total_time(self, total_time):
        self.total_system_times.append(total_time)

    def record_arrival(self):
        self.total_aircraft_arrived += 1

    def record_departure(self):
        self.total_aircraft_departed += 1

    def snapshot_queues(self, time, runway_queue, gate_queue):
        """Record current queue lengths"""
        self.runway_queue_snapshots.append((time, runway_queue))
        self.gate_queue_snapshots.append((time, gate_queue))

    def snapshot_utilization(self, time, runway_in_use, gates_in_use):
        """Record current resource utilization"""
        self.runway_utilization_snapshots.append((time, runway_in_use))
        self.gate_utilization_snapshots.append((time, gates_in_use))

    def calculate_utilization(self, sim_time, num_runways, num_gates):
        """Calculate resource utilization percentages"""
        if not self.runway_utilization_snapshots:
            return {'runway_util': 0, 'gate_util': 0}

        # Calculate runway utilization
        total_runway_time = sum(u for _, u in self.runway_utilization_snapshots)
        runway_utilization = (total_runway_time / len(self.runway_utilization_snapshots)) / num_runways * 100

        # Calculate gate utilization
        total_gate_time = sum(u for _, u in self.gate_utilization_snapshots)
        gate_utilization = (total_gate_time / len(self.gate_utilization_snapshots)) / num_gates * 100

        return {
            'runway_util': runway_utilization,
            'gate_util': gate_utilization
        }

    def get_summary(self, sim_time):
        """Return summary statistics"""
        summary = {
            'total_arrived': self.total_aircraft_arrived,
            'total_departed': self.total_aircraft_departed,
            'avg_runway_wait_landing': sum(self.runway_wait_times_landing) / len(
                self.runway_wait_times_landing) if self.runway_wait_times_landing else 0,
            'avg_runway_wait_takeoff': sum(self.runway_wait_times_takeoff) / len(
                self.runway_wait_times_takeoff) if self.runway_wait_times_takeoff else 0,
            'avg_gate_wait': sum(self.gate_wait_times) / len(self.gate_wait_times) if self.gate_wait_times else 0,
            'avg_total_time': sum(self.total_system_times) / len(
                self.total_system_times) if self.total_system_times else 0,
            'max_runway_wait_landing': max(self.runway_wait_times_landing) if self.runway_wait_times_landing else 0,
            'max_runway_wait_takeoff': max(self.runway_wait_times_takeoff) if self.runway_wait_times_takeoff else 0,
            'max_gate_wait': max(self.gate_wait_times) if self.gate_wait_times else 0,
            'throughput_per_hour': (self.total_aircraft_departed / sim_time) * 60 if sim_time > 0 else 0,
        }
        return summary

    # def print_summary(self, sim_time, num_runways, num_gates):
    #     """Print formatted summary statistics"""
    #     print("\n" + "=" * 70)
    #     print("SIMULATION SUMMARY")
    #     print("=" * 70)
    #     summary = self.get_summary(sim_time)
    #     print(f"Total aircraft arrived: {summary['total_arrived']}")
    #     print(f"Total aircraft departed: {summary['total_departed']}")
    #     print(f"\nWait Times:")
    #     print(f"  Avg runway wait (landing): {summary['avg_runway_wait_landing']:.2f} min")
    #     print(f"  Avg runway wait (takeoff): {summary['avg_runway_wait_takeoff']:.2f} min")
    #     print(f"  Avg gate wait: {summary['avg_gate_wait']:.2f} min")
    #     utilization = self.calculate_utilization(sim_time, num_runways, num_gates)
    #     print(f"\nResource Utilization:")
    #     print(f"  Runway utilization: {utilization['runway_util']:.1f}%")
    #     print(f"  Gate utilization: {utilization['gate_util']:.1f}%")
    #     print(f"\nThroughput:")
    #     print(f"  Aircraft per hour: {summary['throughput_per_hour']:.1f}")
    #     print(f"\nWorst Case:")
    #     print(f"  Max runway wait (landing): {summary['max_runway_wait_landing']:.2f} min")
    #     print(f"  Max runway wait (takeoff): {summary['max_runway_wait_takeoff']:.2f} min")
    #     print(f"  Max gate wait: {summary['max_gate_wait']:.2f} min")
    #     print(f"\nSystem Performance:")
    #     print(f"  Avg total time in system: {summary['avg_total_time']:.2f} min")
    #     print("=" * 70)