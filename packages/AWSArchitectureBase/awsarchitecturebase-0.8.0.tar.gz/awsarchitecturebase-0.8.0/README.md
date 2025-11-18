# AWS Architecture Base

A comprehensive AWS infrastructure framework built with CDKTF (Cloud Development Kit for Terraform) and Python, providing standardized deployment patterns for AWS Lightsail container services with automated SSL certificate management and domain attachment.

[![Version](https://img.shields.io/badge/version-0.1.20-blue.svg)](./AWSArchitectureBase/pyproject.toml)
[![Python](https://img.shields.io/badge/python->=3.8-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CDKTF](https://img.shields.io/badge/CDKTF->=0.17.0-orange.svg)](https://developer.hashicorp.com/terraform/cdktf)

## 🏗️ Overview

The AWS Architecture Base provides a standardized foundation for deploying containerized applications on AWS Lightsail with enterprise-grade features including:

- **Infrastructure as Code**: Built on CDKTF with Python for type-safe infrastructure definitions
- **Container Deployment**: Automated Docker image building, tagging, and deployment to AWS Lightsail
- **SSL/TLS Management**: Automated SSL certificate creation and domain attachment
- **Secret Management**: Integration with AWS Secrets Manager for secure configuration
- **Architecture Flags**: Configurable deployment options for different environments
- **Post-Deployment Automation**: Customizable scripts for additional setup tasks

## 🚀 Features

### Core Infrastructure
- **Base Class Architecture**: Extensible `AWSArchitectureBase` class for common AWS patterns
- **Provider Management**: Automatic setup of AWS, Random, and Null Terraform providers
- **S3 Backend**: Automated S3 bucket creation and Terraform state management
- **Resource Registry**: Centralized resource tracking and management

### Container Deployment
- **Lightsail Integration**: Specialized `BBAWSLightsailMiniV1aDeploy` class for container services
- **Docker Automation**: Build, tag, and push workflows with caching support
- **Environment Management**: Configurable environment variables and secrets injection
- **Health Checks**: Automated health check configuration for container endpoints

### Domain & SSL Management
- **Custom Domains**: `LightSailDomainAttachWrapper` for domain attachment automation
- **SSL Certificates**: Automatic certificate creation and validation
- **DNS Integration**: Route53 integration for domain management
- **Fallback Guidance**: Manual command generation for troubleshooting

### Configuration Management
- **Architecture Flags**: Feature toggles for optional components
  - `SKIP_DATABASE`: Skip database creation
  - `SKIP_DOMAIN`: Skip domain and DNS configuration
  - `SKIP_SSL_CERT`: Skip SSL certificate creation
  - `SKIP_DEFAULT_POST_APPLY_SCRIPTS`: Skip default post-apply scripts
- **Environment Profiles**: Support for multiple AWS profiles and regions
- **Archetype Integration**: Integration with Buzzerboy archetype patterns

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- AWS CLI configured with appropriate credentials
- Docker (for container deployments)
- Node.js (for CDKTF)

### Install from Package Registry
```bash
# Install from Buzzerboy's private registry
pip install AWSArchitectureBase
```

### Development Installation
```bash
# Clone the repository
git clone <repository-url>
cd AWSArchitectureBase

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## 🔧 Quick Start

### Basic Container Service Deployment

```python
from AWSArchitectureBase.AWSArchitectureBaseStack import AWSArchitectureBase, ArchitectureFlags
from cdktf import App

app = App()

# Get archetype configuration
archetype = AWSArchitectureBase.get_archetype(
    product='myapp', 
    app='api',  
    tier='dev', 
    organization='myorg', 
    region='ca-central-1'
)

# Configuration flags
ArchitectureFlags = AWSArchitectureBase.get_architecture_flags()
flags = [
    ArchitectureFlags.SKIP_DATABASE.value,
    ArchitectureFlags.SKIP_SSL_CERT.value,
]

# Custom domains
domains = [
    f"{archetype.get_tier()}.api.example.com"
]

# Post-deployment scripts
post_apply_scripts = [
    "echo '📋 Deployment verification complete'",
    "echo '📋 Container service is ready'",
]

# Create the stack
stack = AWSArchitectureBase(
    app, 
    "my-lightsail-service",
    project_name=archetype.get_project_name(),
    environment=archetype.get_tier(),
    region=archetype.get_region(),
    secret_name=archetype.get_secret_name(),
    profile="default",
    flags=flags,
    domains=domains,
    state_bucket_name="my-tfstate-bucket",
    postApplyScripts=post_apply_scripts,
)

archetype.set_stack(stack)
app.synth()
```

### Container Deployment Automation

```python
from AWSArchitectureBase.AWSArchitectureBaseStack import AWSArchitectureDeploy

# Initialize deployment helper
deployer = AWSArchitectureDeploy(
    product='myapp',
    app='api',
    tier='dev',
    organization='myorg',
    region='ca-central-1',
    debug=True,
    version='1.0.0'
)

# Execute deployment pipeline
deployer.app_deploy()
```

### Domain Attachment with SSL

```python
from AWSArchitectureBase.AWSArchitectureBaseStack.LightSailDomainAttachWrapper import LightSailDomainAttachWrapper

# Initialize domain wrapper
domain_wrapper = LightSailDomainAttachWrapper(
    domains=["api.example.com", "app.example.com"],
    region="ca-central-1",
    container_service_name="my-app-service"
)

# Get attachment script
attach_script = domain_wrapper.get_attach_command()
print(attach_script)
```

## 🏛️ Architecture

### Project Structure
```
AWSArchitectureBase/
├── AWSArchitectureBaseStack/
│   ├── __init__.py
│   ├── AWSArchitectureBase.py          # Main base class
│   ├── ArchitectureFlags.py            # Configuration flags
│   ├── BBAWSLightsailMiniV1aDeploy.py  # Container deployment
│   └── LightSailDomainAttachWrapper.py # Domain management
├── pyproject.toml                      # Package configuration
├── requirements.txt                    # Python dependencies
└── Makefile                           # Build automation
```

### Key Components

#### AWSArchitectureBase Class
The core infrastructure class providing:
- Terraform provider initialization
- S3 backend configuration
- Resource registry management
- Architecture flag handling
- Utility methods for AWS naming conventions

#### BBAWSLightsailMiniV1aDeploy Class
Container deployment automation including:
- Docker image building and caching
- AWS Lightsail container service management
- Secret management integration
- Environment variable configuration
- Deployment pipeline orchestration

#### LightSailDomainAttachWrapper Class
Domain and SSL management featuring:
- SSL certificate creation and validation
- Custom domain attachment automation
- DNS integration support
- Manual fallback command generation

## 🔐 Configuration

### Environment Variables
```bash
export AWS_PROFILE=your-profile
export AWS_REGION=ca-central-1
export VERBOSE=true  # Enable verbose logging
```

### Architecture Flags
Control deployment features using architecture flags:

```python
from AWSArchitectureBase.AWSArchitectureBaseStack import ArchitectureFlags

flags = [
    ArchitectureFlags.SKIP_DATABASE.value,      # Skip RDS/database setup
    ArchitectureFlags.SKIP_SSL_CERT.value,      # Skip SSL certificate creation
    ArchitectureFlags.SKIP_DOMAIN.value,        # Skip domain configuration
    ArchitectureFlags.SKIP_DEFAULT_POST_APPLY_SCRIPTS.value,  # Skip default scripts
]
```

### AWS Secrets Manager
Store application secrets in AWS Secrets Manager:

```json
{
  "database_url": "postgresql://...",
  "api_keys": "...",
  "jwt_secret": "..."
}
```

Secret path format: `{organization}/{tier}/{product}-{app}-{tier}`

## 🚀 Deployment

### Using CDKTF
```bash
# Initialize and plan
cdktf init
cdktf plan

# Deploy infrastructure
cdktf deploy

# Destroy when needed
cdktf destroy
```

### Using Make (for package development)
```bash
# Clean and build
make clean build

# Publish to registry
make publish TYPE=patch  # or minor, major
```

## 📋 Examples

### Multi-Environment Deployment
```python
# Development environment
dev_stack = AWSArchitectureBase(
    app, "my-app-dev",
    environment="dev",
    region="ca-central-1",
    flags=[ArchitectureFlags.SKIP_SSL_CERT.value]
)

# Production environment
prod_stack = AWSArchitectureBase(
    app, "my-app-prod",
    environment="prod",
    region="us-east-1",
    flags=[]  # All features enabled
)
```

### Custom Post-Deploy Scripts
```python
post_apply_scripts = [
    "echo '📋 Running database migrations'",
    "python manage.py migrate",
    "echo '📋 Warming up application cache'",
    "curl -X POST https://api.example.com/warmup",
    "echo '📋 Notifying monitoring systems'",
    "curl -X POST https://monitoring.example.com/deploy-complete"
]
```

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=AWSArchitectureBase
```

### Integration Tests
```bash
# Test infrastructure deployment
cdktf plan --var-file=test.tfvars

# Test container deployment
python test_deployment.py
```

## 🔧 Development

### Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd AWSArchitectureBase

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pre-commit install
```

### Building and Publishing
```bash
# Version bump and build
make publish TYPE=patch

# Manual build
python -m build
twine upload dist/*
```

## 📖 API Reference

### AWSArchitectureBase Methods
- `get_architecture_flags()`: Get available configuration flags
- `get_archetype()`: Get archetype configuration
- `has_flag()`: Check if architecture flag is set
- `get_extra_secret_env()`: Parse extra secrets from environment
- `execute_post_apply_scripts()`: Run post-deployment scripts

### Utils Module
- `properize_string(string)`: Convert string to valid AWS resource name
- `clean_hyphens(string)`: Convert string for database naming
- `parse_secrets_from_env(env_var_name)`: Parse JSON secrets from environment

### BBAWSLightsailMiniV1aDeploy Methods
- `app_deploy()`: Execute complete deployment pipeline
- `build_docker_image()`: Build Docker image for deployment
- `push_docker_image()`: Push image to Lightsail registry
- `deploy_docker_image()`: Deploy container service
- `get_container_fqdn()`: Get container service URL

### LightSailDomainAttachWrapper Methods
- `get_attach_command()`: Generate domain attachment script
- `get_certificate_creation_command()`: Generate SSL cert creation command
- `get_domain_attachment_command()`: Generate domain attachment command

## 🐛 Troubleshooting

### Common Issues

#### SSL Certificate Validation Timeout
```bash
# Check certificate status
aws lightsail get-certificates --region ca-central-1 --include-certificate-details

# Manual domain attachment after validation
aws lightsail update-container-service \
  --service-name my-service \
  --region ca-central-1 \
  --public-domain-names '{"example.com": ["example.com"]}'
```

#### Docker Build Failures
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t my-service .
```

#### Terraform State Issues
```bash
# Refresh state
cdktf refresh

# Import existing resources
cdktf import aws_lightsail_container_service.example my-service
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Create a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints for all public methods
- Include docstrings for classes and methods
- Write unit tests for new functionality
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About Buzzerboy

AWS Architecture Base is developed and maintained by Buzzerboy Inc. For enterprise support and consulting services, contact us at info@buzzerboy.com.

## 🔗 Related Projects

- [BuzzerboyArchetype](https://dev.azure.com/buzzerboyinc/buzzerboy) - Enterprise archetype patterns
- [CDKTF Documentation](https://developer.hashicorp.com/terraform/cdktf) - Cloud Development Kit for Terraform
- [AWS Lightsail](https://aws.amazon.com/lightsail/) - AWS Lightsail container services

---

**Made with ❤️ by the Buzzerboy Team**