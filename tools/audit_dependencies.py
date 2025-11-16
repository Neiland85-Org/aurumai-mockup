#!/usr/bin/env python3
"""
Dependency Audit Script for AurumAI Platform
Checks backend and frontend dependencies for known vulnerabilities.

Usage:
    python tools/audit_dependencies.py
    python tools/audit_dependencies.py --fix
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


class Color:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{text:^70}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.END}\n")


def print_section(text: str) -> None:
    """Print formatted section."""
    print(f"\n{Color.BOLD}{Color.BLUE}{text}{Color.END}")
    print(f"{Color.BLUE}{'-' * len(text)}{Color.END}")


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> tuple:
    """
    Run shell command and return output.
    
    Args:
        cmd: Command as list of strings
        cwd: Working directory (optional)
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out after 60 seconds"
    except Exception as e:
        return -1, "", str(e)


def audit_backend(fix: bool = False) -> Dict:
    """
    Audit backend Python dependencies.
    
    Args:
        fix: Whether to attempt automatic fixes
        
    Returns:
        Dictionary with audit results
    """
    print_section("🐍 Backend (Python) Dependency Audit")
    
    backend_dir = Path(__file__).parent.parent / "backend"
    
    if not backend_dir.exists():
        print(f"{Color.RED}❌ Backend directory not found{Color.END}")
        return {"status": "error", "vulnerabilities": []}
    
    results = {
        "status": "unknown",
        "vulnerabilities": [],
        "outdated": []
    }
    
    # Check if pip-audit is installed
    print(f"{Color.CYAN}📦 Checking for pip-audit...{Color.END}")
    code, stdout, stderr = run_command(["pip", "show", "pip-audit"])
    
    if code != 0:
        print(f"{Color.YELLOW}⚠️  pip-audit not installed. Installing...{Color.END}")
        code, _, _ = run_command(["pip", "install", "pip-audit"])
        if code != 0:
            print(f"{Color.RED}❌ Failed to install pip-audit{Color.END}")
            return results
    
    # Run pip-audit
    print(f"{Color.CYAN}🔍 Running pip-audit...{Color.END}")
    code, stdout, stderr = run_command(
        ["pip-audit", "--format", "json"],
        cwd=backend_dir
    )
    
    if code == 0:
        print(f"{Color.GREEN}✅ No vulnerabilities found!{Color.END}")
        results["status"] = "clean"
    else:
        try:
            vulns = json.loads(stdout) if stdout else []
            results["vulnerabilities"] = vulns
            results["status"] = "vulnerable"
            
            print(f"{Color.RED}🚨 Found {len(vulns)} vulnerabilities:{Color.END}\n")
            
            for vuln in vulns:
                package = vuln.get("name", "unknown")
                version = vuln.get("version", "unknown")
                vuln_id = vuln.get("id", "N/A")
                fix_versions = vuln.get("fix_versions", [])
                
                print(f"{Color.RED}  • {package} {version}{Color.END}")
                print(f"    {Color.YELLOW}Vulnerability: {vuln_id}{Color.END}")
                if fix_versions:
                    print(f"    {Color.GREEN}Fix: Upgrade to {', '.join(fix_versions)}{Color.END}")
                print()
        except json.JSONDecodeError:
            print(f"{Color.RED}❌ Error parsing audit results{Color.END}")
            print(f"Output: {stdout}")
            print(f"Error: {stderr}")
    
    # Check for outdated packages
    print(f"\n{Color.CYAN}📊 Checking for outdated packages...{Color.END}")
    code, stdout, _ = run_command(
        ["pip", "list", "--outdated", "--format", "json"],
        cwd=backend_dir
    )
    
    if code == 0 and stdout:
        try:
            outdated = json.loads(stdout)
            results["outdated"] = outdated
            
            if outdated:
                print(f"{Color.YELLOW}📦 {len(outdated)} outdated packages:{Color.END}\n")
                for pkg in outdated[:10]:  # Show first 10
                    name = pkg.get("name", "unknown")
                    current = pkg.get("version", "?")
                    latest = pkg.get("latest_version", "?")
                    print(f"  • {name}: {current} → {latest}")
                
                if len(outdated) > 10:
                    print(f"\n  ... and {len(outdated) - 10} more")
            else:
                print(f"{Color.GREEN}✅ All packages up to date!{Color.END}")
        except json.JSONDecodeError:
            pass
    
    return results


