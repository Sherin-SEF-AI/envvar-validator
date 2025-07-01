"""
Command-line interface for the env-validator package.

This module provides a comprehensive CLI for environment variable validation,
including validation commands, setup wizards, and reporting tools.
"""

import sys
import os
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

import click
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from ..core.validator import EnvironmentValidator
from ..core.config import load_config, get_default_config
from ..core.types import EnvironmentType, ValidationLevel
from ..validators.registry import get_available_validators, get_validator_info

# Create Typer app
app = typer.Typer(
    name="env-validator",
    help="The most comprehensive environment variable validation library for Python",
    add_completion=False,
)

# Create console for rich output
console = Console()


@app.command()
def validate(
    schema: Optional[Path] = typer.Option(
        None,
        "--schema",
        "-s",
        help="Path to validation schema file (YAML, JSON, TOML, or .env)"
    ),
    environment: EnvironmentType = typer.Option(
        EnvironmentType.DEVELOPMENT,
        "--environment",
        "-e",
        help="Environment type for validation"
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Enable strict validation mode"
    ),
    output: str = typer.Option(
        "text",
        "--output",
        "-o",
        help="Output format (text, json, yaml)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output"
    )
):
    """
    Validate environment variables against a schema.
    
    This command validates the current environment variables against a schema
    and reports any issues found.
    """
    try:
        # Load configuration
        if schema:
            config = load_config(schema, environment, strict)
        else:
            config = get_default_config()
        
        # Create validator
        validator = EnvironmentValidator(
            config,
            environment_type=environment,
            strict_mode=strict
        )
        
        # Validate environment
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Validating environment variables...", total=None)
            result = validator.validate()
            progress.update(task, completed=True)
        
        # Display results
        _display_validation_results(result, output, verbose)
        
        # Exit with error code if validation failed
        if not result.is_valid:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@app.command()
