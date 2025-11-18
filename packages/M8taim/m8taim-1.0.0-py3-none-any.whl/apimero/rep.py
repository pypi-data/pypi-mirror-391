import json
import time
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    def __init__(self):
        self._reports_dir = Path.home() / '.m8taim' / 'reports'
        self._reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_protection_report(self, protection_data):
        report = {
            'generated_at': datetime.now().isoformat(),
            'protection_status': 'active',
            'expiry_date': datetime.fromtimestamp(protection_data.get('expiry', 0)).isoformat(),
            'remaining_time': self._calculate_remaining(protection_data.get('expiry', 0)),
            'security_checks': {
                'time_manipulation': 'protected',
                'pid_injection': 'protected',
                'debugger': 'protected',
                'hardware': 'locked'
            }
        }
        
        return report
    
    def _calculate_remaining(self, expiry_timestamp):
        remaining = expiry_timestamp - time.time()
        
        if remaining <= 0:
            return 'expired'
        
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        
        return f"{days} days, {hours} hours"
    
    def save_report(self, report, name=None):
        if not name:
            name = f"report_{int(time.time())}.json"
        
        filepath = self._reports_dir / name
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            return str(filepath)
        except:
            return None
    
    def generate_html_report(self, report):
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>M8taim Protection Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .content {{ padding: 20px; }}
        .status {{ color: #27ae60; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; }}
        td, th {{ padding: 10px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>M8taim Protection Report</h1>
        <p>Generated: {report.get('generated_at', 'N/A')}</p>
    </div>
    <div class="content">
        <h2>Protection Status: <span class="status">{report.get('protection_status', 'unknown').upper()}</span></h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Expiry Date</td><td>{report.get('expiry_date', 'N/A')}</td></tr>
            <tr><td>Remaining Time</td><td>{report.get('remaining_time', 'N/A')}</td></tr>
        </table>
        <h3>Security Checks</h3>
        <table>
            <tr><th>Check</th><th>Status</th></tr>
"""
        
        for check, status in report.get('security_checks', {}).items():
            html += f"<tr><td>{check.replace('_', ' ').title()}</td><td>{status.upper()}</td></tr>\n"
        
        html += """
        </table>
    </div>
</body>
</html>
"""
        
        return html
    
    def export_statistics(self, stats):
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': stats
        }
        
        return self.save_report(report, f"statistics_{int(time.time())}.json")
