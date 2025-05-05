import psutil
import time
import threading

class SystemMonitor:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.resource_data = []
        
    def start_monitoring(self):
        """Start monitoring system resources"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring system resources"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1.0)
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Store the data
            self.resource_data.append({
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent
            })
            
            # Print current usage
            print(f"CPU: {cpu_percent}% | Memory: {memory_percent}%")
            
            # Sleep for a short period
            time.sleep(2.0)
    
    def get_resource_data(self):
        """Get collected resource data"""
        return self.resource_data

def demonstrate_monitoring():
    """Demonstrate system monitoring"""
    print("Starting system resource monitoring...")
    monitor = SystemMonitor()
    monitor.start_monitoring()
    
    try:
        # Run for a short period
        time.sleep(10)
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Display collected data
        data = monitor.get_resource_data()
        print("\nCollected Resource Data:")
        for entry in data:
            timestamp = time.strftime('%H:%M:%S', time.localtime(entry['timestamp']))
            print(f"Time: {timestamp} | CPU: {entry['cpu_percent']}% | Memory: {entry['memory_percent']}%")
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
        monitor.stop_monitoring()

if __name__ == "__main__":
    demonstrate_monitoring()