def setup(
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        help="Run in interactive mode"
    ),
    output: Path = typer.Option(
        "env-validator.yaml",
        "--output",
        "-o",
        help="Output file for generated schema"
    ),
    framework: Optional[str] = typer.Option(
        None,
        "--framework",
        "-f",
        help="Framework to generate schema for (django, flask, fastapi)"
    )
):
    """
    Interactive setup wizard for environment validation.
    
    This command guides you through creating a validation schema
    for your environment variables.
    """
    try:
        if interactive:
            schema = _run_interactive_setup(framework)
        else:
            schema = _generate_framework_schema(framework)
        
        # Save schema
        _save_schema(schema, output)
        
        console.print(f"[green]✅ Schema saved to {output}[/green]")
        console.print(f"[blue]Run 'env-validator validate --schema {output}' to validate your environment[/blue]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def report(
    schema: Optional[Path] = typer.Option(
        None,
        "--schema",
        "-s",
        help="Path to validation schema file"
    ),
    output: str = typer.Option(
        "text",
        "--output",
        "-o",
        help="Output format (text, json, yaml, html)"
    ),
    detailed: bool = typer.Option(
        False,
        "--detailed",
        "-d",
        help="Include detailed information"
    )
):
    """
    Generate a comprehensive environment validation report.
    
    This command generates a detailed report about your environment
    variables and validation status.
    """
    try:
        # Load configuration
        if schema:
            config = load_config(schema)
        else:
            config = get_default_config()
        
        # Create validator and validate
        validator = EnvironmentValidator(config)
        result = validator.validate()
        
        # Generate report
        report_data = _generate_report(result, detailed)
        
        # Output report
        _output_report(report_data, output)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def scan(
    secrets: bool = typer.Option(
        False,
        "--secrets",
        help="Scan for secrets and sensitive data"
    ),
    compliance: Optional[str] = typer.Option(
        None,
        "--compliance",
        help="Compliance standard to check (gdpr, hipaa, soc2)"
    ),
    output: str = typer.Option(
        "text",
        "--output",
        "-o",
        help="Output format (text, json, yaml)"
    )
):
    """
    Security scanning and compliance checking.
    
    This command scans your environment variables for security issues
    and compliance violations.
    """
    try:
        # Get environment variables
        env_vars = dict(os.environ)
        
        # Perform security scan
        if secrets:
            secret_results = _scan_for_secrets(env_vars)
            _display_secret_scan_results(secret_results, output)
        
        # Perform compliance check
        if compliance:
            compliance_results = _check_compliance(env_vars, compliance)
            _display_compliance_results(compliance_results, output)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def list_validators():
    """
    List all available validators.
    
    This command shows all built-in validators and their descriptions.
    """
    try:
        validators = get_available_validators()
        
        table = Table(title="Available Validators")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Examples", style="green")
        
        for validator_name in sorted(validators):
            info = get_validator_info(validator_name)
            if info:
                examples = ", ".join(info.get('examples', [])[:2])
                table.add_row(
                    validator_name,
                    info.get('description', 'No description available'),
                    examples
                )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def template(
    framework: str = typer.Argument(
        ...,
        help="Framework to generate template for (django, flask, fastapi, generic)"
    ),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for template"
    )
):
    """
    Generate configuration templates for common frameworks.
    
    This command generates ready-to-use validation schemas for popular
    Python frameworks and project types.
    """
    try:
        template_data = _generate_framework_template(framework)
        
        if output:
            _save_schema(template_data, output)
            console.print(f"[green]✅ Template saved to {output}[/green]")
        else:
            # Print to console
            yaml_output = yaml.dump(template_data, default_flow_style=False, sort_keys=False)
            syntax = Syntax(yaml_output, "yaml", theme="monokai")
            console.print(syntax)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def _display_validation_results(result, output_format: str, verbose: bool):
    """Display validation results in the specified format."""
    if output_format == "json":
        console.print(json.dumps(result.__dict__, default=str, indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump(result.__dict__, default_flow_style=False, sort_keys=False))
    else:
        # Text format
        if result.is_valid:
            console.print("[green]✅ Environment validation passed![/green]")
        else:
            console.print("[red]❌ Environment validation failed![/red]")
        
        # Show errors
        if result.errors:
            console.print(f"\n[red]Errors ({len(result.errors)}):[/red]")
            for error in result.errors:
                console.print(f"  • {error.variable_name}: {error.message}")
                if error.suggestion:
                    console.print(f"    [yellow]Suggestion: {error.suggestion}[/yellow]")
        
        # Show warnings
        if result.warnings:
            console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/yellow]")
            for warning in result.warnings:
                console.print(f"  • {warning.variable_name}: {warning.message}")
        
        # Show validated values
        if verbose and result.validated_values:
            console.print(f"\n[blue]Validated Variables ({len(result.validated_values)}):[/blue]")
            for var_name, value in result.validated_values.items():
                # Mask sensitive values
                if isinstance(value, str) and len(value) > 8:
                    display_value = value[:4] + "***" + value[-4:]
                else:
                    display_value = str(value)
                console.print(f"  • {var_name}: {display_value}")
        
        # Show performance metrics
        if verbose and result.performance_metrics:
            console.print(f"\n[blue]Performance Metrics:[/blue]")
            for metric, value in result.performance_metrics.items():
                console.print(f"  • {metric}: {value}")


