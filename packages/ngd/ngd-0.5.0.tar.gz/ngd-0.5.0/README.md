# NGD - Programming Tutorials Package

A comprehensive Python package containing 25 essential programming tutorials covering Git, Flask, Docker, Kubernetes, Jenkins, Android development, and more.

## Installation

You can install the package using pip:

```bash
pip install ngd
```

Or install from source:

```bash
git clone https://github.com/yourusername/ngd.git
cd ngd
pip install -e .
```

## Available Programs

The package includes 25 comprehensive programming tutorials:

### 1. **Git Basics and Local Repository Setup**
- Initialize Git repositories
- Basic Git commands (add, commit, status, log)
- Configure Git user settings
- View commit history and differences

### 2. **Git Remote Repository Management**
- Push local repositories to remote (GitHub)
- Sync local and remote repositories
- Clone public repositories
- Branching and merging operations

### 3. **Flask Web Development (Without Docker)**
- Create Flask applications
- Set up project structure
- Create templates and routes
- Run Flask applications locally

### 4. **Flask with Docker**
- Create Dockerfiles for Flask apps
- Build and run Docker images
- Containerize web applications
- Port mapping and container management

### 5. **Jenkins CI/CD (CIE 1)**
- Set up Jenkins server
- Create freestyle projects
- Configure SCM (GitHub integration)
- Set up build triggers and steps

### 6. **Prometheus Monitoring**
- Install and configure Prometheus
- Set up monitoring targets
- Use PromQL queries
- Basic monitoring setup

### 7. **Grafana Dashboard**
- Install and run Grafana
- Connect to Prometheus data source
- Create dashboards and visualizations
- Monitor system metrics

### 8. **Docker Hub Image Management**
- Create Docker Hub accounts
- Tag and rename Docker images
- Push images to Docker Hub
- Manage Docker Hub repositories

### 9. **Jenkins Pipeline (CIE 2)**
- Create Jenkins pipelines
- Set up build dependencies
- Configure pipeline views
- Advanced Jenkins automation

### 10. **Docker Networking**
- Understand Docker network types
- Create custom bridge networks
- Connect containers across networks
- Network troubleshooting

### 11. **Kubernetes Basics**
- Create and manage pods
- Expose services with NodePort
- Create deployments with replicas
- Scale applications

### 12. **Android Alert Dialog**
- Create Android applications
- Implement alert dialogs
- Handle user interactions
- Android UI development

### 13. **Android Progress Bar**
- Implement progress bars
- Handle background threads
- Update UI from background tasks
- Android threading concepts

### 14. **Android SeekBar**
- Create seekable progress bars
- Handle user input events
- Real-time UI updates
- Android input handling

### 15. **Android Canvas Drawing**
- Draw shapes on Android canvas
- Create custom graphics
- Handle bitmap operations
- Android graphics programming

### 16. **Android Animations**
- Implement various animations
- Create animation resources
- Apply animations to views
- Android animation framework

### 17. **Android Options Menu**
- Create options menus
- Handle menu selections
- Implement menu callbacks
- Android menu system

### 18. **Android Context Menu**
- Implement context menus
- Register for context menus
- Handle long-press events
- Android context menu system

### 19. **Android Popup Menu**
- Create popup menus
- Position popup menus
- Handle menu item clicks
- Android popup menu implementation

### 20. **Android Fragments**
- Create and manage fragments
- Fragment transactions
- Fragment lifecycle
- Android fragment architecture

### 21. **Android SQLite Database**
- Create SQLite databases
- Implement CRUD operations
- Handle database queries
- Android data persistence

### 22. **Android Shared Preferences (Basic)**
- Store simple data
- Save and load preferences
- Clear stored data
- Android data storage

### 23. **Android Shared Preferences (Advanced)**
- Auto-save form data
- Persistent data storage
- Handle application lifecycle
- Advanced Android preferences

### 24. **Android Explicit and Implicit Intents**
- Navigate between activities
- Launch external applications
- Pass data between activities
- Android intent system

### 25. **Android Intent Data Passing**
- Pass complex data between activities
- Handle intent extras
- Receive and process data
- Android activity communication

## Usage

To view the code for any program, use the `print_program` function:

```python
from ngd.programs import print_program

# Print program 1 (Git Basics)
print_program(1)

# Print program 3 (Flask without Docker)
print_program(3)

# Print program 11 (Kubernetes)
print_program(11)

# Print program 21 (Android Database)
print_program(21)

# And so on for programs 1-25...
```

## Requirements

The package requires the following dependencies:
- **flask** >= 2.0.0 - Web framework for Flask tutorials
- **requests** >= 2.25.0 - HTTP library for API calls

## Features

- **Comprehensive Coverage**: From Git basics to advanced Android development
- **Educational**: Step-by-step tutorials suitable for learning
- **Practical**: Real-world applications and examples
- **Multi-platform**: Covers web development, mobile development, and DevOps
- **Extensible**: Easy to modify and extend for specific needs
- **Cross-platform**: Works on Windows, macOS, and Linux

## Examples

### Git Operations
```python
from ngd.programs import print_program
print_program(1)  # Git basics
print_program(2)  # Git remote operations
```

### Web Development
```python
from ngd.programs import print_program
print_program(3)  # Flask without Docker
print_program(4)  # Flask with Docker
```

### DevOps Tools
```python
from ngd.programs import print_program
print_program(5)  # Jenkins CI/CD
print_program(10) # Docker networking
print_program(11) # Kubernetes
```

### Android Development
```python
from ngd.programs import print_program
print_program(12) # Alert Dialog
print_program(21) # Database operations
print_program(25) # Intent data passing
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this package in your research or teaching, please cite:

```
NGD Programming Tutorials Package (2024). A comprehensive collection of programming tutorials.
Available at: https://pypi.org/project/ngd/
``` 