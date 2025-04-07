import random
import time
import datetime
import numpy as np
from collections import defaultdict

class BGLLogSimulator:
    def __init__(self, num_nodes=1024, num_components=10, error_rate=0.05, anomaly_probability=0.01):
        """
        Initialize the BGL log simulator
        
        Parameters:
        -----------
        num_nodes : int
            Number of nodes in the simulated cluster
        num_components : int
            Number of components per node
        error_rate : float
            Basic error rate for normal operation
        anomaly_probability : float
            Probability of an anomaly occurring
        """
        self.num_nodes = num_nodes
        self.num_components = num_components
        self.error_rate = error_rate
        self.anomaly_probability = anomaly_probability
        
        # Define severity levels and their weights
        # Modified to ensure a better mix - increased INFO probability
        self.severity_levels = {
            "INFO": 0.7,     # 70% of logs will be INFO
            "WARNING": 0.15, # 15% will be WARNING
            "ERROR": 0.1,    # 10% will be ERROR
            "FATAL": 0.05    # 5% will be FATAL
        }
        
        # Define components and their message templates
        self.components = [
            "KERNEL", "MEMORY", "NETWORK", "IO", "PROCESSOR", 
            "FILESYSTEM", "SCHEDULER", "POWER", "TEMPERATURE", "APPLICATION"
        ]
        
        # Initialize message templates per component
        self.message_templates = self._init_message_templates()
        
        # Track node failures for generating correlated events
        self.node_status = {node_id: "OPERATIONAL" for node_id in range(self.num_nodes)}
        
        # Tracking time for log sequence
        self.current_time = datetime.datetime.now()
        
        # Track sequence of ongoing anomalies
        self.active_anomalies = defaultdict(list)
    
    def _init_message_templates(self):
        """Initialize message templates for different components"""
        templates = {
            "KERNEL": [
                "Kernel panic on node {node_id}, process {pid} terminated",
                "Memory allocation failed at address 0x{address}",
                "System call {syscall} failed with error {errno}",
                "Kernel module {module} loaded successfully",
                "Process {pid} started with priority {priority}"
            ],
            "MEMORY": [
                "Memory usage at {percent}% on node {node_id}",
                "Memory leak detected in process {pid}",
                "Out of memory error, killed process {pid}",
                "Memory page fault at address 0x{address}",
                "Memory check completed: {status}"
            ],
            "NETWORK": [
                "Network interface {interface} down on node {node_id}",
                "Packet loss detected between nodes {node_id} and {target_node}",
                "Network throughput dropped to {bandwidth} MB/s",
                "TCP connection timeout on port {port}",
                "Link flapping detected on interface {interface}"
            ],
            "IO": [
                "I/O error on device {device} sector {sector}",
                "Disk {disk} full on node {node_id}",
                "Read timeout on device {device}",
                "Write error on file {filename}",
                "I/O wait time increased to {wait_time} ms"
            ],
            "PROCESSOR": [
                "CPU temperature at {temp}°C on node {node_id}",
                "CPU utilization at {percent}% on node {node_id}",
                "Processor {core} throttling due to temperature",
                "Instruction cache error on core {core}",
                "Processor completed {cycles} cycles"
            ],
            "FILESYSTEM": [
                "Filesystem {fs} mounted on node {node_id}",
                "File corruption detected at {path}",
                "Inode table overflow on {fs}",
                "Filesystem {fs} remounted read-only due to errors",
                "Journal commit failure on {fs}"
            ],
            "SCHEDULER": [
                "Job {job_id} scheduled on nodes {node_range}",
                "Job {job_id} failed with exit code {exit_code}",
                "Scheduler queue full, rejecting new jobs",
                "Resource allocation failed for job {job_id}",
                "Job {job_id} completed in {duration} seconds"
            ],
            "POWER": [
                "Power supply {psu} failed on rack {rack_id}",
                "Entering power saving mode on node {node_id}",
                "Power consumption at {watts} watts",
                "Voltage fluctuation detected on rail {rail}",
                "UPS activated due to power instability"
            ],
            "TEMPERATURE": [
                "Temperature critical at {temp}°C in rack {rack_id}",
                "Cooling fan {fan_id} failed in node {node_id}",
                "Temperature normalized at {temp}°C",
                "Thermal throttling activated on node {node_id}",
                "HVAC system error code {error_code}"
            ],
            "APPLICATION": [
                "Application {app_name} crashed with signal {signal}",
                "MPI communication timeout in job {job_id}",
                "Checkpoint created for job {job_id} at {timestamp}",
                "Application {app_name} requested {mem_amount} GB memory",
                "Performance degradation detected in job {job_id}"
            ]
        }
        
        # Add more INFO-level templates to each component to ensure a better mix
        info_templates = {
            "KERNEL": [
                "Kernel update completed successfully on node {node_id}",
                "Task scheduler optimized on node {node_id}",
                "System performance metrics collected on node {node_id}"
            ],
            "MEMORY": [
                "Memory test passed on node {node_id}",
                "Memory allocation pool optimized",
                "Swap usage at {percent}% on node {node_id}"
            ],
            "NETWORK": [
                "Network bandwidth test completed on node {node_id}: {bandwidth} MB/s",
                "Connectivity verified between node {node_id} and {target_node}",
                "Network configuration updated on node {node_id}"
            ],
            "IO": [
                "Disk performance test completed on node {node_id}",
                "I/O scheduler switched to {scheduler} on node {node_id}",
                "Device {device} read speed: {speed} MB/s"
            ],
            "PROCESSOR": [
                "CPU idle at {percent}% on node {node_id}",
                "Processor frequency scaled to {freq} GHz",
                "Core {core} running optimally on node {node_id}"
            ],
            "FILESYSTEM": [
                "Routine filesystem check passed on {fs}",
                "Quota usage at {percent}% on filesystem {fs}",
                "Filesystem {fs} defragmentation completed"
            ],
            "SCHEDULER": [
                "Queue status: {waiting} jobs waiting, {running} jobs running",
                "Scheduler load balanced across {count} nodes",
                "Resource availability updated: {cpu_free} CPUs, {mem_free} GB memory"
            ],
            "POWER": [
                "Power supply status normal on rack {rack_id}",
                "Energy efficiency optimized on node {node_id}",
                "Power consumption within normal parameters"
            ],
            "TEMPERATURE": [
                "Temperature stable at {temp}°C in rack {rack_id}",
                "Cooling system operating normally on node {node_id}",
                "HVAC maintenance completed successfully"
            ],
            "APPLICATION": [
                "Application {app_name} started successfully on node {node_id}",
                "Job {job_id} resource usage within expected parameters",
                "Application metrics collected for {app_name}"
            ]
        }
        
        # Merge the info templates with the existing templates
        for component, info_template_list in info_templates.items():
            templates[component].extend(info_template_list)
            
        return templates
    
    def _get_severity(self, component=None, node_id=None):
        """
        Determine severity level based on component, node status and randomness
        Modified to ensure a better mix of severity levels
        """
        # If node is failing, increase probability of errors
        if node_id is not None and self.node_status[node_id] != "OPERATIONAL":
            severity_weights = {
                "INFO": 0.2,
                "WARNING": 0.3,
                "ERROR": 0.4,
                "FATAL": 0.1
            }
        else:
            # Normal operation - use standard severity distribution
            severity_weights = self.severity_levels.copy()
            
            # Make random adjustment to ensure variety
            if random.random() < self.error_rate:
                # Increase error probabilities slightly
                severity_weights["WARNING"] *= 1.2
                severity_weights["ERROR"] *= 1.2
                severity_weights["FATAL"] *= 1.2
            else:
                # Increase info probability even more to ensure mix
                severity_weights["INFO"] *= 1.2
                
        # Certain components are more likely to have errors
        if component in ["MEMORY", "PROCESSOR", "POWER"]:
            severity_weights["ERROR"] *= 1.2
            severity_weights["FATAL"] *= 1.1
        
        # Components more likely to generate routine info
        if component in ["SCHEDULER", "FILESYSTEM", "NETWORK"]:
            severity_weights["INFO"] *= 1.2
            
        # Normalize weights
        total = sum(severity_weights.values())
        normalized_weights = {k: v/total for k, v in severity_weights.items()}
        
        # Select severity based on weights
        severities = list(normalized_weights.keys())
        weights = list(normalized_weights.values())
        return random.choices(severities, weights=weights)[0]
    
    def _generate_timestamp(self):
        """Generate timestamp with realistic intervals"""
        # Add a random time interval (0-5 seconds)
        interval = random.random() * 5
        self.current_time += datetime.timedelta(seconds=interval)
        return self.current_time.strftime("%Y-%m-%d-%H.%M.%S.%f")[:-3]
    
    def _format_log_entry(self, timestamp, node_id, component, severity, message):
        """Format log entry according to BGL format"""
        return f"{timestamp} {severity} {node_id:04d} {component}: {message}"
    
    def _fill_template_placeholders(self, template, node_id):
        """Fill in placeholders in message templates with realistic values"""
        message = template
        
        # Replace common placeholders
        if "{node_id}" in message:
            message = message.replace("{node_id}", f"{node_id:04d}")
            
        if "{pid}" in message:
            message = message.replace("{pid}", str(random.randint(1, 32768)))
            
        if "{address}" in message:
            message = message.replace("{address}", f"{random.randint(0, 0xFFFFFFFF):08x}")
            
        if "{percent}" in message:
            message = message.replace("{percent}", str(random.randint(1, 100)))
            
        if "{status}" in message:
            message = message.replace("{status}", random.choice(["SUCCESS", "FAILURE", "WARNING", "PARTIAL"]))
            
        if "{interface}" in message:
            message = message.replace("{interface}", f"eth{random.randint(0, 3)}")
            
        if "{target_node}" in message:
            message = message.replace("{target_node}", f"{random.randint(0, self.num_nodes-1):04d}")
            
        if "{bandwidth}" in message:
            message = message.replace("{bandwidth}", str(random.randint(10, 1000)))
            
        if "{port}" in message:
            message = message.replace("{port}", str(random.randint(1024, 65535)))
            
        if "{device}" in message:
            message = message.replace("{device}", f"/dev/sd{random.choice('abcdefgh')}")
            
        if "{disk}" in message:
            message = message.replace("{disk}", f"/dev/sd{random.choice('abcdefgh')}")
            
        if "{sector}" in message:
            message = message.replace("{sector}", str(random.randint(0, 999999)))
            
        if "{temp}" in message:
            message = message.replace("{temp}", str(random.randint(25, 85)))
            
        if "{filename}" in message:
            message = message.replace("{filename}", f"/path/to/file_{random.randint(1, 1000)}.dat")
            
        if "{wait_time}" in message:
            message = message.replace("{wait_time}", str(random.randint(5, 500)))
            
        if "{core}" in message:
            message = message.replace("{core}", str(random.randint(0, 31)))
            
        if "{cycles}" in message:
            message = message.replace("{cycles}", str(random.randint(1000000, 9999999)))
            
        if "{fs}" in message:
            message = message.replace("{fs}", random.choice(["/home", "/scratch", "/tmp", "/var", "/usr"]))
            
        if "{path}" in message:
            message = message.replace("{path}", f"/path/to/file_{random.randint(1, 1000)}.dat")
            
        if "{job_id}" in message:
            message = message.replace("{job_id}", str(random.randint(1000, 9999)))
            
        if "{exit_code}" in message:
            message = message.replace("{exit_code}", str(random.randint(1, 255)))
            
        if "{node_range}" in message:
            start = random.randint(0, self.num_nodes - 10)
            end = start + random.randint(1, 10)
            message = message.replace("{node_range}", f"{start:04d}-{end:04d}")
            
        if "{duration}" in message:
            message = message.replace("{duration}", str(random.randint(10, 86400)))
            
        if "{psu}" in message:
            message = message.replace("{psu}", f"PSU{random.randint(1, 4)}")
            
        if "{rack_id}" in message:
            message = message.replace("{rack_id}", f"R{random.randint(1, 16):02d}")
            
        if "{watts}" in message:
            message = message.replace("{watts}", str(random.randint(100, 1500)))
            
        if "{rail}" in message:
            message = message.replace("{rail}", random.choice(["3.3V", "5V", "12V"]))
            
        if "{fan_id}" in message:
            message = message.replace("{fan_id}", f"FAN{random.randint(1, 8)}")
            
        if "{error_code}" in message:
            message = message.replace("{error_code}", f"E{random.randint(1, 999):03d}")
            
        if "{app_name}" in message:
            message = message.replace("{app_name}", random.choice(["mpi_app", "linpack", "hpcg", "gromacs", "namd", "vasp"]))
            
        if "{signal}" in message:
            message = message.replace("{signal}", random.choice(["SIGSEGV", "SIGABRT", "SIGTERM", "SIGKILL"]))
            
        if "{timestamp}" in message:
            timestamp = self._generate_timestamp()
            message = message.replace("{timestamp}", timestamp)
            
        if "{mem_amount}" in message:
            message = message.replace("{mem_amount}", str(random.randint(1, 128)))
            
        if "{syscall}" in message:
            message = message.replace("{syscall}", random.choice(["read", "write", "open", "close", "fork", "exec"]))
            
        if "{errno}" in message:
            message = message.replace("{errno}", str(random.randint(1, 255)))
            
        if "{module}" in message:
            message = message.replace("{module}", random.choice(["nvidia", "infiniband", "lustre", "nfs", "rdma"]))
            
        if "{priority}" in message:
            message = message.replace("{priority}", str(random.randint(1, 99)))
            
        if "{scheduler}" in message:
            message = message.replace("{scheduler}", random.choice(["cfq", "noop", "deadline"]))
            
        if "{speed}" in message:
            message = message.replace("{speed}", str(random.randint(50, 500)))
            
        if "{freq}" in message:
            message = message.replace("{freq}", f"{random.uniform(2.0, 4.0):.2f}")
            
        if "{waiting}" in message:
            message = message.replace("{waiting}", str(random.randint(0, 100)))
            
        if "{running}" in message:
            message = message.replace("{running}", str(random.randint(10, 500)))
            
        if "{count}" in message:
            message = message.replace("{count}", str(random.randint(2, 64)))
            
        if "{cpu_free}" in message:
            message = message.replace("{cpu_free}", str(random.randint(10, 1000)))
            
        if "{mem_free}" in message:
            message = message.replace("{mem_free}", str(random.randint(100, 10000)))
            
        return message
    
    def _create_anomaly(self):
        """Create a cluster anomaly that will generate correlated events"""
        anomaly_type = random.choice([
            "network_partition",
            "rack_power_failure",
            "filesystem_corruption",
            "memory_errors",
            "overheating"
        ])
        
        affected_nodes = []
        messages = []
        
        if anomaly_type == "network_partition":
            # Network partition affects a range of nodes
            start_node = random.randint(0, self.num_nodes - 100)
            affected_count = random.randint(10, 100)
            affected_nodes = list(range(start_node, start_node + affected_count))
            
            # Generate initial events
            for node_id in affected_nodes:
                self.node_status[node_id] = "NETWORK_DEGRADED"
                component = "NETWORK"
                severity = "ERROR"
                template = "Network connectivity lost on node {node_id}, isolating from cluster"
                message = self._fill_template_placeholders(template, node_id)
                timestamp = self._generate_timestamp()
                log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                messages.append(log_entry)
            
            # Schedule follow-up events for later
            self.active_anomalies["network_partition"].extend(affected_nodes)
            
        elif anomaly_type == "rack_power_failure":
            # Power failure affects nodes in the same rack (assume 32 nodes per rack)
            rack_id = random.randint(0, self.num_nodes // 32 - 1)
            start_node = rack_id * 32
            affected_nodes = list(range(start_node, start_node + 32))
            
            # Generate initial events
            severity = "FATAL"
            component = "POWER"
            template = "Power supply failure on rack {rack_id}, nodes shutting down"
            message = template.replace("{rack_id}", f"R{rack_id:02d}")
            timestamp = self._generate_timestamp()
            
            # Master event
            log_entry = self._format_log_entry(timestamp, affected_nodes[0], component, severity, message)
            messages.append(log_entry)
            
            # Node shutdown events
            for node_id in affected_nodes:
                self.node_status[node_id] = "POWERED_OFF"
                template = "Node {node_id} shutting down due to power failure"
                message = self._fill_template_placeholders(template, node_id)
                timestamp = self._generate_timestamp()
                log_entry = self._format_log_entry(timestamp, node_id, component, "ERROR", message)
                messages.append(log_entry)
            
            # Schedule follow-up events
            self.active_anomalies["rack_power_failure"].extend(affected_nodes)
            
        elif anomaly_type == "filesystem_corruption":
            # Filesystem corruption affects random nodes
            affected_count = random.randint(5, 20)
            affected_nodes = random.sample(range(self.num_nodes), affected_count)
            fs_name = random.choice(["/home", "/scratch", "/tmp"])
            
            # Generate initial events
            severity = "ERROR"
            component = "FILESYSTEM"
            
            for node_id in affected_nodes:
                self.node_status[node_id] = "FILESYSTEM_ERROR"
                template = f"Filesystem {fs_name} corruption detected on node {{node_id}}, remounting read-only"
                message = self._fill_template_placeholders(template, node_id)
                timestamp = self._generate_timestamp()
                log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                messages.append(log_entry)
            
            # Schedule follow-up events
            self.active_anomalies["filesystem_corruption"].extend(affected_nodes)
            
        elif anomaly_type == "memory_errors":
            # Memory errors on a single node
            node_id = random.randint(0, self.num_nodes - 1)
            affected_nodes = [node_id]
            self.node_status[node_id] = "MEMORY_ERROR"
            
            # Generate cascade of memory errors
            error_count = random.randint(3, 10)
            component = "MEMORY"
            
            for i in range(error_count):
                if i < 2:
                    severity = "WARNING"
                    template = "Memory ECC error detected at address 0x{address} on node {node_id}"
                elif i < error_count - 1:
                    severity = "ERROR"
                    template = "Multiple memory errors detected on node {node_id}, DIMM {dimm_id} failing"
                    template = template.replace("{dimm_id}", f"DIMM{random.randint(0, 7)}")
                else:
                    severity = "FATAL"
                    template = "Uncorrectable memory errors on node {node_id}, taking node offline"
                
                message = self._fill_template_placeholders(template, node_id)
                timestamp = self._generate_timestamp()
                log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                messages.append(log_entry)
            
            # Schedule follow-up events
            self.active_anomalies["memory_errors"].append(node_id)
            
        elif anomaly_type == "overheating":
            # Overheating affects a range of nodes (e.g., in the same rack)
            start_node = random.randint(0, self.num_nodes - 32)
            affected_count = random.randint(5, 32)
            affected_nodes = list(range(start_node, start_node + affected_count))
            
            # Initial temperature warning
            component = "TEMPERATURE"
            
            for node_id in affected_nodes:
                self.node_status[node_id] = "OVERHEATING"
                temp = random.randint(75, 95)  # Critical temperature
                
                if temp > 90:
                    severity = "FATAL"
                    template = "CRITICAL: Temperature at {temp}°C on node {node_id}, emergency shutdown initiated"
                elif temp > 85:
                    severity = "ERROR"
                    template = "Temperature threshold exceeded at {temp}°C on node {node_id}, throttling enabled"
                else:
                    severity = "WARNING"
                    template = "High temperature warning at {temp}°C on node {node_id}"
                
                template = template.replace("{temp}", str(temp))
                message = self._fill_template_placeholders(template, node_id)
                timestamp = self._generate_timestamp()
                log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                messages.append(log_entry)
            
            # Schedule follow-up events
            self.active_anomalies["overheating"].extend(affected_nodes)
        
        return messages, affected_nodes
    
    def _continue_anomaly(self):
        """Generate follow-up logs for ongoing anomalies"""
        if not self.active_anomalies:
            return []
        
        messages = []
        # Filter out empty anomaly lists first
        active_anomalies = {k: v for k, v in self.active_anomalies.items() if v}
        
        if not active_anomalies:
            return []
            
        anomaly_type = random.choice(list(active_anomalies.keys()))
        affected_nodes = active_anomalies[anomaly_type]
        
        # 10% chance to resolve the anomaly
        if random.random() < 0.1:
            if anomaly_type == "network_partition":
                component = "NETWORK"
                template = "Network connectivity restored on node {node_id}"
                severity = "INFO"
                
                for node_id in affected_nodes:
                    self.node_status[node_id] = "OPERATIONAL"
                    message = self._fill_template_placeholders(template, node_id)
                    timestamp = self._generate_timestamp()
                    log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                    messages.append(log_entry)
                
                # Clear this anomaly
                self.active_anomalies[anomaly_type] = []
                
            elif anomaly_type == "rack_power_failure":
                component = "POWER"
                template = "Power restored to rack, initiating node startup sequence"
                severity = "INFO"
                
                # Master message
                node_id = affected_nodes[0]
                rack_id = node_id // 32
                message = template.replace("{rack_id}", f"R{rack_id:02d}")
                timestamp = self._generate_timestamp()
                log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                messages.append(log_entry)
                
                # Node recovery messages
                for node_id in affected_nodes:
                    self.node_status[node_id] = "OPERATIONAL"
                    template = "Node {node_id} power on self-test completed successfully"
                    message = self._fill_template_placeholders(template, node_id)
                    timestamp = self._generate_timestamp()
                    log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                    messages.append(log_entry)
                
                # Clear this anomaly
                self.active_anomalies[anomaly_type] = []
                
            elif anomaly_type == "filesystem_corruption":
                component = "FILESYSTEM"
                severity = "INFO"
                
                for node_id in affected_nodes:
                    self.node_status[node_id] = "OPERATIONAL"
                    template = "Filesystem check completed successfully on node {node_id}, remounting read-write"
                    message = self._fill_template_placeholders(template, node_id)
                    timestamp = self._generate_timestamp()
                    log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                    messages.append(log_entry)
                
                # Clear this anomaly
                self.active_anomalies[anomaly_type] = []
                
            elif anomaly_type == "memory_errors":
                node_id = affected_nodes[0]
                component = "MEMORY"
                severity = "INFO"
                template = "Memory diagnostics completed on node {node_id}, DIMM replaced, node back online"
                
                self.node_status[node_id] = "OPERATIONAL"
                message = self._fill_template_placeholders(template, node_id)
                timestamp = self._generate_timestamp()
                log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                messages.append(log_entry)
                
                # Clear this anomaly
                self.active_anomalies[anomaly_type] = []
                
            elif anomaly_type == "overheating":
                component = "TEMPERATURE"
                severity = "INFO"
                
                for node_id in affected_nodes:
                    self.node_status[node_id] = "OPERATIONAL"
                    template = "Temperature normalized at {temp}°C on node {node_id}, resuming normal operation"
                    template = template.replace("{temp}", str(random.randint(45, 65)))
                    message = self._fill_template_placeholders(template, node_id)
                    timestamp = self._generate_timestamp()
                    log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                    messages.append(log_entry)
                
                # Clear this anomaly
                self.active_anomalies[anomaly_type] = []
        
        # Otherwise continue the anomaly
        else:
            # Select a random node from those affected
            if self.active_anomalies[anomaly_type]:
                node_id = random.choice(self.active_anomalies[anomaly_type])
                
                if anomaly_type == "network_partition":
                    component = "NETWORK"
                    severity = "ERROR"
                    template = random.choice([
                        "Failed to reestablish network connectivity on node {node_id}",
                        "Packet loss at {percent}% on node {node_id}, network degraded",
                        "Retry {attempt} to reconnect node {node_id} failed"
                    ])
                    template = template.replace("{attempt}", str(random.randint(1, 5)))
                    
                elif anomaly_type == "rack_power_failure":
                    component = "POWER"
                    severity = "ERROR"
                    template = random.choice([
                        "Power supply {psu} still offline on rack {rack_id}",
                        "UPS battery at {percent}%, critical level",
                        "Power restoration delayed, ETA {minutes} minutes"
                    ])
                    template = template.replace("{minutes}", str(random.randint(5, 30)))
                    rack_id = node_id // 32
                    template = template.replace("{rack_id}", f"R{rack_id:02d}")
                    
                elif anomaly_type == "filesystem_corruption":
                    component = "FILESYSTEM"
                    severity = "ERROR"
                    template = random.choice([
                        "Filesystem check found {count} corrupted inodes on node {node_id}",
                        "Repair attempt {attempt} failed on node {node_id}",
                        "I/O errors continue on device {device} on node {node_id}"
                    ])
                    template = template.replace("{count}", str(random.randint(10, 1000)))
                    template = template.replace("{attempt}", str(random.randint(1, 3)))
                    
                elif anomaly_type == "memory_errors":
                    component = "MEMORY"
                    severity = "ERROR"
                    template = random.choice([
                        "Memory errors continue on node {node_id}, address range 0x{address}",
                        "DIMM {dimm_id} scheduled for replacement on node {node_id}",
                        "Uncorrectable memory error at 0x{address} on node {node_id}"
                    ])
                    template = template.replace("{dimm_id}", f"DIMM{random.randint(0, 7)}")
                    
                elif anomaly_type == "overheating":
                    component = "TEMPERATURE"
                    severity = "ERROR"
                    temp = random.randint(75, 95)
                    template = random.choicetemplate = random.choice([
                        f"Temperature still critical at {temp}°C on node {{node_id}}",
                        f"Cooling system failure persists on node {{node_id}}, temp {temp}°C",
                        f"Unable to reduce temperature below {temp}°C on node {{node_id}}"
                    ])
                
                message = self._fill_template_placeholders(template, node_id)
                timestamp = self._generate_timestamp()
                log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
                messages.append(log_entry)
        
        return messages
    
    def generate_logs(self, count=100):
        """Generate a batch of log entries"""
        logs = []
        
        for _ in range(count):
            # Check if we should trigger an anomaly
            if random.random() < self.anomaly_probability and not any(self.active_anomalies.values()):
                anomaly_logs, _ = self._create_anomaly()
                logs.extend(anomaly_logs)
                continue
                
            # Check if we should continue an existing anomaly
            if any(self.active_anomalies.values()) and random.random() < 0.3:
                anomaly_logs = self._continue_anomaly()
                logs.extend(anomaly_logs)
                continue
            
            # Generate a normal log
            node_id = random.randint(0, self.num_nodes - 1)
            component = random.choice(self.components)
            severity = self._get_severity(component, node_id)
            
            # Select a message template appropriate for the severity
            templates = self.message_templates[component]
            template = random.choice(templates)
            
            # Fill in placeholders
            message = self._fill_template_placeholders(template, node_id)
            
            # Generate timestamp
            timestamp = self._generate_timestamp()
            
            # Format the log entry
            log_entry = self._format_log_entry(timestamp, node_id, component, severity, message)
            logs.append(log_entry)
        
        return logs
    
    def generate_log_file(self, filepath, count=1000):
        """Generate log file with specified number of entries"""
        logs = self.generate_logs(count)
        
        with open(filepath, 'w') as f:
            for log in logs:
                f.write(log + "\n")
        
        return len(logs)


if __name__ == "__main__":
    # Example usage
    simulator = BGLLogSimulator(num_nodes=1024, num_components=10, error_rate=0.05, anomaly_probability=0.02)
    
    # Generate 1000 log entries to a file
    log_count = simulator.generate_log_file("simulated_bgl_logs.txt", count=1000)
    print(f"Generated {log_count} log entries to simulated_bgl_logs.txt")
    
    # Generate 5 log entries and print them
    sample_logs = simulator.generate_logs(count=5)
    print("\nSample log entries:")
    for log in sample_logs:
        print(log)
