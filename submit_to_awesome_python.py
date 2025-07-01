#!/usr/bin/env python3
"""
Script to automatically add envvar-validator to Awesome Python README.md
Run this script from the awesome-python directory after cloning your fork
"""

import re
import os

def update_readme():
    """Update the README.md file with envvar-validator entries"""
    
    # Check if we're in the right directory
    if not os.path.exists('README.md'):
        print("❌ Error: README.md not found. Please run this script from the awesome-python directory.")
        return False
    
    print("📖 Reading README.md...")
    
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Store original content for backup
    with open('README.md.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Created backup: README.md.backup")
    
    # 1. Update Newly Created Repositories section
    print("🔧 Adding to Newly Created Repositories section...")
    
    # Find the end of the Newly Created Repositories section
    newly_created_pattern = r'(10\. <a href="https://github\.com/sakanaai/ai-scientist-iclr2025-workshop-experiment">sakanaai/</a><b><a href="https://github\.com/sakanaai/ai-scientist-iclr2025-workshop-experiment">AI-Scientist-ICLR2025-Workshop-Experiment</a></b> ⭐ 192    \n   A paper produced by The AI Scientist passed a peer-review process at a workshop in a top machine learning conference  \n\n## Agentic AI)'
    
    newly_created_replacement = r'''10. <a href="https://github.com/sakanaai/ai-scientist-iclr2025-workshop-experiment">sakanaai/</a><b><a href="https://github.com/sakanaai/ai-scientist-iclr2025-workshop-experiment">AI-Scientist-ICLR2025-Workshop-Experiment</a></b> ⭐ 192    
   A paper produced by The AI Scientist passed a peer-review process at a workshop in a top machine learning conference  

11. <a href="https://github.com/Sherin-SEF-AI/envvar-validator">Sherin-SEF-AI/</a><b><a href="https://github.com/Sherin-SEF-AI/envvar-validator">envvar-validator</a></b> ⭐ 0    
   The most comprehensive environment variable validation library for Python with CLI tools, framework integrations, and security scanning.  
   🔗 [pypi.org/project/envvar-validator](https://pypi.org/project/envvar-validator/)  

## Agentic AI'''
    
    content = re.sub(newly_created_pattern, newly_created_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # 2. Update Security section
    print("🔒 Adding to Security section...")
    
    # Find the end of the Security section
    security_pattern = r'(16\. <a href="https://github\.com/thecyb3ralpha/bobthesmuggler">thecyb3ralpha/</a><b><a href="https://github\.com/thecyb3ralpha/bobthesmuggler">BobTheSmuggler</a></b> ⭐ 530    \n   A tool that leverages HTML Smuggling Attack and allows you to create HTML files with embedded 7z/zip archives.  \n\n## Simulation)'
    
    security_replacement = r'''16. <a href="https://github.com/thecyb3ralpha/bobthesmuggler">thecyb3ralpha/</a><b><a href="https://github.com/thecyb3ralpha/bobthesmuggler">BobTheSmuggler</a></b> ⭐ 530    
   A tool that leverages HTML Smuggling Attack and allows you to create HTML files with embedded 7z/zip archives.  

17. <a href="https://github.com/Sherin-SEF-AI/envvar-validator">Sherin-SEF-AI/</a><b><a href="https://github.com/Sherin-SEF-AI/envvar-validator">envvar-validator</a></b> ⭐ 0    
   The most comprehensive environment variable validation library for Python with CLI tools, framework integrations, and security scanning.  
   🔗 [pypi.org/project/envvar-validator](https://pypi.org/project/envvar-validator/)  

## Simulation'''
    
    content = re.sub(security_pattern, security_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # 3. Update category counts in table of contents
    print("📊 Updating category counts...")
    
    # Update Newly Created Repositories count
    content = re.sub(
        r'\(10 repos\)',
        '(11 repos)',
        content
    )
    
    # Update Security count
    content = re.sub(
        r'\(16 repos\)',
        '(17 repos)',
        content
    )
    
    # Write the updated content
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully updated README.md!")
    print("📝 Changes made:")
    print("   - Added envvar-validator to Newly Created Repositories (entry #11)")
    print("   - Added envvar-validator to Security section (entry #17)")
    print("   - Updated category counts: Newly Created (10→11), Security (16→17)")
    
    return True

def create_pr_description():
    """Create the PR description file"""
    
    pr_description = """## Add envvar-validator to Security and Newly Created Repositories sections

### What is this?
envvar-validator is the most comprehensive environment variable validation library for Python.

### Why should this be added?
- **Comprehensive Validation**: 20+ built-in validators for security, data, cloud, and system validation
- **Framework Integration**: FastAPI, Django, and Flask integrations with automatic validation
- **CLI Tool**: Full-featured command-line interface for validation and security scanning
- **Security First**: Built-in security scanning, compliance checking, and audit logging
- **Production Ready**: Sub-millisecond validation times, comprehensive error handling
- **Developer Experience**: Interactive setup wizard, detailed documentation, working examples

### Features:
- ✅ Real-time environment variable validation
- ✅ Security scanning and compliance checking
- ✅ Framework integrations (FastAPI, Django, Flask)
- ✅ CLI tool with 6 commands
- ✅ 20+ built-in validators
- ✅ Performance monitoring and health checks
- ✅ Comprehensive documentation and examples

### Links:
- GitHub: https://github.com/Sherin-SEF-AI/envvar-validator
- PyPI: https://pypi.org/project/envvar-validator/
- Documentation: https://github.com/Sherin-SEF-AI/envvar-validator#readme

### Categories Added:
- **Security**: Environment variable security scanning and validation
- **Newly Created Repositories**: Recently created and actively maintained
"""
    
    with open('PR_DESCRIPTION.md', 'w', encoding='utf-8') as f:
        f.write(pr_description)
    
    print("📄 Created PR_DESCRIPTION.md - use this for your pull request!")

def main():
    """Main function"""
    print("🚀 Awesome Python Submission Script")
    print("=" * 50)
    
    if update_readme():
        create_pr_description()
        
        print("\n🎉 Next Steps:")
        print("1. Review the changes: git diff README.md")
        print("2. Commit the changes: git add README.md")
        print("3. Commit: git commit -m 'Add envvar-validator to Security and Newly Created Repositories sections'")
        print("4. Push: git push origin add-envvar-validator")
        print("5. Create PR on GitHub using the description in PR_DESCRIPTION.md")
        
        print("\n✅ Your package is ready for Awesome Python!")
    else:
        print("❌ Failed to update README.md")

if __name__ == "__main__":
    main() 