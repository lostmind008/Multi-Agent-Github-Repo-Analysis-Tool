#!/usr/bin/env python3
"""
Multi-Agent GitHub Analysis System - CLI Interface
Enhanced with code-reviewer subagents for quality assurance.
"""
import argparse
import sys
import os
from typing import Optional
from src.workflow import run_analysis, get_quality_summary
from src.report import generate_enhanced_report, build_pdf


def setup_environment():
    """Verify environment setup and requirements."""
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("   Please copy .env.example to .env and configure your API keys.")
        print("   The system may not work properly without proper configuration.")
        print()
    
    # Check critical environment variables
    required_vars = ['GITHUB_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please configure these in your .env file.")
        return False
    
    # Check for at least one LLM provider
    llm_vars = ['OPENAI_API_KEY', 'GOOGLE_API_KEY', 'ANTHROPIC_API_KEY', 'GROK_API_KEY']
    has_llm = any(os.getenv(var) for var in llm_vars)
    
    if not has_llm:
        print("⚠️  Warning: No LLM provider API keys found!")
        print("   Please configure at least one of: OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, GROK_API_KEY")
        print("   The system requires LLM access for analysis.")
        return False
    
    return True


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="Multi-Agent GitHub Repository Analysis System with Code Review",
        epilog="""
Examples:
  %(prog)s --user octocat
  %(prog)s --user microsoft --repos vscode,TypeScript
  %(prog)s --user your-username --repos your-repo --out custom_report.pdf
  %(prog)s --user fastapi --repos fastapi --enhanced
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--user", 
        required=False, 
        help="GitHub username to analyze"
    )
    
    parser.add_argument(
        "--repos", 
        default="all", 
        help="Repository selection: 'all' for all repos, or comma-separated list of specific repos (default: all)"
    )
    
    parser.add_argument(
        "--out", 
        default="reports/repo_report.pdf", 
        help="Output PDF file path (default: reports/repo_report.pdf)"
    )
    
    parser.add_argument(
        "--enhanced",
        action="store_true",
        help="Generate enhanced PDF report with quality metrics and appendix"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output (only show final results)"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate environment setup, don't run analysis"
    )
    
    args = parser.parse_args()
    
    # ASCII art header
    if not args.quiet:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║          Multi-Agent GitHub Analysis System v2.0                 ║
║                   Enhanced with Code Review                       ║
╚═══════════════════════════════════════════════════════════════════╝
        """)
    
    # Validate environment
    if not setup_environment():
        if not args.quiet:
            print("❌ Environment validation failed. Please check your configuration.")
        sys.exit(1)
    
    if args.validate_only:
        print("✅ Environment validation successful!")
        print("   System ready for analysis.")
        sys.exit(0)
    
    # Validate inputs
    if not args.user:
        print("❌ GitHub username is required for analysis")
        sys.exit(1)
        
    if not args.user.strip():
        print("❌ GitHub username cannot be empty")
        sys.exit(1)
    
    if args.repos != "all" and not args.repos.strip():
        print("❌ Repository list cannot be empty (use 'all' for all repositories)")
        sys.exit(1)
    
    # Run analysis
    try:
        if not args.quiet:
            print(f"🎯 Target: GitHub user '{args.user}'")
            print(f"📁 Scope: {args.repos}")
            print(f"📄 Output: {args.out}")
            print(f"🔧 Enhanced: {args.enhanced}")
            print()
        
        # Execute the multi-agent workflow
        result = run_analysis(args.user, args.repos)
        
        # Generate PDF report
        if args.enhanced:
            pdf_path = generate_enhanced_report(result, args.out)
        else:
            # Use legacy PDF generation for compatibility
            quality_summary = get_quality_summary(result)
            pdf_path = build_pdf(
                report=result["final_report"],
                username=args.user,
                quality_summary=quality_summary,
                outfile=args.out
            )
        
        # Final results
        print()
        print("🎉 Analysis Complete!")
        print(f"📊 Report saved to: {pdf_path}")
        
        # Quality summary
        quality_summary = get_quality_summary(result)
        print(f"✅ Overall Quality: {'Approved' if quality_summary['overall_approved'] else 'Issues Found'}")
        print(f"📈 Repositories Analyzed: {quality_summary['repositories_analyzed']}")
        print(f"📁 Files Processed: {quality_summary['total_files_processed']}")
        
        # Quality details
        if not quality_summary['overall_approved']:
            print("\n⚠️  Quality Issues Summary:")
            
            if not quality_summary['data_quality']['approved']:
                print("   • Data Quality: Issues found during data fetching")
                
            if not quality_summary['analysis_quality']['approved']:
                print("   • Analysis Quality: Analysis depth or accuracy concerns")
                
            if not quality_summary['final_quality']['approved']:
                print("   • Final Quality: Report formatting or completeness issues")
                
            print("   📋 Detailed quality feedback available in PDF appendix")
        
        print(f"\n📖 Open your report: {pdf_path}")
        
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        if not args.quiet:
            print("\n🔍 Troubleshooting tips:")
            print("   • Verify your GitHub token has proper permissions")
            print("   • Check that the username and repository names are correct")
            print("   • Ensure your LLM provider API keys are valid")
            print("   • Try with a smaller repository first (--repos specific-repo)")
            print("   • Use --validate-only to check your environment setup")
        sys.exit(1)


if __name__ == "__main__":
    main()