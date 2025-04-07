from bgl_log_simulator import BGLLogSimulator

# Create a simulator with default settings
simulator = BGLLogSimulator()

# Calculate total number of logs to generate
total_logs = 10 * 100  # duration_minutes * logs_per_minute

# Generate logs using generate_log_file method
logs_generated = simulator.generate_log_file("my_logs.txt", count=total_logs)

# Print a confirmation message
print(f"Simulation complete. Generated {logs_generated} logs to my_logs.txt")

# Display a few sample logs from the output file
print("\nSample logs from the generated file:")
with open("my_logs.txt", "r") as f:
    # Print the first 5 log entries
    for i in range(5):
        line = f.readline().strip()
        print(line)