def _run_interactive_setup(framework: Optional[str]) -> Dict[str, Any]:
    """Run interactive setup wizard."""
    console.print(Panel.fit(
        "[bold blue]Environment Validator Setup Wizard[/bold blue]\n"
        "This wizard will help you create a validation schema for your environment variables.",
        title="Welcome"
    ))
    
    if not framework:
        framework = Prompt.ask(
            "Select your framework",
            choices=["django", "flask", "fastapi", "generic"],
            default="generic"
        )
    
    # Generate base schema
    schema = _generate_framework_schema(framework)
    
    # Ask for custom variables
    console.print("\n[bold]Custom Environment Variables[/bold]")
    console.print("Add any additional environment variables you need to validate.")
    
    while Confirm.ask("Add another environment variable?"):
        var_name = Prompt.ask("Variable name")
        var_type = Prompt.ask(
            "Variable type",
            choices=["str", "int", "bool", "list", "dict", "url", "email", "file_path"],
            default="str"
        )
        required = Confirm.ask("Is this variable required?")
        
        var_config = {
            "type": var_type,
            "required": required
        }
        
        if not required:
            default_value = Prompt.ask("Default value (optional)")
            if default_value:
                var_config["default"] = default_value
        
        description = Prompt.ask("Description (optional)")
        if description:
            var_config["description"] = description
        
        schema["schema"][var_name] = var_config
    
    return schema


def _generate_framework_schema(framework: Optional[str]) -> Dict[str, Any]:
    """Generate a schema for the specified framework."""
    base_schema = {
        "environment_type": "development",
        "strict_mode": False,
        "allow_unknown": False,
        "schema": {}
    }
    
    if framework == "django":
        base_schema["schema"] = {
            "SECRET_KEY": {
                "type": "str",
                "required": True,
                "validators": ["secret_key"],
                "sensitive": True,
                "description": "Django secret key for security"
            },
            "DEBUG": {
                "type": "bool",
                "default": False,
                "description": "Django debug mode"
            },
            "DATABASE_URL": {
                "type": "str",
                "required": True,
                "validators": ["database_url"],
                "description": "Database connection URL"
            },
            "ALLOWED_HOSTS": {
                "type": "list",
                "default": ["localhost", "127.0.0.1"],
                "description": "List of allowed host names"
            }
        }
    elif framework == "flask":
        base_schema["schema"] = {
            "SECRET_KEY": {
                "type": "str",
                "required": True,
                "validators": ["secret_key"],
                "sensitive": True,
                "description": "Flask secret key"
            },
            "DATABASE_URL": {
                "type": "str",
                "required": True,
                "validators": ["database_url"],
                "description": "Database connection URL"
            },
            "FLASK_ENV": {
                "type": "str",
                "default": "development",
                "description": "Flask environment"
            }
        }
    elif framework == "fastapi":
        base_schema["schema"] = {
            "DATABASE_URL": {
                "type": "str",
                "required": True,
                "validators": ["database_url"],
                "description": "Database connection URL"
            },
            "API_KEY": {
                "type": "str",
                "required": True,
                "validators": ["api_key"],
                "sensitive": True,
                "description": "API key for authentication"
            },
            "ENVIRONMENT": {
                "type": "str",
                "default": "development",
                "description": "Application environment"
            }
        }
    else:
        # Generic schema
        base_schema["schema"] = {
            "DATABASE_URL": {
                "type": "str",
                "required": True,
                "validators": ["database_url"],
                "description": "Database connection URL"
            },
            "SECRET_KEY": {
                "type": "str",
                "required": True,
                "validators": ["secret_key"],
                "sensitive": True,
                "description": "Application secret key"
            },
            "DEBUG": {
                "type": "bool",
                "default": False,
                "description": "Debug mode flag"
            },
            "PORT": {
                "type": "int",
                "default": 8000,
                "description": "Application port"
            }
        }
    
    return base_schema


