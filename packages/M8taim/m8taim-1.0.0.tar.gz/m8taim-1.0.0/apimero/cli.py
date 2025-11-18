import argparse
import sys
from datetime import datetime
from .core import M8taim

class CLIManager:
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description='M8taim - Ultimate Time-Based Protection System',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        protect_parser = subparsers.add_parser('protect', help='Protect a script')
        protect_parser.add_argument('script', help='Script to protect')
        protect_parser.add_argument('--year', type=int, help='Expiry year')
        protect_parser.add_argument('--month', type=int, help='Expiry month or relative months')
        protect_parser.add_argument('--day', type=int, help='Expiry day or relative days')
        protect_parser.add_argument('--hour', type=int, help='Expiry hour or relative hours')
        protect_parser.add_argument('--message', help='Custom expiry message')
        protect_parser.add_argument('--output', help='Output file path')
        
        check_parser = subparsers.add_parser('check', help='Check protection status')
        check_parser.add_argument('script', help='Script to check')
        
        remove_parser = subparsers.add_parser('remove', help='Remove protection')
        remove_parser.add_argument('script', help='Script to remove protection from')
        
        info_parser = subparsers.add_parser('info', help='Show M8taim information')
        
        return parser
    
    def run(self, args=None):
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return 0
        
        if args.command == 'protect':
            return self._protect_script(args)
        elif args.command == 'check':
            return self._check_script(args)
        elif args.command == 'remove':
            return self._remove_protection(args)
        elif args.command == 'info':
            return self._show_info()
        
        return 1
    
    def _protect_script(self, args):
        try:
            with open(args.script, 'r') as f:
                original_code = f.read()
        except FileNotFoundError:
            print(f"Error: Script '{args.script}' not found")
            return 1
        
        protection_code = "from apimero import M8taim\n"
        protection_code += f"M8taim("
        
        params = []
        if args.year:
            params.append(f"year={args.year}")
        if args.month:
            params.append(f"month={args.month}")
        if args.day:
            params.append(f"day={args.day}")
        if args.hour:
            params.append(f"hour={args.hour}")
        if args.message:
            params.append(f'message="{args.message}"')
        
        protection_code += ", ".join(params) + ")\n\n"
        
        protected_code = protection_code + original_code
        
        output_file = args.output or args.script
        
        try:
            with open(output_file, 'w') as f:
                f.write(protected_code)
            
            print(f"Successfully protected: {output_file}")
            return 0
        except Exception as e:
            print(f"Error protecting script: {e}")
            return 1
    
    def _check_script(self, args):
        try:
            with open(args.script, 'r') as f:
                code = f.read()
            
            if 'M8taim' in code and 'from apimero import M8taim' in code:
                print(f"✓ Script is protected with M8taim")
                return 0
            else:
                print(f"✗ Script is NOT protected")
                return 1
        except FileNotFoundError:
            print(f"Error: Script '{args.script}' not found")
            return 1
    
    def _remove_protection(self, args):
        try:
            with open(args.script, 'r') as f:
                lines = f.readlines()
            
            filtered_lines = []
            skip_next = False
            
            for line in lines:
                if 'from apimero import M8taim' in line:
                    continue
                if 'M8taim(' in line:
                    skip_next = True
                    continue
                if skip_next and line.strip() == '':
                    skip_next = False
                    continue
                
                filtered_lines.append(line)
            
            with open(args.script, 'w') as f:
                f.writelines(filtered_lines)
            
            print(f"Successfully removed protection from: {args.script}")
            return 0
        except Exception as e:
            print(f"Error removing protection: {e}")
            return 1
    
    def _show_info(self):
        print("="*60)
        print("M8taim - Ultimate Time-Based Protection System")
        print("="*60)
        print(f"Version: 1.0.0")
        print(f"Developer: MERO (@Qp4rm)")
        print(f"License: MIT")
        print("="*60)
        return 0

def main():
    cli = CLIManager()
    sys.exit(cli.run())
