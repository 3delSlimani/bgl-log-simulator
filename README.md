# BGL Log Simulator

A Python-based simulator for generating Blue Gene/L (BGL) supercomputer log entries. This tool generates realistic system logs, including various types of events, anomalies, and error conditions. It is useful for testing log analysis systems, anomaly detection algorithms, and monitoring tools.

---

## Features

- **Realistic Log Generation**: Simulates logs for multiple system components (e.g., Kernel, Memory, Network, etc.).
- **Anomaly Simulation**: Generates anomalies such as network partitions, rack power failures, filesystem corruption, memory errors, and overheating.
- **Configurable Parameters**: Allows customization of cluster size, error rates, and anomaly probabilities.
- **Severity Levels**: Supports different severity levels (INFO, WARNING, ERROR, FATAL).
- **Time-Sequenced Logs**: Generates logs with realistic timestamps and intervals.
- **Log Output**: Outputs logs to a file or in-memory for further processing.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/3delSlimani/bgl-log-simulator.git
   cd bgl-log-simulator
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv myenv
   source myenv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Example Script
```python
from bgl_log_simulator import BGLLogSimulator

# Create a simulator instance
simulator = BGLLogSimulator(
    num_nodes=1024,          # Number of nodes in the cluster
    num_components=10,       # Number of components per node
    error_rate=0.05,         # Basic error rate
    anomaly_probability=0.01 # Probability of anomaly occurrence
)

# Generate logs to a file
simulator.generate_log_file("my_logs.txt", count=1000)

# Generate logs in memory
logs = simulator.generate_logs(count=5)
for log in logs:
    print(log)
```

### Running the Simulator
To run the simulator and generate logs:
```bash
python run_simulator.py
```

---

## Configuration

You can configure the simulator with the following parameters:

- **`num_nodes`**: Number of nodes in the simulated cluster (default: 1024).
- **`num_components`**: Number of components per node (default: 10).
- **`error_rate`**: Basic error rate for normal operation (default: 0.05).
- **`anomaly_probability`**: Probability of an anomaly occurring (default: 0.01).

---

## Sample Output

### Log File
Example of a generated log file (`my_logs.txt`):
```
2025-04-07-14.23.45.123 INFO 0042 SCHEDULER: Job 1234 scheduled on nodes 0042-0048
2025-04-07-14.23.46.234 WARNING 0123 MEMORY: Memory usage at 92% on node 0123
2025-04-07-14.23.47.345 ERROR 0234 NETWORK: Network connectivity lost on node 0234
```

### Console Output
Example of logs printed to the console:
```
2025-04-07-14.23.45.123 INFO 0042 SCHEDULER: Job 1234 scheduled on nodes 0042-0048
2025-04-07-14.23.46.234 WARNING 0123 MEMORY: Memory usage at 92% on node 0123
2025-04-07-14.23.47.345 ERROR 0234 NETWORK: Network connectivity lost on node 0234
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

---

## Author

Created by **3delSlimani**.