def audit_frontend(fix: bool = False) -> Dict:
    """
    Audit frontend npm dependencies.
    
    Args:
        fix: Whether to attempt automatic fixes
        
    Returns:
        Dictionary with audit results
    """
    print_section("📦 Frontend (npm) Dependency Audit")
    
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    if not frontend_dir.exists():
        print(f"{Color.RED}❌ Frontend directory not found{Color.END}")
        return {"status": "error", "vulnerabilities": []}
    
    results = {
        "status": "unknown",
        "vulnerabilities": [],
        "fix_available": False
    }
    
    # Run npm audit
    print(f"{Color.CYAN}🔍 Running npm audit...{Color.END}")
    
    cmd = ["npm", "audit", "--json"]
    if fix:
        cmd = ["npm", "audit", "fix", "--json"]
    
    code, stdout, stderr = run_command(cmd, cwd=frontend_dir)
    
    try:
        audit_data = json.loads(stdout) if stdout else {}
        
        # npm audit returns 0 if no vulnerabilities, non-zero otherwise
        vuln_count = audit_data.get("metadata", {}).get("vulnerabilities", {})
        total_vulns = sum(vuln_count.values()) if isinstance(vuln_count, dict) else 0
        
        if total_vulns == 0:
            print(f"{Color.GREEN}✅ No vulnerabilities found!{Color.END}")
            results["status"] = "clean"
        else:
            results["status"] = "vulnerable"
            results["vulnerabilities"] = audit_data.get("vulnerabilities", {})
            
            print(f"{Color.RED}🚨 Found vulnerabilities:{Color.END}\n")
            
            for severity, count in vuln_count.items():
                if count > 0:
                    color = Color.RED if severity in ["critical", "high"] else Color.YELLOW
                    print(f"{color}  • {severity.capitalize()}: {count}{Color.END}")
            
            # Check if fix is available
            if audit_data.get("metadata", {}).get("totalDependencies", 0) > 0:
                results["fix_available"] = True
                
                if not fix:
                    print(f"\n{Color.YELLOW}💡 Run with --fix to attempt automatic fixes{Color.END}")
                else:
                    print(f"\n{Color.GREEN}✅ Automatic fixes applied{Color.END}")
    
    except json.JSONDecodeError:
        # Older npm versions or errors might not return JSON
        if "found 0 vulnerabilities" in stdout.lower():
            print(f"{Color.GREEN}✅ No vulnerabilities found!{Color.END}")
            results["status"] = "clean"
        else:
            print(f"{Color.YELLOW}⚠️  Could not parse audit results{Color.END}")
            print(f"Output: {stdout[:500]}")
    
    # Check for outdated packages
    print(f"\n{Color.CYAN}📊 Checking for outdated packages...{Color.END}")
    code, stdout, _ = run_command(
        ["npm", "outdated", "--json"],
        cwd=frontend_dir
    )
    
    # npm outdated returns non-zero if there are outdated packages
    if stdout:
        try:
            outdated = json.loads(stdout)
            if outdated:
                print(f"{Color.YELLOW}📦 {len(outdated)} outdated packages:{Color.END}\n")
                for name, info in list(outdated.items())[:10]:  # Show first 10
                    current = info.get("current", "?")
                    latest = info.get("latest", "?")
                    print(f"  • {name}: {current} → {latest}")
                
                if len(outdated) > 10:
                    print(f"\n  ... and {len(outdated) - 10} more")
            else:
                print(f"{Color.GREEN}✅ All packages up to date!{Color.END}")
        except json.JSONDecodeError:
            pass
    else:
        print(f"{Color.GREEN}✅ All packages up to date!{Color.END}")
    
    return results


def generate_report(backend_results: Dict, frontend_results: Dict) -> None:
    """Generate summary report."""
    print_header("📊 Audit Summary Report")
    
    # Backend summary
    print(f"{Color.BOLD}Backend (Python):{Color.END}")
    backend_status = backend_results.get("status", "unknown")
    
    if backend_status == "clean":
        print(f"  Status: {Color.GREEN}✅ No vulnerabilities{Color.END}")
    elif backend_status == "vulnerable":
        vuln_count = len(backend_results.get("vulnerabilities", []))
        print(f"  Status: {Color.RED}🚨 {vuln_count} vulnerabilities found{Color.END}")
    else:
        print(f"  Status: {Color.YELLOW}⚠️  Unknown{Color.END}")
    
    outdated_count = len(backend_results.get("outdated", []))
    if outdated_count > 0:
        print(f"  Outdated: {Color.YELLOW}{outdated_count} packages{Color.END}")
    
    # Frontend summary
    print(f"\n{Color.BOLD}Frontend (npm):{Color.END}")
    frontend_status = frontend_results.get("status", "unknown")
    
    if frontend_status == "clean":
        print(f"  Status: {Color.GREEN}✅ No vulnerabilities{Color.END}")
    elif frontend_status == "vulnerable":
        print(f"  Status: {Color.RED}🚨 Vulnerabilities found{Color.END}")
        if frontend_results.get("fix_available"):
            print(f"  Fix: {Color.GREEN}Automatic fix available{Color.END}")
    else:
        print(f"  Status: {Color.YELLOW}⚠️  Unknown{Color.END}")
    
    # Overall recommendation
    print(f"\n{Color.BOLD}Recommendation:{Color.END}")
    
    if backend_status == "clean" and frontend_status == "clean":
        print(f"  {Color.GREEN}✅ All dependencies are secure!{Color.END}")
        print(f"  {Color.CYAN}Continue regular security audits (weekly recommended){Color.END}")
    else:
        print(f"  {Color.RED}⚠️  Action required:{Color.END}")
        
        if backend_status == "vulnerable":
            print(f"    1. Review backend vulnerabilities above")
            print(f"    2. Update affected packages: pip install --upgrade <package>")
        
        if frontend_status == "vulnerable":
            print(f"    3. Run: npm audit fix (in frontend directory)")
            print(f"    4. For breaking changes: npm audit fix --force")
        
        print(f"\n    5. Test all changes before deploying")
        print(f"    6. Commit updated requirements.txt / package-lock.json")
    
    print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Audit dependencies for security vulnerabilities"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to automatically fix vulnerabilities"
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Audit backend dependencies only"
    )
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Audit frontend dependencies only"
    )
    
    args = parser.parse_args()
    
    print_header("🔐 AurumAI Dependency Security Audit")
    
    backend_results = {}
    frontend_results = {}
    
    # Run audits
    if not args.frontend_only:
        backend_results = audit_backend(fix=args.fix)
    
    if not args.backend_only:
        frontend_results = audit_frontend(fix=args.fix)
    
    # Generate report
    generate_report(backend_results, frontend_results)
    
    # Exit with error code if vulnerabilities found
    backend_vulnerable = backend_results.get("status") == "vulnerable"
    frontend_vulnerable = frontend_results.get("status") == "vulnerable"
    
    if backend_vulnerable or frontend_vulnerable:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