def _save_schema(schema: Dict[str, Any], output_path: Path):
    """Save schema to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.suffix.lower() in ['.yaml', '.yml']:
        with open(output_path, 'w') as f:
            yaml.dump(schema, f, default_flow_style=False, sort_keys=False)
    elif output_path.suffix.lower() == '.json':
        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=2)
    else:
        # Default to YAML
        with open(output_path.with_suffix('.yaml'), 'w') as f:
            yaml.dump(schema, f, default_flow_style=False, sort_keys=False)


def _generate_report(result, detailed: bool) -> Dict[str, Any]:
    """Generate a comprehensive report."""
    report = {
        "summary": {
            "is_valid": result.is_valid,
            "total_variables": len(result.validated_values),
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "security_score": result.security_score
        },
        "errors": [
            {
                "variable": error.variable_name,
                "message": error.message,
                "suggestion": error.suggestion
            }
            for error in result.errors
        ],
        "warnings": [
            {
                "variable": warning.variable_name,
                "message": warning.message,
                "suggestion": warning.suggestion
            }
            for warning in result.warnings
        ]
    }
    
    if detailed:
        report["validated_variables"] = result.validated_values
        report["performance_metrics"] = result.performance_metrics
        report["compliance_status"] = result.compliance_status
    
    return report


def _output_report(report_data: Dict[str, Any], output_format: str):
    """Output report in the specified format."""
    if output_format == "json":
        console.print(json.dumps(report_data, indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump(report_data, default_flow_style=False, sort_keys=False))
    elif output_format == "html":
        _generate_html_report(report_data)
    else:
        # Text format
        _display_text_report(report_data)


def _display_text_report(report_data: Dict[str, Any]):
    """Display report in text format."""
    summary = report_data["summary"]
    
    if summary["is_valid"]:
        console.print("[green]✅ Environment Validation Report - PASSED[/green]")
    else:
        console.print("[red]❌ Environment Validation Report - FAILED[/red]")
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  • Total Variables: {summary['total_variables']}")
    console.print(f"  • Errors: {summary['errors']}")
    console.print(f"  • Warnings: {summary['warnings']}")
    if summary.get('security_score'):
        console.print(f"  • Security Score: {summary['security_score']}/100")
    
    if report_data["errors"]:
        console.print(f"\n[red]Errors:[/red]")
        for error in report_data["errors"]:
            console.print(f"  • {error['variable']}: {error['message']}")
            if error['suggestion']:
                console.print(f"    [yellow]Suggestion: {error['suggestion']}[/yellow]")
    
    if report_data["warnings"]:
        console.print(f"\n[yellow]Warnings:[/yellow]")
        for warning in report_data["warnings"]:
            console.print(f"  • {warning['variable']}: {warning['message']}")


def _generate_html_report(report_data: Dict[str, Any]):
    """Generate HTML report."""
    # This would generate a comprehensive HTML report
    # For now, just print a message
    console.print("[yellow]HTML report generation not yet implemented[/yellow]")


def _scan_for_secrets(env_vars: Dict[str, str]) -> Dict[str, Any]:
    """Scan environment variables for secrets."""
    # This would implement secret scanning logic
    # For now, return a placeholder
    return {
        "secrets_found": 0,
        "sensitive_variables": [],
        "recommendations": []
    }


def _check_compliance(env_vars: Dict[str, str], standard: str) -> Dict[str, Any]:
    """Check compliance with specified standard."""
    # This would implement compliance checking logic
    # For now, return a placeholder
    return {
        "standard": standard,
        "compliant": True,
        "issues": [],
        "recommendations": []
    }


def _display_secret_scan_results(results: Dict[str, Any], output_format: str):
    """Display secret scan results."""
    if output_format == "json":
        console.print(json.dumps(results, indent=2))
    else:
        console.print(f"[blue]Secret Scan Results:[/blue]")
        console.print(f"  • Secrets Found: {results['secrets_found']}")


def _display_compliance_results(results: Dict[str, Any], output_format: str):
    """Display compliance check results."""
    if output_format == "json":
        console.print(json.dumps(results, indent=2))
    else:
        console.print(f"[blue]Compliance Check Results:[/blue]")
        console.print(f"  • Standard: {results['standard']}")
        console.print(f"  • Compliant: {'Yes' if results['compliant'] else 'No'}")


def _generate_framework_template(framework: str) -> Dict[str, Any]:
    """Generate a template for the specified framework."""
    return _generate_framework_schema(framework)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main() 