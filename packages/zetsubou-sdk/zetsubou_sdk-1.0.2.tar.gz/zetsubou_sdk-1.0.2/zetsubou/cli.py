#!/usr/bin/env python3
"""
Zetsubou.life CLI Tool

Command-line interface for the Zetsubou.life SDK.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .client import ZetsubouClient
from .exceptions import ZetsubouError


def list_tools(client: ZetsubouClient, category: Optional[str] = None):
    """List available tools."""
    tools = client.tools.list()
    
    if category:
        tools = [t for t in tools if t.category == category]
    
    print(f"\nAvailable Tools ({len(tools)}):")
    print("=" * 50)
    
    for tool in tools:
        status = "✅" if tool.accessible else "❌"
        print(f"{status} {tool.name}")
        print(f"   ID: {tool.id}")
        print(f"   Category: {tool.category}")
        print(f"   Tier: {tool.required_tier}")
        print(f"   Input: {tool.input_type} → Output: {tool.output_type}")
        if tool.description:
            print(f"   Description: {tool.description}")
        print()


def execute_tool(
    client: ZetsubouClient,
    tool_id: str,
    files: List[str],
    options: Optional[dict] = None,
    wait: bool = True
):
    """Execute a tool."""
    print(f"Executing tool: {tool_id}")
    print(f"Files: {', '.join(files)}")
    
    if options:
        print(f"Options: {json.dumps(options, indent=2)}")
    
    try:
        # Execute the tool
        job = client.tools.execute(tool_id, files, options or {})
        print(f"\nJob started: {job.id}")
        print(f"Status: {job.status}")
        
        if wait:
            print("Waiting for completion...")
            completed_job = client.jobs.wait_for_completion(job.id)
            print(f"\nJob completed!")
            print(f"Status: {completed_job.status}")
            print(f"Progress: {completed_job.progress}%")
            
            if completed_job.outputs:
                print(f"Outputs: {', '.join(completed_job.outputs)}")
                
                # Ask if user wants to download results
                download = input("\nDownload results? (y/N): ").lower().strip()
                if download == 'y':
                    output_file = f"results_{job.id}.zip"
                    client.jobs.download_results(job.id, output_file)
                    print(f"Results downloaded to: {output_file}")
        else:
            print(f"\nJob submitted. Use 'zetsubou jobs get {job.id}' to check status.")
            
    except ZetsubouError as e:
        print(f"Error: {e}")
        sys.exit(1)


def list_jobs(client: ZetsubouClient, status: Optional[str] = None, limit: int = 10):
    """List jobs."""
    jobs = client.jobs.list(status=status, limit=limit)
    
    print(f"\nRecent Jobs ({len(jobs)}):")
    print("=" * 50)
    
    for job in jobs:
        status_icon = {
            'completed': '✅',
            'failed': '❌',
            'running': '🔄',
            'pending': '⏳',
            'cancelled': '⏹️'
        }.get(job.status, '❓')
        
        print(f"{status_icon} {job.id}")
        print(f"   Tool: {job.tool_id}")
        print(f"   Status: {job.status}")
        print(f"   Progress: {job.progress}%")
        print(f"   Created: {job.created_at}")
        if job.error:
            print(f"   Error: {job.error}")
        print()


def get_job(client: ZetsubouClient, job_id: str):
    """Get job details."""
    try:
        job = client.jobs.get(job_id)
        
        print(f"\nJob Details: {job.id}")
        print("=" * 30)
        print(f"Tool: {job.tool_id}")
        print(f"Status: {job.status}")
        print(f"Progress: {job.progress}%")
        print(f"Created: {job.created_at}")
        print(f"Updated: {job.updated_at}")
        
        if job.completed_at:
            print(f"Completed: {job.completed_at}")
        
        if job.inputs:
            print(f"Inputs: {', '.join(job.inputs)}")
        
        if job.outputs:
            print(f"Outputs: {', '.join(job.outputs)}")
        
        if job.error:
            print(f"Error: {job.error}")
        
        if job.options:
            print(f"Options: {json.dumps(job.options, indent=2)}")
            
    except ZetsubouError as e:
        print(f"Error: {e}")
        sys.exit(1)


def list_files(client: ZetsubouClient, limit: int = 20):
    """List VFS files."""
    files = client.vfs.list_nodes(node_type="file", limit=limit)
    
    print(f"\nVFS Files ({len(files)}):")
    print("=" * 50)
    
    for file in files:
        size_mb = file.size_bytes / (1024 * 1024)
        print(f"📄 {file.name}")
        print(f"   ID: {file.id}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Type: {file.mime_type}")
        print(f"   Created: {file.created_at}")
        print()


def account_info(client: ZetsubouClient):
    """Show account information."""
    try:
        account = client.account.get_account()
        quota = client.account.get_storage_quota()
        
        print(f"\nAccount Information:")
        print("=" * 30)
        print(f"Username: {account.username}")
        print(f"Email: {account.email}")
        print(f"Tier: {account.tier}")
        print(f"Created: {account.created_at}")
        
        print(f"\nStorage Quota:")
        print(f"Used: {quota.used_bytes:,} bytes ({quota.usage_percent:.1f}%)")
        print(f"Available: {quota.available_bytes:,} bytes")
        print(f"Total: {quota.quota_bytes:,} bytes")
        print(f"Files: {quota.file_count}")
        print(f"Folders: {quota.folder_count}")
        
        print(f"\nFeatures:")
        for feature, value in account.features.items():
            if isinstance(value, list):
                print(f"  {feature}: {len(value)} items")
            else:
                print(f"  {feature}: {value}")
                
    except ZetsubouError as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Zetsubou.life CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zetsubou tools list
  zetsubou tools list --category video
  zetsubou tools execute remove_bg image.jpg
  zetsubou tools execute datamosher video1.mp4 video2.mp4 --options '{"width": 640}'
  zetsubou jobs list
  zetsubou jobs get job_123
  zetsubou files list
  zetsubou account info
        """
    )
    
    parser.add_argument(
        '--api-key',
        help='API key (or set ZETSUBOU_API_KEY environment variable)',
        default=None
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Tools commands
    tools_parser = subparsers.add_parser('tools', help='Tool operations')
    tools_subparsers = tools_parser.add_subparsers(dest='tools_action')
    
    tools_subparsers.add_parser('list', help='List available tools')
    tools_subparsers.add_parser('execute', help='Execute a tool')
    
    # Jobs commands
    jobs_parser = subparsers.add_parser('jobs', help='Job operations')
    jobs_subparsers = jobs_parser.add_subparsers(dest='jobs_action')
    
    jobs_subparsers.add_parser('list', help='List jobs')
    jobs_subparsers.add_parser('get', help='Get job details')
    
    # Files commands
    files_parser = subparsers.add_parser('files', help='File operations')
    files_subparsers = files_parser.add_subparsers(dest='files_action')
    
    files_subparsers.add_parser('list', help='List VFS files')
    
    # Account commands
    account_parser = subparsers.add_parser('account', help='Account operations')
    account_subparsers = account_parser.add_subparsers(dest='account_action')
    
    account_subparsers.add_parser('info', help='Show account information')
    
    args, unknown_args = parser.parse_known_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get('ZETSUBOU_API_KEY')
    if not api_key:
        print("Error: API key required. Set --api-key or ZETSUBOU_API_KEY environment variable.")
        sys.exit(1)
    
    # Initialize client
    try:
        client = ZetsubouClient(api_key)
    except Exception as e:
        print(f"Error initializing client: {e}")
        sys.exit(1)
    
    try:
        if args.command == 'tools':
            if args.tools_action == 'list':
                category = None
                if '--category' in unknown_args:
                    idx = unknown_args.index('--category')
                    if idx + 1 < len(unknown_args):
                        category = unknown_args[idx + 1]
                list_tools(client, category)
                
            elif args.tools_action == 'execute':
                if len(unknown_args) < 2:
                    print("Error: tool ID and files required")
                    print("Usage: zetsubou tools execute <tool_id> <file1> [file2] ...")
                    sys.exit(1)
                
                tool_id = unknown_args[0]
                files = unknown_args[1:]
                
                # Parse options if provided
                options = None
                if '--options' in unknown_args:
                    idx = unknown_args.index('--options')
                    if idx + 1 < len(unknown_args):
                        try:
                            options = json.loads(unknown_args[idx + 1])
                        except json.JSONDecodeError:
                            print("Error: Invalid JSON in --options")
                            sys.exit(1)
                
                execute_tool(client, tool_id, files, options)
        
        elif args.command == 'jobs':
            if args.jobs_action == 'list':
                status = None
                if '--status' in unknown_args:
                    idx = unknown_args.index('--status')
                    if idx + 1 < len(unknown_args):
                        status = unknown_args[idx + 1]
                list_jobs(client, status)
                
            elif args.jobs_action == 'get':
                if len(unknown_args) < 1:
                    print("Error: job ID required")
                    print("Usage: zetsubou jobs get <job_id>")
                    sys.exit(1)
                get_job(client, unknown_args[0])
        
        elif args.command == 'files':
            if args.files_action == 'list':
                list_files(client)
        
        elif args.command == 'account':
            if args.account_action == 'info':
                account_info(client)
        
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except ZetsubouError as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    import os
    main()